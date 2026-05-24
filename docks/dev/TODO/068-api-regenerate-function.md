# Task 068: Add `regenerateLastAssistantMessage` API Function

**Feature:** Regenerate last assistant message
**Status:** TODO

## Description

Add an exported `regenerateLastAssistantMessage(storyId, sceneId)` function to `frontend/src/api/scenes.js`. It calls `POST /api/stories/{storyId}/scenes/{sceneId}/regenerate` with no request body and returns the parsed JSON response. Follows the exact same pattern as the existing `finishScene`, `playScene`, etc. functions in that file.

## Scope

What IS included:
- New exported async function `regenerateLastAssistantMessage(storyId, sceneId)` in `frontend/src/api/scenes.js`
- Uses the existing `apiFetch` helper — no direct `fetch` calls
- HTTP method: `POST`, no `Content-Type` header, no body

What is NOT included (deferred):
- Component or page wiring (tasks 069–071)
- Error handling beyond what `apiFetch` already does

## Deliverable

One new exported function appended to `frontend/src/api/scenes.js`:

```
frontend/src/api/scenes.js
```

```js
export async function regenerateLastAssistantMessage(storyId, sceneId) {
  return apiFetch(
    `/api/stories/${storyId}/scenes/${sceneId}/regenerate`,
    { method: "POST" }
  );
}
```

## Acceptance Criteria

- [ ] `regenerateLastAssistantMessage` is exported from `scenes.js`
- [ ] Calling it sends a `POST` request to `/api/stories/{storyId}/scenes/{sceneId}/regenerate` with no body
- [ ] Returns the full JSON response object (same as other API functions)
- [ ] No other functions in `scenes.js` are modified
- [ ] Frontend app builds without errors (`npm run build` or `npm run dev`)

## Test Notes

Manual: import in browser console or call via ScenePage once wired in task 071. Verify the request appears in the Network tab with the correct URL and method.

## Dependencies

- 066 (backend endpoint must exist for end-to-end testing; not a code dependency)
