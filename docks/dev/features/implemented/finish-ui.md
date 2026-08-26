# Feature: Scene Finish UI

**Status**: Draft  
**Date**: 2026-07-08

## Summary
Add a "Finish" button to the Scene Page that opens a modal where the user enters a scene summary as a list of items. On submit, the scene is marked finished and the user is redirected to the story scenes page. This completes the core MVP scene lifecycle flow.

## Value
- Allows the user to formally close a scene with a structured summary from within the UI.
- Fits the core MVP purpose: playing and completing scenes in-app.
- Success criteria: user can open the finish modal, enter a multi-item summary, submit, and land on the story page with the scene shown as finished.

## Scope
**In scope for first iteration:**
- "Finish" button on the Scene Page (visible only when scene is not finished).
- Modal with a list-format textarea for summary input and Cancel / Submit buttons.
- Auto-insert `- ` prefix on Enter keypress.
- Paste normalization: lines already starting with `- ` are kept; other non-empty lines get `- ` prepended; empty lines are dropped.
- Client-side validation: at least 1 item, max 100 items (lines starting with `- ` after trim).
- On submit: call `POST .../finish`, close modal, redirect to story scenes page.
- Backend API update: `scene_summary` changed from `str` to `list[str]` in request, response, and scene detail models.

**Out of scope / future:**
- UI for editing scene summary after submission.
- Next scene creation via UI.
- Automated summary generation.
- Support for bullet styles other than `-` (e.g. `*`, `+`).

## User Flow
1. User is on the Scene Page for an active (unfinished) scene.
2. User clicks the **Finish** button (located below the Send button).
3. A modal opens with:
   - A title ("Finish Scene").
   - A large textarea pre-populated with `- ` on the first line as a hint.
   - A **Cancel** button and a **Submit** button.
4. User types or pastes summary items. Each line starting with `- ` is one item.
   - Pressing Enter auto-inserts `- ` at the start of the new line.
   - Pasting text normalizes each non-empty line to have `- ` prefix.
5. User clicks **Submit**.
   - Client parses items: splits on newlines, filters lines starting with `- `, strips the prefix to get content strings.
   - Validates: 1–100 non-empty items; shows inline error if not met.
   - Calls `POST /api/stories/{story_id}/scenes/{scene_id}/finish` with the parsed list.
6. On success: modal closes, user is redirected to `/stories/{story_id}`.
7. User clicks **Cancel**: modal closes, draft summary is discarded.

## API Changes

### POST /api/stories/{story_id}/scenes/{scene_id}/finish

**Request** — `scene_summary` changes from `str` to `list[str]`:
```json
{
  "scene_summary": [
    "The hero discovered the map.",
    "Escaped the harbor before dawn."
  ]
}
```
Validation:
- `scene_summary`: required, non-empty list, min 1 item, max 100 items, each item a non-empty string.

**Response 200** — `scene_summary` changes from `str` to `list[str]`:
```json
{
  "data": {
    "id": 3,
    "finished": true,
    "scene_summary": [
      "The hero discovered the map.",
      "Escaped the harbor before dawn."
    ]
  }
}
```

### GET /api/stories/{story_id}/scenes/{scene_id}

`scene_summary` in the response changes from `str | null` to `list[str] | null`:
```json
{
  "data": {
    "...": "...",
    "scene_summary": ["Item one.", "Item two."],
    "...": "..."
  }
}
```

## Data Changes
No structural change — `scene_summary` in `metadata.yaml` is already stored as a YAML list (`list[str] | null`) in the domain model. Only the API layer was misaligned.

## Backend Changes

**`backend/app/models/api.py`** — three field type fixes:
- `FinishSceneRequest.scene_summary`: `str` → `list[str]` with min 1 / max 100 item-count validation.
- `FinishedSceneData.scene_summary`: `str` → `list[str]`.
- `SceneDetail.scene_summary`: `str | None` → `list[str] | None`.

**`docks/dev/endpoints.md`** — update request/response examples for `POST .../finish` and `GET .../scenes/{scene_id}` to reflect `list[str]`.

No changes needed to services, repositories, or storage — the domain model is already correct.

## Frontend Changes

**`frontend/src/components/FinishSceneModal.jsx`** *(new component)*
- Modal overlay with title, textarea, Cancel and Submit buttons.
- Textarea behavior: auto-insert `- ` on Enter; paste normalization on `paste` event.
- Client-side validation: parse items from textarea, enforce 1–100 items, show inline error.
- Emits parsed `string[]` to parent on submit; emits cancel signal on Cancel.

**`frontend/src/components/SceneActions.jsx`** *(modified)*
- Replace current inline textarea + button with a "Finish" button that toggles modal visibility.
- When scene is finished: display the summary list (read-only).

**`frontend/src/pages/ScenePage.jsx`** *(modified)*
- `handleFinish`: after successful API call, redirect to `/stories/{storyId}` using React Router `navigate`.

**`frontend/src/api/scenes.js`** *(modified)*
- `finishScene`: update payload shape — `scene_summary` is now `string[]`.

## Open Questions
- Should the textarea have a visible item counter (e.g. "3 / 100 items") to help the user track the limit? - No

## Risks
- Paste normalization edge cases: pasted content with leading spaces before `-`, mixed bullet styles, or multi-line items. First iteration handles only `- ` prefix; anything else gets auto-prefixed as a new item.
- The auto-insert on Enter interacts with browser undo history in non-obvious ways — may need testing across browsers.
