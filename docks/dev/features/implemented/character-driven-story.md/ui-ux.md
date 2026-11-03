# Scene Creation Page

The character-driven scene creation page follows the existing scene-driven story creation approach. The page does not include a story navigation header because stories do not have a dedicated story page yet.

## Schematic

```text
┌──────────────────────────────────────────────────────────────┐
│ New Character-Driven Scene                                  │
├──────────────────────────────────────────────────────────────┤
│ PARTICIPANTS                                                  │
│                                                              │
│ Player                                                       │
│ [ Select player character                              ▼ ]  │
│                                                              │
│ Characters                                                   │
│ [ ] Captain Mora                                             │
│ [ ] Harbor Guard                                             │
│ [ ] Navigator                                                │
│                                                              │
├──────────────────────────────────────────────────────────────┤
│ STARTING SITUATION                                            │
│                                                              │
│ Context                                                      │
│ ┌──────────────────────────────────────────────────────────┐ │
│ │ - The ship has reached the harbor.                       │ │
│ │ - The captain suspects a betrayal.                       │ │
│ └──────────────────────────────────────────────────────────┘ │
│                                                              │
│ Opening narrator paragraph                                   │
│ ┌──────────────────────────────────────────────────────────┐ │
│ │ A bell rings through the fog...                           │ │
│ └──────────────────────────────────────────────────────────┘ │
│                                                              │
├──────────────────────────────────────────────────────────────┤
│ NARRATIVE DIRECTION                                           │
│                                                              │
│ General scene direction                                      │
│ ┌──────────────────────────────────────────────────────────┐ │
│ │ Keep tension rising during the negotiation.               │ │
│ └──────────────────────────────────────────────────────────┘ │
│                                                              │
│ Writing style                                                │
│ ┌──────────────────────────────────────────────────────────┐ │
│ │ Cinematic, concise, sensory.                              │ │
│ └──────────────────────────────────────────────────────────┘ │
│                                                              │
├──────────────────────────────────────────────────────────────┤
│ AGENTS                                                        │
│                                                              │
│ Character agent model     [ Select model                ▼ ]  │
│ Narrator agent model     [ Select model                ▼ ]  │
│                                                              │
├──────────────────────────────────────────────────────────────┤
│                                      [Create scene]           │
└──────────────────────────────────────────────────────────────┘
```

## Widget behavior

### Player

- A single-choice dropdown.
- Contains every character available in the story.
- Also contains a `Narrator` option, which creates the scene without a player character (`user_character_id: null`).
- The selected character represents the character controlled by the player in this scene.
- A selection is required: either a character or `Narrator`.
- A character selected here cannot be selected in `Characters`.

### Characters

- A multi-select list of checkboxes.
- Contains every character available in the story.
- Selected characters are the NPCs that the player can trigger during the scene.
- The player character must be excluded from this selection.
- If a character is selected as `Player`, it is removed from the NPC selection or disabled there.
- If a character is selected as an NPC, it cannot remain selected as `Player`.
- An empty selection is allowed.

### Context

- A `BulletTextarea`, following the behavior in `frontend/src/pages/NewScenePage.jsx` and `frontend/src/components/BulletTextarea.jsx`.
- The value is represented as a list of context items, displayed one bullet per line.
- Pressing `Enter` creates the next bullet.
- Pasted lines are normalized into bullet items.
- Empty lines and empty items are ignored when the value is parsed.
- At least one non-empty context item is required.
- For a later scene, it is pre-filled with the previous scene's context followed by its summary.

### Opening narrator paragraph

- A text input field implemented as a multiline textarea.
- Contains the first narrator paragraph displayed when the scene starts.
- The field is required.
- The paragraph is stored as the initial scene item, with the selected agent models recorded in its `llm_data`.
- The field holds at most 4000 characters. For a later scene it is pre-filled with the previous scene's last narration and stays editable.

### General scene direction

- A text input field implemented as a multiline textarea.
- Describes the intended direction, events, or tension for the scene.
- The field is required.

### Writing style

- A text input field implemented as a multiline textarea.
- Describes how the narrator should write the scene.
- For a later scene, it is pre-filled with the previous scene's writing style.
- The field is required.

### Agents

- Contains one single-choice dropdown for the character agent model.
- Contains one single-choice dropdown for the narrator agent model.
- Each dropdown contains the configured language models available to the application.
- Each selector has one selected model when the page is ready.
- Both selectors are required. For a later scene each defaults to the model last used in the previous scene (the narrator from its latest turn, the character from its latest character turn), or to the registry default if that model is no longer configured.

### Create scene

- Validates all required fields before submitting.
- Shows field-level validation errors without leaving the page.
- Shows an operation-level error if scene creation fails.
- Disables the action while the scene is being created.
- Navigates to the newly created scene after a successful response.

## Implementation details

Use `frontend/src/pages/NewScenePage.jsx` as the behavioral reference and extract reusable pieces instead of duplicating its form logic.

