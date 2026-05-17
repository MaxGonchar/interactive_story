# Task 048: Frontend API Client — Real HTTP Calls

**Feature:** M6 — Services and Full Integration
**Status:** TODO

## Description

Replace all mocked return values and `throw new Error("not implemented")` stubs in the frontend API client modules (`api/stories.js` and `api/scenes.js`) with real `fetch` calls to the backend. All functions must use the base URL from an environment variable and return the parsed JSON response.

## Scope

What IS included:
- `frontend/src/api/stories.js`:
  - `getStories()` → `GET /api/stories`
  - `getStory(storyId)` → `GET /api/stories/{storyId}`
- `frontend/src/api/scenes.js`:
  - `getScene(storyId, sceneId)` → `GET /api/stories/{storyId}/scenes/{sceneId}`
  - `playScene(storyId, sceneId, content)` → `POST /api/stories/{storyId}/scenes/{sceneId}/play`
  - `editMessage(storyId, sceneId, messageId, content)` → `PUT /api/stories/{storyId}/scenes/{sceneId}/messages/{messageId}`
  - `deleteMessage(storyId, sceneId, messageId)` → `DELETE /api/stories/{storyId}/scenes/{sceneId}/messages/{messageId}`
  - `finishScene(storyId, sceneId, sceneSummary)` → `POST /api/stories/{storyId}/scenes/{sceneId}/finish`
- Base URL read from `import.meta.env.VITE_API_BASE_URL` (defaults to `http://localhost:8000`)
- Non-2xx responses throw an `Error` with the error body's `error.message`
- All mock data constants removed from both files

What is NOT included (deferred):
- UI error handling or toast notifications (existing component error handling is sufficient)
- Authentication headers
- Retry logic

## Deliverable

Updated `frontend/src/api/stories.js` and `frontend/src/api/scenes.js` with real fetch calls.

```
frontend/src/api/stories.js
frontend/src/api/scenes.js
```

## Acceptance Criteria

- [ ] `getStories()` returns `{ data: [...] }` from the real backend
- [ ] `getStory(storyId)` returns story detail from the real backend
- [ ] `getScene(storyId, sceneId)` returns scene detail including messages
- [ ] `playScene(storyId, sceneId, content)` sends POST with `{ content }` and returns `{ data: { user_message, assistant_message } }`
- [ ] `editMessage(...)` sends PUT with `{ content }` and returns the updated message
- [ ] `deleteMessage(...)` sends DELETE and returns `{ success: true }`
- [ ] `finishScene(storyId, sceneId, summary)` sends POST with `{ scene_summary }` and returns finished scene data
- [ ] Non-2xx responses throw a JS `Error` so existing UI error handlers fire
- [ ] No hardcoded mock data remains in either file
- [ ] Frontend builds without errors (`npm run build`)

## Test Notes

Manual end-to-end verification with both backend and frontend running:

1. Open `http://localhost:5173` — stories list loads from YAML
2. Click a story — scene list loads
3. Click a scene — messages render
4. Type a message and send — LLM response appears
5. Edit a message — content updates
6. Delete a message — message disappears
7. Click "Finish scene" — scene marked finished; edit/delete blocked

## Dependencies

046 (stories router wired), 047 (scenes router wired)
