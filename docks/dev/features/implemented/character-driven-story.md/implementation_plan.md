# Character-Driven Story: Implementation Plan

**Status**: Draft (main steps only)

Each step is meant to be a shippable slice. Backend steps come first because the frontend depends on the API contract in `API.md`.

## Backend

1. **Foundation: types and storage models**

   `file_paths.py` already matches the storage layout, and story list and detail pick up the new type through the shared `StoryType` alias, so neither needs changes.

   - **1a. Story type and usage tracking**
     - Add `character_driven` to `StoryType`, and `character_action`, `narration` and `character_memory_update` to `LLMUsageOperation`.
     - Add nullable `character_id` to `LLMUsage` and `LLMUsageYaml`, and to the `_to_domain` / `_to_storage` mapping in `LLMUsageRepository`. Without the mapping the field is silently dropped.
     - Add a `character_id` keyword argument to `record_usage`.
     - Update the usage validators in `domain.py` and `storage.py`. Handle the new operations before the `story_generation` catch-all branch.
       - `character_action` and `narration` require `scene_id` and `message_id`, and forbid `step_id`.
       - `character_action` requires `character_id`. `narration` forbids it.
       - `character_memory_update` requires `scene_id` and `character_id`, and forbids `message_id` and `step_id`.
     - Add tests for the validators and the repository round trip.
   - **1b. Message storage models** (`storage.py` only)
     - Add `CharacterDrivenInputYaml`, `CharacterDrivenLLMDataYaml`, `CharacterDrivenMessageYaml` and `CharacterDrivenMessagesYaml`.
     - Decisions:
       - `llm_data` is required on every entry, including the opening item. For the opening item it stores the model IDs selected at scene creation (same approach as scene-driven stories). `narrator_model_id` is always required and `character_model_id` is nullable.
       - `input.author` is `str | None`. A null author means a player turn with no player character assigned.
       - Turn kind is derived from scene metadata. A turn is a player turn if `author is None` or `author == user_character_id`, and a character turn otherwise.
     - Domain and API item models are added in steps 2 and 4, where they are first used.

2. **Repository layer**

   Decisions:
   - Character-driven scenes get a separate `CharacterDrivenSceneRepository`. `SceneRepository` stays untouched and keeps serving scene-driven stories. The repository is chosen in service wiring, not by switching on story type inside one repository.
   - The new repository composes `SceneRepository` for metadata read and write, because `SceneMetadataYaml` is shared.
   - A null `user_character_id` is valid for character-driven scenes (the UI shows it as a `Narrator` option). The `NarratorModeNotSupportedError` check in `SceneRepository` and `SceneCreationService` stays scene-driven only and is not reused.

   - **2a. Domain models**
     - Add `CharacterDrivenInput(author, action, guidance)`, a two-field `CharacterDrivenLLMData` and `CharacterDrivenMessage`. The domain stays storage-shaped.
     - Add one helper that derives player versus character turn from scene metadata (step 1 decision). The API-level `actor` and `character_action` mapping belongs to the service in step 4.
   - **2b. `CharacterDrivenSceneRepository`**
     - Create a scene (metadata plus opening message), get messages, append a message, update narration, replace a message in place and delete the last message.
     - Validate authors against the scene: a null author is valid only when `user_character_id` is null, and an NPC author must be in `character_ids`.
     - Validate that all referenced character files exist.
   - **2c. Character memory append**
     - Add `CharacterRepository.append_memory(story_id, character_id, entries)`, skipping entries already present, and `set_memory(story_id, character_id, memory)` for rollback in step 7c.
     - The write re-dumps `CharacterYaml`, so unknown keys in a hand-written character file would be dropped. Preserve them or accept the loss explicitly.
     - The finish strategy is decided in step 7.

