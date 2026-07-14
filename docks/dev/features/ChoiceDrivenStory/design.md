# Feature: Choice-Driven Story

**Status**: Draft  
**Date**: 2026-06-28

## Summary

A new story type where the user advances the plot by selecting from AI-generated action choices rather than typing free-form messages. Two specialized LLM agents cooperate: N parallel Choice Engines each generate two options steered by a pre-configured plot direction, and a single Story Engine extends the narrative paragraph by paragraph based on the chosen action. The history is stored linearly; the user can return to any previous step and branch differently.

## Value

- **Problem it solves**: Free-form scene chat requires the user to drive the narrative themselves. Choice-driven stories offload that creative burden and deliver a more guided, game-like experience.
- **Fit**: Expands story-playing modes without touching the existing scene-based flow.
- **Success criteria**: User can open a choice-driven story, generate choices, pick one, see the story extended, and repeat — including returning to a past step and continuing differently.

## Scope

### In scope for first iteration
- Manual story creation (YAML files only, no UI)
- Stories list shows choice-driven stories alongside regular ones with a type indicator
- Dedicated playing page for choice-driven stories
- Generate choices: N parallel Choice Engines → 2N options shown in a 2-column grid
- Select a choice → Story Engine appends new paragraph
- Regenerate choices for the latest step
- Edit a paragraph's text (cosmetic correction only, no cascade)
- Return to a previous step (delete all subsequent steps)
- Persist history atomically to `history.yaml` after each operation
- Resume from saved state on page load (no re-generation if choices already exist)

### Out of scope / future
- UI creation of choice-driven stories
- Configurable truncation limit via UI
- Ending/conclusion detection
- Full branching tree (preserving all explored paths)

## User Flow

1. User opens the app and sees the stories list. Choice-driven stories show a type badge.
2. User selects a choice-driven story → navigates to the **Choice-Driven Story Page**.
3. Page renders the list of existing story paragraphs (steps) from history. Each paragraph has an edit icon and a return icon.
4. If the latest step has no choices yet, a "Generate choices" button is shown at the bottom.
5. User clicks "Generate choices" → N Choice Engines called in parallel → 2N choice cards appear in a 2-column grid.
6. User clicks a choice card → Story Engine called with last N paragraphs + chosen action + consequence → new paragraph appended → choice grid replaced by "Generate choices" button.
7. User repeats steps 4–6.
8. **Edit**: User clicks the edit icon on any paragraph → inline editor opens → user saves corrected text. Only the text of that step changes; choices and subsequent steps are untouched.
9. **Return**: User clicks the return icon on step N → all steps after N are deleted → step N's choices are shown again (or "Generate choices" button if none were saved).

## API Changes

### Modified

**`GET /api/stories`** — response item gains `type` field:
```json
{ "id": "...", "title": "...", "type": "scene" | "choice_driven" }
```

### New endpoints

**`GET /api/stories/{story_id}/choice-play`**  
Returns full play state. Used on page load.
```json
{
  "data": {
    "id": "...",
    "title": "...",
    "steps": [
      {
        "id": 1,
        "incoming_choice": null,
        "text": "The harbor fog rolled...",
        "choices": [
          { "action": "...", "consequence": "..." }
        ]
      },
      {
        "id": 2,
        "incoming_choice": { "action": "...", "consequence": "..." },
        "text": "The figure resolved...",
        "choices": []
      }
    ]
  }
}
```

---

**`POST /api/stories/{story_id}/choice-play/generate-choices`**  
Runs N Choice Engines in parallel for the latest step. Persists and returns all choices.
```json
Response 200:
{ "data": { "choices": [{ "action": "...", "consequence": "..." }] } }
```

---

**`POST /api/stories/{story_id}/choice-play/regenerate-choices`**  
Clears and regenerates choices for the latest step.
```json
Response 200:
{ "data": { "choices": [{ "action": "...", "consequence": "..." }] } }
```

---

