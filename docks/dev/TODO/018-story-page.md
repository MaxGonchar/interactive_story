# Task 018: StoryPage

**Feature:** M3 — Frontend UI Pages (Mocked)
**Status:** TODO

## Description

Implement the `StoryPage` page component. Reads `storyId` from the URL, calls `getStory(storyId)` on mount, and renders story title and a `SceneList`. Navigates to `ScenePage` when a scene is selected.

## Scope

What IS included:
- `StoryPage` component: reads `:storyId` from route params, calls `getStory()` on mount
- Renders story title and `SceneList` with scenes and `activeSceneId`
- Navigates to `/stories/:storyId/scenes/:sceneId` on scene selection
- Loading and error states

What is NOT included (deferred):
- `SceneList` implementation (task 017)
- Routing configuration (task 025)

## Deliverable

`frontend/src/pages/StoryPage.jsx` — a functional React component that fetches and displays a single story.

```
frontend/src/pages/StoryPage.jsx
```

## Acceptance Criteria

- [ ] Reads `storyId` from React Router params
- [ ] Calls `getStory(storyId)` on mount via `useEffect`
- [ ] Renders the story title
- [ ] Renders `SceneList` with `scenes` and `activeSceneId` from the response
- [ ] Navigates to `/stories/:storyId/scenes/:sceneId` when `SceneList` calls `onSelect`
- [ ] Shows loading indicator while fetching; shows error message on failure
- [ ] Component is the default export

## Test Notes

Navigate to `/stories/some-id` in the browser; verify story title and scene list appear and clicking a scene navigates correctly.

## Dependencies

- 013 (mock stories API)
- 017 (SceneList component)
