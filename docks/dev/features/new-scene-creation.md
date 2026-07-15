# Feature: New Scene Creation

**Status**: Draft  
**Date**: 2026-07-15

## Summary
Allow users to create new scenes directly from the story page, replacing the current error-prone manual workflow of creating folders and writing YAML files by hand. The feature covers two cases: creating the very first scene in a story (all fields entered from scratch) and creating a subsequent scene (key fields prepopulated from the last finished scene so the user only fills in what changes).

## Value
- Eliminates manual folder and YAML file creation — currently the primary source of mistakes.
- Makes the app self-sufficient for the most frequent content-creation task.
- Speeds up the between-scene transition, keeping the playing flow uninterrupted.
- **Success criteria**: a user can go from a finished scene to a playable new scene entirely within the UI, without touching the filesystem.

## Scope

### In scope for first iteration
- "Create new scene" button on the story page, disabled when an active scene already exists.
- Scene creation form with all required fields (user character, characters, context, general scene guide, writing style, first message).
- Prepopulation from the last finished scene for subsequent scenes (context = previous context + previous summary; writing style and first message carried over).
- `GET /api/stories/{story_id}/characters` — new endpoint to list story characters.
- `POST /api/stories/{story_id}/scenes` — new endpoint to create a scene.
- Active-scene guard: 409 if a non-finished scene already exists.
- Redirect to the newly created scene page after successful creation.
- Reuse `BulletTextarea` pattern (extracted from `FinishModal.jsx`) for the context field.

### Out of scope / future
- LLM-generated `general_scene_guide`.
- Story creation and character creation via UI.
- Branching from arbitrary earlier scenes (always inherits from last finished).
- Automated between-scene state updates (character memory, prompt evolution).

## User Flow

1. User lands on the story page. All existing scenes are finished (or no scenes exist yet) → "Create new scene" button is enabled.
2. If an active scene exists → button is disabled; no navigation possible.
3. User clicks the button → navigated to `/stories/:storyId/scenes/new`.
4. **First scene** (no previous scenes): all fields are empty, all fields are required.
5. **Subsequent scene** (previous scenes exist):
   - *Context* — prepopulated with previous scene's `context` + `scene_summary` merged into bullet-list format; editable.
   - *Writing style* — prepopulated from previous scene's `writing_style`; editable.
   - *First message* — prepopulated with the last assistant message of the previous scene; editable.
   - *User character*, *Characters*, *General scene guide* — always empty, required.
6. Character selection uses two linked controls fed from the same full story character list:
   - *User character* dropdown — required, exactly one must be selected. Shows all characters not currently checked in the checkboxes.
   - *Scene characters* checkboxes — optional, zero or more. Shows all characters not currently selected in the dropdown. An empty selection is valid (solo scene with user character only).
   - Selecting a character in the dropdown immediately removes it from the checkbox list, and vice versa.
   - The two sets are always mutually exclusive.
7. User fills in or edits the remaining fields.
8. User clicks "Create" → client-side validation runs.
9.  On validation pass → `POST /api/stories/{story_id}/scenes` called.
10. On success → redirect to `/stories/:storyId/scenes/:newSceneId`.
11. On error → inline error displayed, user stays on the form.

## API Changes

### New: `GET /api/stories/{story_id}/characters`

List all characters defined for a story.

**Response 200**
```json
{
  "data": [
    { "id": "captain-mora", "name": "Captain Mora" },
    { "id": "harbor-guard", "name": "Harbor Guard" }
  ]
}
```

**Response 404** — story not found

---

### New: `POST /api/stories/{story_id}/scenes`

Create a new scene.

**Request body**
```json
{
  "user_character_id": "captain-mora",
  "character_ids": ["harbor-guard"],
  "context": ["The crew arrived at Black Harbor.", "Mora suspects a betrayal."],
  "general_scene_guide": "Build tension through a tense negotiation at the docks.",
  "writing_style": "Cinematic, sensory details, concise dialog turns.",
  "first_message": "The dockmaster eyes you with suspicion as you approach..."
}
```

**Response 201**
```json
{
  "data": {
    "id": 4,
    "finished": false
  }
}
```

**Errors**
- `404 not_found` — story not found
- `409 active_scene_exists` — a non-finished scene already exists; creation is blocked
- `422 validation_error` — `user_character_id` missing, `user_character_id` appears in `character_ids`, or unknown character ids

## Data Changes

No changes to existing YAML schemas. Scene creation writes two new files:

- `data/stories/{story_id}/scenes/{scene_id}/meta.yaml` — all metadata fields (`character_ids`, `user_character_id`, `context`, `scene_description`, `finished: false`, `scene_summary: null`).
- `data/stories/{story_id}/scenes/{scene_id}/messages.yaml` — single assistant message with `id: 1`.

**Scene ID generation**: `max(existing scene ids) + 1`; if no scenes exist, `id = 1`. Derived from filesystem folder names, consistent with current convention.

## Backend Changes

| Layer | Change |
|---|---|
| `CharacterRepository` | Add `list_characters(story_id) -> list[CharacterCard]` — scans `characters/` dir, returns all character cards (id + name sufficient for the response). |
| New `SceneCreationService` | Orchestrates: validate no active scene exists, derive next scene id, write `meta.yaml` and `messages.yaml`, return new scene ref. |
| `SceneRepository` | Add `create_scene(story_id, scene_id, metadata, first_message)` — creates scene directory and writes both files. |
| New `CreateSceneRequest` model | Pydantic request model with validation: `user_character_id` required; `character_ids` is a list defaulting to `[]` (empty = solo scene); `user_character_id` must **not** appear in `character_ids`. |
| New `CharacterListResponse` model | Response model for `GET /characters`. |
| Scenes router | Add handler for `POST /api/stories/{story_id}/scenes`. |
| New characters router | Add handler for `GET /api/stories/{story_id}/characters`. |
| New error code | `active_scene_exists` — 409 response when creation is attempted with an active scene present. |

## Frontend Changes

| Component / Page | Change |
|---|---|
| `BulletTextarea` (new shared component) | Extract `parseItems`, `normalisePaste`, Enter-key and paste handling from `FinishModal.jsx` into a reusable component. |
| `StoryPage` | Add "Create new scene" button; disabled when `active_scene_id !== null`. Navigates to `/stories/:storyId/scenes/new`. |
| `NewScenePage` (new page) | Full scene creation form: linked user-character dropdown + scene-characters checkboxes (mutually exclusive, both derived from the full character list), context (`BulletTextarea`), general scene guide textarea, writing style textarea, first message textarea, "Create" button, inline error display. Fetches characters via `GET /characters`; fetches last scene data for prepopulation if scenes exist. |
| `App.jsx` | Add route `/stories/:storyId/scenes/new` → `NewScenePage`. |
| `src/api/scenes.js` | Add `createScene(storyId, payload)` function. |
| `src/api/characters.js` (new) | Add `getCharacters(storyId)` function. |

## Open Questions

- Should the backend validate that all submitted `character_ids` and `user_character_id` actually exist as character files on disk, or is a missing character only caught at play time?

## Risks

- **Partial write failure**: scene directory creation and writing two YAML files are not a single atomic operation. A crash mid-way could leave an orphaned directory with incomplete files. Mitigation: write to a temp location and rename (extend `atomic_write`), or add a cleanup step on startup for incomplete scenes.
- **Race conditions**: not a real concern for single-user local usage, but worth noting if the usage model ever changes.
- **Prepopulation data availability**: the last scene's `scene_summary` must exist for meaningful context prepopulation. If the previous scene was finished without a summary, the context will only carry forward `context`. The UI should handle a `null` summary gracefully.
