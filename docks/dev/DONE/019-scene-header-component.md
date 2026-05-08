# Task 019: SceneHeader Component

**Feature:** M3 — Frontend UI Pages (Mocked)
**Status:** TODO

## Description

Implement the `SceneHeader` presentational component. Displays the scene id, its finished/active status, and the entry point text from `scene_description`.

## Scope

What IS included:
- `SceneHeader` component accepting `scene: { id, finished, scene_description: { entry_point } }` prop
- Renders scene id, status badge ("Active" or "Finished"), and entry point text

What is NOT included (deferred):
- Full `scene_description` fields (`general_scene_guide`, `writing_style`) — not shown in header
- Scene summary display (belongs to `SceneActions`, task 023)

## Deliverable

`frontend/src/components/SceneHeader.jsx` — a functional React component.

```
frontend/src/components/SceneHeader.jsx
```

## Acceptance Criteria

- [ ] Renders "Scene {id}" heading
- [ ] Shows "Active" when `finished` is `false`; shows "Finished" when `finished` is `true`
- [ ] Renders `scene_description.entry_point` text
- [ ] Component is the default export

## Test Notes

Render with `scene={id:3, finished:false, scene_description:{entry_point:"Fog rolls..."}}` and verify all three pieces of information are visible.

## Dependencies

None