3. **LLM layer**

   Decisions:
   - The character agent's `INTERNAL / ACTION / SPEECH / TONE` output is not parsed. The raw response string is stored as `input.action` and passed to the narrator and the transcripts unchanged. No format validation is done, other than treating an empty response as an LLM error.
   - New templates live in `templates/character_driven/` to avoid clashing with the scene-driven `scene_system_narrator.j2`.
   - The summary and memory agents use the env-configured `SUMMARY_MODEL` (via `get_summary_model`), as scene-driven summarizing does. The draft endpoints take no model ID. Upgrading to the narrator's last-used model later needs no API change.
   - The narrator's `story_context` is the current scene's `context`. The creation form already pre-fills it with the previous scene's context plus its summary (as `NewScenePage` does), so no cross-scene reads are needed.

   - **3a. Plumbing**
     - Add the template subdirectory and per-call model factories, following `SceneLLMClientFactory`.
     - Services override `completion.model_id` with the registry model ID before recording usage, as `ScenePlayService` does.
   - **3b. Character agent**
     - Add the client and the context builder: profile from `features`, memories from the root-level `memory` field, and the concatenated scene narration.
     - `CharacterCard.to_prompt_text()` appends a `### Memory` section, which would duplicate the separate `accumulated_memories` prompt variable. Add a profile-only render that uses `features` alone.
   - **3c. Narrator**
     - Add the client and the user-message builder (scene so far plus the current turn), sent as one user message.
   - **3d. Memory agent**
     - Add the client, with JSON `items` output like the summary client, and the transcript builder.

4. **Scene creation and read**

   Decisions:
   - `GET /api/stories/{story_id}` gains a `type` field (additive), because it currently omits it. `StoryPage` is reused for character-driven stories and picks its scene link prefix from `story.type`.
   - No story-type guard is added to the existing `/scenes` endpoints or the new `/character-play` endpoints. Only the frontend calls the API and it routes by story type, so a wrong-type call is treated as a client bug, not a supported case.
   - Routers shape responses. The mapping from the storage-shaped domain message to the API item (`actor`, `input`, `character_action`) is a pure function in the new router module, using the 2a player-versus-character helper.
   - Request validation: non-empty strings for the guide, style, opening paragraph and each context item. Duplicate IDs in `character_ids` give `422`.
   - Add one `ModelRegistryService` helper that validates several model IDs at once. It has three new call sites (create, turn, replace), and it also covers the existing TODO in `SceneCreationService`.

   - **4a. Creation**
     - Add `POST .../character-play/scenes`, `CharacterDrivenSceneCreationService`, a new `character_play.py` router, the request model and the dependency wiring.
     - Validate participants, both model IDs and the "no other active scene" rule.
     - The opening item stores the creation-time model IDs in `llm_data`.
   - **4b. Read**
     - Add `GET .../character-play/scenes/{id}` and `CharacterDrivenSceneQueryService`, plus the response models. Nulls stay explicit (no `exclude_none`).
   - **4c. Story detail type**
     - Add `type` to `StoryDetail` and the stories router handler.
   - Add tests for each slice.

5. **Turn processing**

   Decisions:
   - Failure and retry is whole-turn. If the character call or the narration fails, nothing is persisted and the retry re-runs the whole request, so a retried character action may differ. This follows `API.md`; the other design docs were corrected to match.
   - Usage is recorded only after the item is persisted. Both calls of a successful turn are recorded then, with the registry model ID and the new `message_id`. The cost of failed chains is not tracked.
   - Item IDs use `max(id) + 1`, so the ID of a deleted last item can be reused after a delete. `data-storage.md` now says "not renumbered" instead of "not reused".
   - Request model: a discriminated union on `actor.type`.
     - A player request requires a non-empty `action` and rejects `guidance`.
     - A character request has optional `guidance`, where empty means none.
     - Both require both model IDs, and both are validated against the registry. A player turn stores `character_model_id: null` in `llm_data`.
   - A character that is not in the scene's `character_ids` gives `422`. A missing character file gives `404`.
   - The service catches `LLMError`, logs `stage=character_action` or `stage=narration`, and re-raises. The existing handler returns the generic `502`.
   - The narrator's `actor_name` is the player character's name, or `Player` when `user_character_id` is null.
   - No locking. The UI disables the composer during a turn, and the scene-driven path has the same exposure.

   - **5a. Player turn**
     - Add `POST .../turns` with `CharacterDrivenSceneTurnService`, which handles a player turn (narrator call only) and the request validation.
   - **5b. Character turn**
     - Add the character-agent call followed by the narrator call, and save one item with the generated action stored as `input.action`.
   - Record usage after the save, and add tests for the failure paths (nothing persisted, no usage records).
   - Keep generation separate from persistence in `CharacterDrivenSceneTurnService`: a method takes the history items, the request and the models, and returns the new item content. Step 6b reuses it with the history excluding the replaced item.

