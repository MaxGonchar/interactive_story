# Task 014: Mocked API Client — scenes.js

**Feature:** M3 — Frontend UI Pages (Mocked)
**Status:** TODO

## Description

Create the `api/scenes.js` module with mocked implementations of all scene-related API calls. Returns hardcoded data matching the real endpoint shapes from `endpoints.md`.

## Scope

What IS included:
- `getScene(storyId, sceneId)` — returns a hardcoded scene object with messages, `finished` flag, `scene_description`, and `scene_summary`

What is NOT included (deferred):
- `playScene()`, `editMessage()`, `deleteMessage()`, `finishScene()` (needed in M6 when real calls are wired; stubs are acceptable here if `SceneActions` or `MessageComposer` need an importable reference)
- Real HTTP calls (M6)
- `api/stories.js` (task 013)

## Deliverable

`frontend/src/api/scenes.js` with `getScene` exported as an async function returning hardcoded data. Stub exports (throw `new Error("not implemented")`) for `playScene`, `editMessage`, `deleteMessage`, `finishScene` so imports don't break in M3 components.

```
frontend/src/api/scenes.js
```

## Acceptance Criteria

- [ ] `getScene(storyId, sceneId)` is exported and returns `{ data: { id, finished, scene_description, scene_summary, messages } }` matching `endpoints.md`
- [ ] Mocked messages include at least one `role: "assistant"` and one `role: "user"` entry
- [ ] `finished: false` in the mocked active scene so finish-button is visible during manual testing
- [ ] `playScene`, `editMessage`, `deleteMessage`, `finishScene` are exported stubs (throw `Error("not implemented")`)

## Test Notes

Import and call `getScene("any-id", 1)` in browser console; verify resolved shape matches endpoint spec.

## Dependencies

None