**`POST /api/stories/{story_id}/choice-play/select-choice`**  
User picks a choice. Calls Story Engine, appends new step, persists, returns it.
```json
Request: { "action": "...", "consequence": "..." }

Response 200:
{
  "data": {
    "id": 2,
    "incoming_choice": { "action": "...", "consequence": "..." },
    "text": "New paragraph...",
    "choices": []
  }
}
```

---

**`PATCH /api/stories/{story_id}/choice-play/steps/{step_id}`**  
Cosmetic text edit. No cascade.
```json
Request:  { "text": "Corrected text..." }
Response: { "data": { "id": 1, "text": "Corrected text..." } }
```

---

**`DELETE /api/stories/{story_id}/choice-play/steps/{step_id}/forward`**  
Deletes all steps with id > step_id (return to step).
```json
Response 200: { "data": { "step_id": 2 } }
```

## Data Changes

### `data/stories/<story_id>/story.yaml` — new shape for choice-driven stories
```yaml
title: "..."
type: "choice_driven"
created_at: "2024-06-01T12:00:00Z"
character_ids:
  - "john"
writing_style: "dark, suspenseful, first-person"
plot_directions:
  - "Romance with Sarah"
  - "Betrayal by the Ally"
  - "Escaping the City"
```
No `scenes` list. `writing_style` and `plot_directions` are new fields specific to this type.
The story ID is derived from the enclosing folder name, not stored in the file.

### `data/stories/<story_id>/history.yaml` — new file
```yaml
steps:
  - id: 1
    incoming_choice: null
    text: "The harbor fog rolled in..."
    choices:
      - action: "Step into the fog"
        consequence: "A figure emerges from the shadows"
      - action: "Turn back to the inn"
        consequence: "You overhear a whispered conversation"
  - id: 2
    incoming_choice:
      action: "Step into the fog"
      consequence: "A figure emerges from the shadows"
    text: "The figure resolved into..."
    choices: []
```

Constraints:
- `id` is integer, sequential, never re-numbered
- `incoming_choice` is null only for step 1
- `choices` is empty list when not yet generated

## Backend Changes

### `app/models/domain.py`
- `StoryIndexItem`: add `type: Literal["scene", "choice_driven"]`
- New `Choice`: `action: str`, `consequence: str`
- New `Step`: `id: int`, `incoming_choice: Choice | None`, `text: str`, `choices: list[Choice]`
- New `ChoiceDrivenStoryMeta`: `id`, `title`, `writing_style: str`, `plot_directions: list[str]`, `character_ids: list[str]`

### `app/models/storage.py`
- New `ChoiceDrivenStoryYaml`: `title`, `type`, `created_at`, `character_ids`, `writing_style`, `plot_directions`
- New `ChoiceYaml`: `action`, `consequence`
- New `StepYaml`: `id`, `incoming_choice: ChoiceYaml | None`, `text`, `choices: list[ChoiceYaml]`
- New `HistoryYaml`: `steps: list[StepYaml]`

### `app/models/api.py`
- `StoryListItem`: add `type` field
- New `ChoiceResponse`, `StepResponse`, `ChoiceDrivenPlayResponse`, `GenerateChoicesResponse`, `SelectChoiceResponse`

### `app/utils/file_paths.py`
- Add `history_file(story_id: str) -> Path` → `data/stories/<story_id>/history.yaml`

### `app/repositories/story_repository.py`
- `list_stories`: include `type` from `StoriesIndexEntry` in returned `StoryIndexItem`

### New `app/repositories/choice_driven_story_repository.py`
- `get_story_meta(story_id)` → `ChoiceDrivenStoryMeta`
- `get_history(story_id)` → `list[Step]`
- `append_step(story_id, step)` → load, append, atomic save
- `update_step_choices(story_id, step_id, choices)` → load, replace choices on step, atomic save
- `update_step_text(story_id, step_id, text)` → load, mutate text, atomic save
- `truncate_from(story_id, step_id)` → delete steps where id > step_id, atomic save