6. **Correction operations**

   Decisions:
   - The opening item cannot be deleted (`409 opening_item_not_deletable`). A scene therefore always has its opening item, the narrator history is never empty, and the creation-time model defaults can always be derived. A bad opening is fixed through edit. This resolves the open API decision and is listed in `API.md`.
   - Any item, including the opening one, can be edited, and only its narration changes. Narration must be 1-4000 characters, matching `UpdateMessageRequest`. The same 4000 limit applies to the opening paragraph at creation.
   - New `409` domain errors: `not_last_item`, `not_replaceable` and `opening_item_not_deletable`.
   - Check order: story and scene `404`, then `scene_finished`, then item `404`, then `not_last_item`, then `not_replaceable`.

   - **6a. Edit and delete**
     - Add `PUT` and `DELETE .../items/{id}` and an item service, mirroring `SceneMessageService`.
     - Repository operations: update narration, and delete the last item (both planned in 2b).
   - **6b. Replace the last turn**
     - Add `POST .../turns/{item_id}/replace` on the turn service, reusing the step 5 generation with the replaced item excluded from the history.
     - On success, overwrite the whole item in place (input, narration and `llm_data`) with the same ID. On failure the old item stays untouched.
     - Record usage after the save with the same `message_id`. The superseded item's earlier usage rows stay, since they were real calls.
   - Add tests for each slice.

7. **Finish flow**

   Decisions:
   - Finish consistency: validate everything before any write, then write each character's memory first and the scene `meta.yaml` last. The `finished` flag is the commit marker.
     - Before writing, snapshot each character's memory list. If any write raises, restore the snapshots and re-raise, so an exception leaves persisted data unchanged.
     - A hard crash mid-finish leaves the scene unfinished with some memories appended. Retry is safe, because `append_memory` skips entries already present.
     - No write-ahead journal. `API.md` states this exact guarantee.
   - Summary and memory drafts use `SUMMARY_MODEL` (step 3 decision), so the open API decision about draft model IDs is resolved.
   - Participants for memory purposes are `character_ids` plus the player character when `user_character_id` is set.

   - **7a. Summary draft**
     - Add `GET .../summary/draft`, reusing `SummarizeLLMClient`.
     - `previous_summary` is the scene's `context` (last 50 items), as in scene-driven. The transcript is the narrations joined by blank lines.
     - Record `scene_summary` usage, and return `Cache-Control: no-store` (new to this codebase).
   - **7b. Memory draft**
     - Add `GET .../characters/{character_id}/memory/draft` with the memory agent client and the transcript builder (3d).
     - Each transcript entry has the actor's name (`Player` for a null author), the raw action or character output, and the narration.
     - A character not in the scene gives `409 character_not_in_scene`, and a missing file gives `404`.
     - Record `character_memory_update` usage with `character_id`.
   - **7c. Finish**
     - Add `POST .../finish` with a service that composes `SceneRepository` metadata and `CharacterRepository`.
     - Request: a non-empty summary list (max 100 items, non-empty strings). `character_memory_updates` must have exactly the participant keys, each a list of non-empty strings, and empty lists are allowed.
     - The response echoes the saved summary and memory updates.
     - Tests inject a write failure on the Nth file and assert that nothing changed.

## Frontend

