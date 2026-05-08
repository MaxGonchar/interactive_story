# Task 017: SceneList Component

**Feature:** M3 — Frontend UI Pages (Mocked)
**Status:** TODO

## Description

Implement the `SceneList` presentational component. Receives an array of scene summary objects and renders them as a list. Visually distinguishes finished vs. active scenes. Calls `onSelect` when a scene is clicked.

## Scope

What IS included:
- `SceneList` component that accepts `scenes: [{ id, finished }]`, `activeSceneId`, and `onSelect(sceneId)` props
- Renders each scene as a list item labeled "Scene {id}" with a finished/active indicator
- Calls `onSelect(scene.id)` on click

What is NOT included (deferred):
- Fetching data (done in `StoryPage`, task 018)
- Routing/navigation (done in page-level tasks)

## Deliverable

`frontend/src/components/SceneList.jsx` — a functional React component rendering a list of scenes.

```
frontend/src/components/SceneList.jsx
```

## Acceptance Criteria

- [ ] Renders one list item per scene in the `scenes` prop
- [ ] Each item shows scene id and a label or style distinguishing `finished: true` from `finished: false`
- [ ] The active scene (matching `activeSceneId`) is visually highlighted or labelled "Active"
- [ ] Clicking a scene item calls `onSelect` with the correct scene id
- [ ] Component is the default export

## Test Notes

Render with `scenes=[{id:1,finished:true},{id:2,finished:false}]` and `activeSceneId=2`; verify labels and click behaviour.

## Dependencies

None
