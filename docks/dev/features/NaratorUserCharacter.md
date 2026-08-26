# Feature: Narrator User Character

**Status**: Draft
**Date**: 2026-08-26

## Summary
Today every scene requires the user to control a specific character (`user_character_id`). In practice, users already switch which character they play between scenes within the same story (e.g. playing Ben in scene 1, then Mark in scene 2) to shape the story from different angles. This feature closes a gap in that pattern: sometimes the user wants to shape a scene without occupying any character's perspective at all — observing or directing NPC-only interactions (e.g. Ben sleeps while Mark and Bob interact). We introduce "Narrator" as a per-scene alternative to picking a character: the user still sends messages and drives the scene, but is not tied to any character identity, and the story engine adjusts its system prompt accordingly.

## Value
- Closes the gap where users want to influence a scene's direction without roleplaying a specific character.
- Extends the existing "switch user character between scenes" pattern rather than introducing a new mechanic.
- Success: users can create/pick a scene with no user character selected, play it normally (send/edit/delete messages, finish scene), and the assistant's behavior correctly reflects that no character represents the user.

## Scope
### In scope for first iteration
- `user_character_id` becomes optional (nullable) at the scene level, for `"scene"` type stories only.
- Frontend scene creation picker: a constant "Narrator" option alongside real characters; selecting it clears `user_character_id` to `null`.
- Story engine system prompt: a distinct template variant used when there is no user character, replacing the "User's Character Profile" section and the protagonist-agency directive with narrator-appropriate wording.
- Scene summarization: no changes — it already only depends on `context` and `messages`.

### Out of scope / future
- Choice-driven stories (`type: "choice_driven"`) — `user_character_id` remains required there; not addressed by this feature.
- Mid-scene switching between narrator and character (role is fixed for the lifetime of a scene, same as character choice today).
- Any UI indication/badge distinguishing narrator-authored messages from character-authored ones beyond the existing `role: "user"` message field.
- Changing `PATCH`-style scene metadata updates (still post-MVP/out of scope generally).

## User Flow
1. User opens "New Scene" for a story.
2. In the "User character" picker, a fixed "Narrator" option appears above/alongside the story's characters.
3. If the user selects "Narrator": `user_character_id` is unset; all other characters remain available to add to `character_ids` (no exclusion needed since there's no user character to exclude).
4. If the user selects a real character: existing behavior is unchanged (that character is excluded from the NPC checklist).
5. Scene plays exactly as before — user sends messages, gets assistant replies, can edit/delete messages, and finish the scene.
6. Assistant behavior differs only in how it interprets the user's messages: as narrator direction/turning points rather than one character's actions/dialogue.

## API Changes
### POST /api/stories/{story_id}/scenes (create scene)
- `user_character_id`: now optional (`str | None`, default `null`), previously required `str`.
- Validator "user_character_id must not appear in character_ids" only runs when `user_character_id` is not null.

### GET /api/stories/{story_id}/scenes/{scene_id} (scene detail)
- No shape change required beyond what already exists; `user_character_id` is not currently exposed in `SceneDetail` response (confirmed not present today), so no response contract changes needed for read.

No other endpoints change shape. Play/edit/delete/finish endpoints are unaffected — they operate on messages, not on the user_character concept directly.

## Data Changes
### Scene Metadata (`meta.yaml`)
- `user_character_id`: becomes optional field, `null` allowed.
- Constraint update: "user_character_id must have a matching character file" only enforced when the field is not null.
- Applies only to `"scene"` type stories; `"choice_driven"` story metadata keeps `user_character_id` required (unchanged).

No new files, no new top-level YAML structures. This is a nullability relaxation of an existing field.

## Backend Changes
- `SceneMetadata` (`app/models/domain.py`): `user_character_id: str | None`.
- `SceneMetadataYaml` (`app/models/storage.py`): same nullability change, mirrored.
- `CreateSceneRequest` (`app/models/api.py`): `user_character_id: str | None = None`; `user_character_not_in_character_ids` validator short-circuits when `user_character_id is None`.
- `scene_creation_service.py`: pass through optional `user_character_id`; no character-file lookup/validation when null.
- `scene_repository.py`: relax the "must have matching character file" check to skip when null.
- `SceneContext` (`app/llm/models.py`): `user_character: CharacterCard | None`.
- `scene_play_service.py`: when `metadata.user_character_id` is null, skip `get_character` lookup and pass `user_character=None` into `SceneContext`.
- `PromptBuilder` (`app/llm/prompt_builder.py`): branch on `context.user_character is None` to select between `scene_system.j2` (existing, character mode) and a new `scene_system_narrator.j2` template.
- New template `app/llm/templates/scene_system_narrator.j2`: omits "User's Character Profile" section; replaces Core Directive #1 ("user controls the protagonist... react only to what they provide") with narrator-appropriate direction (user is not a character, but is directing pacing/turning points; assistant still fully controls all NPCs and world reactions based on the narrator's input).
- `scene_summarize_service.py`: no changes.

## Frontend Changes
- `NewScenePage.jsx`:
  - Add a constant "Narrator" option rendered in the "User character" `<select>`, distinct from the existing "— select —" placeholder (need a real selectable value, not just an empty placeholder, since empty currently also represents "nothing chosen yet" for validation).
  - `validate()`: `user_character_id` is no longer strictly required — only invalid if truly unset (no explicit narrator/character choice made yet); narrator counts as a valid, deliberate selection.
  - `handleUserCharacterChange`: when narrator is selected, `sceneCharacterIds` filtering by `characterId` is skipped (no id to exclude); all characters remain eligible NPCs.
  - Submit payload: `user_character_id` becomes `null` when narrator is selected instead of a character id string.

## Open Questions
- Exact sentinel/representation for "Narrator selected but not yet decided" vs "nothing selected" in the frontend picker, to keep validation meaningful (need a value distinct from empty-string placeholder). - ** Narator should be a real selectable value, not just an empty placeholder, since empty currently also represents "nothing chosen yet" for validation.**
- Exact wording of the narrator system prompt directive — should be refined/polished independently of this design doc, per prompt template being kept separate for easier iteration.
- Whether existing scenes created before this change (all with non-null `user_character_id`) need any migration — likely not, since this is purely an added nullable case.

## Risks
- Prompt quality risk: narrator-mode system prompt needs real testing/tuning to ensure the assistant doesn't default to inventing a user-controlled character anyway.
- Two templates (`scene_system.j2` and `scene_system_narrator.j2`) must be kept in sync for shared sections (formatting rules, execution protocol) — drift between them over time is a maintenance risk.
- Validation gap: need to ensure `character_ids` still can't be empty/inconsistent in narrator mode (e.g. a narrator scene with zero NPCs would be a degenerate case worth guarding against, though not necessarily blocking).