8. **Foundation and routing**

   Decisions:
   - `StoriesPage` needs no change. It sends only `choice_driven` stories to `/play`, so character-driven stories already land on `StoryPage`.
   - `StoryPage` is reused and branches on `story.type` for its scene links and the create-scene link (needs the `type` field from step 4c).
   - Routes: `/stories/:storyId/character-scenes/new` and `/stories/:storyId/character-scenes/:sceneId`.
   - `NewScenePage` already has the `Narrator` pseudo-option (`__narrator__` maps to `null`). "Required" in `ui-ux.md` therefore means a Narrator or character selection is required.
   - `apiFetch` is copy-pasted in each API module. `character_play.js` follows that pattern, and extracting a shared client is out of scope.
   - `NewScenePage` is migrated onto the extracted components in the same step (refactor only). The existing `NewScenePage.test.jsx` must pass unchanged.

   - **8a. API module**
     - Add `api/character_play.js` covering all character-play endpoints, with fetch-mock tests.
   - **8b. Routing and `StoryPage`**
     - Add the routes, make `StoryPage` branch on `story.type`, and give `StoryList` a `Character` label.
   - **8c. Shared components**
     - Extract `ModelSelect`, `CharacterSelect` (single, with an optional Narrator option) and `CharacterCheckboxList`.
     - Move the player/NPC mutual-exclusion rule into one pure helper.
     - Add an optional `modelLabel` prop to `SceneHeader` (default `Model`), so the character-driven page can show `LLM`.
     - Migrate `NewScenePage` onto these components.

9. **Scene creation page**

   Decisions:
   - A new `NewCharacterScenePage` is added, not a parametrized `NewScenePage`. The two forms differ in sections, payload, previous-scene response shape, prefill and navigation. The new page reuses the `new-scene-page__*` CSS classes, `BulletTextarea` and the 8c components.
   - The default models come from the previous finished scene's items. The narrator model is the latest item's `narrator_model_id`, and the character model is the latest non-null `character_model_id`. If the derived ID is not in the registry, fall back to the registry default, because the endpoint rejects unknown IDs with `422`.
   - Prefill from the previous finished scene: context (previous context plus its summary), writing style, and the opening paragraph from the last narration (editable). The general scene guide is not prefilled, as in scene-driven.
   - Client validation: a Narrator or character selection, at least one context bullet, and a non-empty (after trimming) guide, style and opening paragraph. The opening paragraph is at most 4000 characters. Server errors, including `409 active_scene_exists`, show as the submit error.

   - **9a. Pure helpers**
     - `deriveModelDefaults(items, registry)` with the registry fallback. Step 10 reuses it for the play page's initial model selections.
     - A helper that builds the prefill values from the previous finished scene.
     - Both are unit tested.
   - **9b. Page**
     - Add `NewCharacterScenePage` with the Participants, Starting situation, Narrative direction and Agents sections, and wire the route from 8b.
     - Load the story, characters and models in parallel, fetch the last finished scene when one exists, and submit the `API.md` payload. Navigate to the new scene's route on success.
     - Add RTL tests and the factories for a character scene and a scene item.