### New `app/llm/choice_engine_client.py`
- `ChoiceEngineClient(plot_direction: str)`
- System prompt: character descriptions + plot direction
- `async invoke(story_text: str) -> list[Choice]`
- Parses the Markdown `### Option 1 / ### Option 2` output into `Choice` objects

### New `app/llm/story_engine_client.py`
- `StoryEngineClient`
- System prompt: character descriptions + writing style
- `async invoke(story_text: str, action: str, consequence: str) -> str`

### New `app/services/choice_driven_play_service.py`
- `ChoiceDrivenPlayService`
- `get_play_state(story_id)` → full step list for page load
- `generate_choices(story_id)` → build one `ChoiceEngineClient` per plot direction, run all via `asyncio.gather`, flatten 2N results, persist to latest step, return
- `regenerate_choices(story_id)` → same as above; clears existing choices first
- `select_choice(story_id, choice)` → call `StoryEngineClient` with last 10 paragraph texts + choice, append new step, return it
- `edit_step_text(story_id, step_id, text)` → delegate to repository
- `return_to_step(story_id, step_id)` → delegate `truncate_from` to repository
- Story context window: last 10 paragraphs (constant, to be tuned via testing)

### New `app/api/routers/choice_driven.py`
- All 6 new endpoints wired to `ChoiceDrivenPlayService` via `Depends`
- Registered in `main.py`

### `app/api/dependencies.py`
- Add factory functions for `ChoiceDrivenPlayService` and `ChoiceDrivenStoryRepository`

## Frontend Changes

### `frontend/src/pages/StoriesPage.jsx`
- Pass `story.type` forward; navigate to `/stories/:storyId/play` for `choice_driven`, existing `/stories/:storyId` path for `scene`

### `frontend/src/components/StoryList.jsx`
- Render type badge next to title

### `frontend/src/App.jsx`
- Add route: `/stories/:storyId/play` → `ChoiceDrivenStoryPage`

### New `frontend/src/api/choice_driven.js`
- `getChoiceDrivenPlay(storyId)` → `GET /api/stories/{storyId}/choice-play`
- `generateChoices(storyId)` → `POST .../generate-choices`
- `regenerateChoices(storyId)` → `POST .../regenerate-choices`
- `selectChoice(storyId, choice)` → `POST .../select-choice`
- `editStepText(storyId, stepId, text)` → `PATCH .../steps/{stepId}`
- `returnToStep(storyId, stepId)` → `DELETE .../steps/{stepId}/forward`

### New `frontend/src/pages/ChoiceDrivenStoryPage.jsx`
- Fetches play state on mount
- Renders `StepList` of paragraphs
- Renders `ChoicesGrid` or "Generate choices" button based on latest step state
- Handles all user actions: generate, select, regenerate, edit, return

### New `frontend/src/components/StepItem.jsx`
- Renders one story paragraph
- Edit icon → inline text editor with save/cancel
- Return icon → calls `returnToStep`

### New `frontend/src/components/ChoicesGrid.jsx`
- 2-column grid of choice cards (action text shown)
- Regenerate button triggers `regenerateChoices`

## Open Questions

- Should "return to step" require a confirmation dialog to prevent accidental loss of progress?
- Should consequences be shown on choice cards, or kept hidden to preserve the surprise?
- How to handle partial parallel failure: if 1 of N Choice Engines fails, return partial results or fail all?

## Risks

- **LLM output parsing**: Choice Engine output is Markdown-structured. Deviation from the expected `### Option 1 / ### Option 2` format will cause parse failures. Needs a robust parser with a clear error response.
- **Parallel LLM calls**: N concurrent requests per "Generate choices" click. With N=3 this is 3 simultaneous Venice AI calls — acceptable locally, but latency adds up.
- **Growing story context**: Truncating to last 10 paragraphs may cause continuity issues in long stories. Correct limit unknown before testing.