- Reuse `BulletTextarea` for `Context`.
- Extract the player-character dropdown into a reusable character single-select component.
- Extract the NPC checkbox list into a reusable character multi-select component.
- Keep the mutual-exclusion rule in shared selection logic so both controls always produce a valid participant set.
- Extract the model dropdown into a reusable model single-select component. The character and narrator selectors should use the same component with different field values.
- Keep field labels, validation messages, loading state, submit state, and API error handling consistent with `NewScenePage.jsx`.
- Extend the scene creation request only as needed to carry the two agent model selections separately.

# Main Scene Play Page

The main scene page should preserve the existing scene-driven page structure from `frontend/src/pages/ScenePage.jsx`, while presenting the result as a readable growing story. The visible scene history contains narrator paragraphs only. Player actions, character guidance, and generated character actions are used for processing but are not displayed in the main story timeline.

## Schematic

```text
┌──────────────────────────────────────────────────────────────┐
│ Story title       Scene 1       Active       LLM [ Model ▼ ]│
├──────────────────────────────────────────────────────────────┤
│                                                              │
│ A bell rings through the fog.                               │
│                                                              │
│ ──────────────────────────────────────────────────────────── │
│                                                              │
│ The harbor master turns toward the approaching captain...   │
│                                                              │
│ ──────────────────────────────────────────────────────────── │
│                                                              │
│ A gloved hand settles on the guard's sword hilt.             │
│                                                              │
│                                      [edit] [delete] [retry] │
│                                                              │
├──────────────────────────────────────────────────────────────┤
│ [ Actor: Player ▼ ] [ Character LLM: Model ▼ ]              │
│ ┌──────────────────────────────────────────────────────────┐ │
│ │ Describe an action, reaction, or dialogue...              │ │
│ └──────────────────────────────────────────────────────────┘ │
│                                                              │
│ [Finish]                                       [Send]        │
└──────────────────────────────────────────────────────────────┘
```

## Header

- Keep the existing scene title, scene status, and story identity from `SceneHeader`.
- Narrator agent control - one `LLM` single-choice dropdown.
- The `LLM` dropdown controls the narrator LLM for the current turn.
- The selected narrator LLM can be changed before each turn.
- The header does not contain an Agent settings panel.
- Keep `Finish` out of the header. It belongs in the bottom-left of the composer area, like the existing scene-driven page.

## Main scene area

- Display only narrator-generated paragraphs.
- Render each paragraph as a story item in chronological order.
- Use tiny borders or separators between items rather than message bubbles or large cards.
- Keep the reading area focused on the narrative and allow it to scroll as the story grows.
- Do not show player actions, character guidance, generated character actions, agent metadata, or intermediate prompts in the default view.
- Preserve the underlying turn data so correction, deletion, regeneration, retries, and future detail views remain possible.

### Paragraph actions

- Paragraph actions are hidden by default.
- On hover, show icon buttons for `Edit` on each paragraph and `Delete` and `Retry` only on the last paragraph.
- Each icon button has an accessible label and tooltip.
- Every narrator paragraph can be edited independently.
- Clicking `Edit` replaces only that paragraph with an inline text input, styled to match the paragraph's typography, width, and spacing.
- The editing state includes `Save` and `Cancel` buttons.
- `Save` applies the edited text to that same paragraph in its existing position in the story.
- `Cancel` exits editing and restores the original paragraph text without saving changes.
- While a save is in progress, disable the text input and both buttons and show a saving state on `Save`.
- If saving fails, keep the edit field and its unsaved text visible, show an error beside the paragraph, and allow the user to retry or cancel.
- Editing changes only the displayed narrator paragraph; it does not expose or edit the hidden player action, character guidance, or generated character action.
- `Delete` is available only for the last narrator paragraph, and never for the opening paragraph.
- Clicking `Delete` immediately removes the last paragraph from the scene and updates the visible story; no confirmation step is shown.
- `Retry` is available only for the last narrator paragraph, and never for the opening paragraph, which has no turn input to restore.
- Clicking `Retry` switches the existing composer into retry mode; it does not replace the composer widget or immediately call an LLM.
- In retry mode, show a clear `Retrying last paragraph` state, restore the text used to initiate that paragraph in the main input field, and return focus to the composer.
- Change the submit button label to `Replace last paragraph` while retry mode is active.
- Show a `Cancel retry` action in the composer.
- When entering retry mode, preserve any unsent composer text and actor/model selections so they can be restored if the retry is canceled.
- Clicking `Cancel retry` discards the staged retry and returns the composer to its normal state. Restore the pre-retry text and actor/model selections if there was a pre-existing draft; otherwise show an empty input with `Player` selected.
- The actor used for the last turn is selected initially. The player can edit the restored text, change either model, switch to another available actor, or clear the text before submitting.
- On submit, the app generates a replacement for the last paragraph using the current actor, text, and model selections. The existing last paragraph remains visible until the replacement succeeds; success replaces it in place rather than appending a duplicate.
- After successful replacement, exit retry mode and return the composer to its normal state with an empty input and `Player` selected.
- If the retry fails, keep the restored or edited input and current selections in the composer so the player can adjust them and try again.
- Disable `Retry` while another operation is in progress or after the scene is finished.
- Disable paragraph actions while another operation is in progress, while retry mode is active, or after the scene is finished.
- On touch layouts without hover, keep the actions available through a compact always-visible or tap-revealed action row.