10. **Scene play page**

    Decisions:
    - New components, not reuse of the message components: `CharacterScenePage`, `StoryTimeline`, `StoryItem` and `TurnComposer`. `MessageItem` is built around roles and bubbles, and its save path closes the editor on failure. Reused: `SceneHeader` (with `modelLabel="LLM"`), `ResponseTimeIndicator`, `RefreshIcon` for Retry and the markdown rendering.
    - The scene response returns only character IDs, so the page also loads the story's character list for the Actor dropdown names.
    - The composer is controlled. The page owns the actor, text and character model, and `TurnComposer` is presentational, so retry staging needs no imperative handle.
    - After every successful turn, clear the text and reset the Actor to `Player`. This avoids an accidental repeat character trigger, which costs two LLM calls, and matches the retry rule.
    - The opening item shows only Edit. It has no turn input (so no Retry) and cannot be deleted (step 6).
    - While retry mode is active, Edit, Delete and Retry are disabled on all paragraphs.
    - The turn is one synchronous request, so there is one progress label chosen by actor type: "Narrator is writing" for a player turn, "Character and narrator are working" for a character turn. This replaces the two-phase wording in `ui-ux.md`.
    - Scroll to the end only on load and when the item count changes, not on an edit or replace.
    - On no-hover devices the paragraph actions stay visible (`@media (hover: none)`).
    - A failed turn keeps the inputs, and Send acts as the retry (whole-turn retry, step 5).

    - **10a. Read-only page shell**
      - Load the scene, story, characters and models. Initial models come from `deriveModelDefaults` (9a).
      - Header via `SceneHeader` with the LLM label, plus `StoryTimeline`, `StoryItem`, and the finished and loading states.
    - **10b. Turn composer and send**
      - `TurnComposer` has the Actor select (`Player` plus the scene's characters), the Character LLM select, the textarea and a Send or Trigger button. The Character LLM select is inactive for `Player`.
      - A player turn needs non-empty text. A character turn allows empty guidance.
      - The `Finish` button stays at the bottom-left.
      - A successful turn appends the returned item and updates the model selections from its `llm_data`.
    - **10c. Paragraph actions**
      - Inline edit with Save and Cancel, a saving state, and on failure the text and an error beside the paragraph.
      - Delete on the last paragraph (not the opening item), with no confirmation.
    - **10d. Retry mode**
      - Retry stages the last item's actor and text (`input.action` for a player item, `input.guidance ?? ''` for a character item) and its models from `llm_data`. A null `character_model_id` keeps the current character model.
      - Stash the draft (text, actor, models) on entering retry and restore it on cancel. If there was no draft, reset to `Player` with an empty input.
      - The submit button reads `Replace last paragraph`, with a `Cancel retry` action. A successful replace overwrites the item in place and resets the composer. A failure keeps retry mode and the inputs.
    - Add component and page tests for each slice.

11. **Finish modal**

    Decisions:
    - A new `CharacterFinishModal` is added. The scene-driven `FinishModal` stays as is.
    - The modal calls `onSubmit` itself, catches errors and shows them inline, and stays open with edits intact. On success the page navigates to the story page.
    - Tab order is Summary, then the player character (if any), then the NPCs. Names come from the character list the play page already loads.
    - `Generate all` generates only tabs that are empty and never generated, or that failed. Tabs that are done, generating or non-empty are skipped. `Regenerate this` overwrites the selected tab explicitly. This also covers "retry only failed outputs".
    - Late results from generation calls that finish after the modal closes are discarded. Cancel is always enabled.
    - `Finish scene` is disabled while any tab is generating. The summary needs 1-100 non-empty items.
    - Soft confirmation for unresolved memory tabs. A memory tab is resolved when it was generated successfully (even if the user then cleared it) or contains text. If any are unresolved, the first click on `Finish scene` shows an inline warning, "No memory update was generated or entered for: X, Y. Select Finish scene again to confirm." The second click proceeds. Generating or editing anything resets the warning.
    - New component styles use CSS classes and tokens (not the inline styles of `FinishModal`), and reuse `.modal-overlay` and `.modal-panel`.

    - **11a. Draft state logic**
      - A hook or reducer holds the per-tab items and status (`idle`, `generating`, `done`, `error`).
      - It implements the `Generate all` rule, per-tab regenerate and the stale-result guard.
      - It computes the unresolved tabs and builds the finish payload.
      - It is unit tested.
    - **11b. `CharacterFinishModal`**
      - Tablist with a status badge per tab, a single visible editor, and the Generate all, Regenerate this, Cancel and Finish scene buttons.
      - Per-tab progress and error text, summary validation, the soft confirmation, inline submit errors, and tab roles with `aria-selected`.
    - **11c. Wiring**
      - Connect the `Finish` button on `CharacterScenePage` to the modal.
      - Add the draft and finish calls to `api/character_play.js` if 8a doesn't already have them.
      - Add a page test.

## Cross-cutting

12. **Hardening and docs**
    - Add functional and API tests across the full flow.
    - Do a manual run with a hand-made story folder.
    - Update the project docs: `requirements.md`, `endpoints.md`, `data_storage_structure.md` and `progect_structure.md`.
    - The feature design docs (`API.md`, `data-storage.md`, `Algorithms.md`, `ui-ux.md`, `UX-play-flow.md`, `llm_agents.md`) were already corrected to match this plan's decisions, so no further design-doc edits are planned. If an implementation detail changes a decision, update both this plan and the affected design doc.
    - After implementation, merge the character-driven behavior into the project docs listed above, which describe the current implementation.
