# Task 024: ScenePage

**Feature:** M3 — Frontend UI Pages (Mocked)
**Status:** TODO

## Description

Implement the `ScenePage` page component. Reads `storyId` and `sceneId` from the URL, fetches scene data via `getScene()`, and composes `SceneHeader`, `MessageList`, `MessageComposer`, and `SceneActions` into the full scene view.

## Scope

What IS included:
- `ScenePage` component: reads `:storyId` and `:sceneId` from route params
- Calls `getScene(storyId, sceneId)` on mount
- Renders `SceneHeader`, `MessageList`, `MessageComposer` (disabled when finished), and `SceneActions`
- `onSend` handler logs the content to console (real call wired in M6)
- `onFinish` handler logs to console (real call wired in M6)
- Loading and error states

What is NOT included (deferred):
- Real `playScene` or `finishScene` API calls (M6)
- Message edit/delete (M6)
- Routing configuration (task 025)

## Deliverable

`frontend/src/pages/ScenePage.jsx` — a functional React component composing all scene sub-components.

```
frontend/src/pages/ScenePage.jsx
```

## Acceptance Criteria

- [ ] Reads `storyId` and `sceneId` from React Router params
- [ ] Calls `getScene(storyId, sceneId)` on mount via `useEffect`
- [ ] Renders `SceneHeader` with scene data
- [ ] Renders `MessageList` with `messages` from response
- [ ] Renders `MessageComposer` with `disabled={scene.finished}`
- [ ] Renders `SceneActions` with `finished`, `sceneSummary`, and `onFinish={()=>console.log("finish")}`
- [ ] Shows loading indicator while fetching; shows error message on failure
- [ ] Component is the default export

## Test Notes

Navigate to `/stories/some-id/scenes/3` in the browser. Verify header, messages, composer, and finish button all render. Verify composer is disabled on a finished scene (change mock `finished` to `true` to test).

## Dependencies

- 014 (mock scenes API)
- 019 (SceneHeader)
- 021 (MessageList)
- 022 (MessageComposer)
- 023 (SceneActions)