## Bottom input area

### Actor dropdown

- A single-choice dropdown labeled `Actor`.
- Contains `Player` and all characters selected for this scene.
- `Player` is selected by default, and again after every successful turn.
- Selecting `Player` enables the player action input.
- Selecting a character changes the action to a character trigger.
- Only characters selected during scene creation appear in this dropdown.
- A character can be triggered repeatedly during the scene.

### Character LLM dropdown

- A single-choice dropdown labeled `Character LLM`.
- Contains the configured language models available to the application.
- Used when the selected actor is a character.
- The selected character LLM can be changed before each character turn.
- The control may be disabled or visually inactive when `Actor` is set to `Player`, because player turns do not call a character agent.

### Input field

- A multiline text input following the existing `MessageComposer` behavior.
- When `Actor` is `Player`, the input contains the player's action, words, or reaction.
- When `Actor` is a character, the input is optional guidance for that character's action.
- The placeholder changes with the selected actor so the purpose of the input is clear.
- Sending a player turn requires non-empty text.
- Sending a character turn may allow empty guidance, meaning the character reacts from the current scene context.
- When retrying the last paragraph, prefill this field with the text used for its original turn; keep it editable and allow it to be cleared.
- In retry mode, the composer remains the same widget but shows `Retrying last paragraph`, `Replace last paragraph`, and `Cancel retry` controls.

### Finish

- Keep the `Finish` button at the bottom-left of the composer area.
- Opens a tabbed modal for reviewing the scene summary and character memory updates before finishing.
- Is disabled while a turn is being processed or when the scene is already finished.

#### Finish modal

```text
┌──────────────────────────────────────────────────────────┐
│ Finish Scene                                              │
│ [Summary] [Captain Mora] [Harbor Guard] [Navigator]      │
│                                                          │
│ Editable bullet-text field for the selected tab          │
│                                                          │
│ [Generate all]                   [Cancel] [Finish scene] │
└──────────────────────────────────────────────────────────┘
```

- The first tab is `Summary` and contains the editable scene summary.
- Add one tab for each character participating in the scene, including the player character; each contains that character's editable memory update. The tab order is Summary, the player character, then the NPCs.
- Use character names as tab labels.
- Only the selected tab's editor is visible, keeping the modal compact as the number of characters grows.
- Keep each tab's text when the user switches between tabs.
- Allow the user to review and edit the generated summary and each character memory before submitting.
- `Generate all` generates the scene summary and memory updates for every participating character, regardless of which tab is active. It generates only tabs that are empty and never generated, or that failed; it does not overwrite tabs that are done, generating or already contain text.
- Show generation progress and completion or error status on each tab.
- If generation fails for one or more tabs, keep successful results and edits; allow retrying only the failed outputs.
- Provide `Regenerate this` for the currently selected tab to generate that output again without replacing the other tabs' content.
- Keep generation, validation, and submission errors visible in the modal without discarding edits.
- `Cancel` closes the modal without finishing the scene. Results of generation still running are discarded.
- `Finish scene` submits the reviewed summary and memory updates and closes the modal after success. It is disabled while any tab is generating, and the summary needs 1-100 non-empty items.
- A memory tab is resolved when it was generated successfully (even if the user then cleared it) or contains text. If any memory tab is unresolved, the first click on `Finish scene` shows an inline warning, "No memory update was generated or entered for: X, Y. Select Finish scene again to confirm." The second click proceeds, and generating or editing anything resets the warning.

### Send

- The primary action remains at the bottom-right.
- The label changes with the selected actor, for example `Send` for `Player` and `Trigger` for a character.
- In retry mode, use `Replace last paragraph` instead of the actor-specific submit label.
- Disable it while the character agent or narrator LLM is processing.
- Show progress for the current operation with one label chosen by the actor type, for example `Narrator is writing...` for a player turn and `Character and narrator are working...` for a character turn. A turn is one request, so the label does not change between the two calls.

## Loading and error behavior

- Keep the existing scene loading and operation-error patterns from `ScenePage.jsx`.
- During a multi-agent character turn, keep the composer disabled until the narrator paragraph is returned.
- If either the character call or the narrator call fails, nothing is saved; show an operation error. Retrying resubmits the whole request (a retried character action may differ from the failed attempt), and the Send button acts as the retry.
- A retry must not silently create a duplicate visible paragraph.
- Preserve the input and selected actor/model after a failed request so the player can retry or adjust it.
- A finished scene remains readable but its composer and paragraph actions are disabled.

## Implementation details

- Use `frontend/src/pages/ScenePage.jsx` as the page-level reference for loading, scrolling, busy state, errors, finishing, and model selection.
- Extract the header LLM selector into a reusable model select component.
- Extend or extract `MessageComposer` into an actor-aware composer with actor and character-LLM selectors.
- Replace the message-pair assumption in `MessageList` with a story timeline component that renders narrator paragraphs and paragraph actions.
- Keep the existing edit, delete, regenerate, finish-modal, response-time, and error components reusable where their behavior still matches.
- Keep intermediate turn details out of the visible UI until a later UX decision requires them.
