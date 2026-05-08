# Task 023: SceneActions Component

**Feature:** M3 — Frontend UI Pages (Mocked)
**Status:** TODO

## Description

Implement the `SceneActions` presentational component. Shows the "Finish Scene" button for active scenes, and the scene summary for finished scenes. Calls `onFinish()` when the button is clicked.

## Scope

What IS included:
- `SceneActions` component accepting `finished`, `sceneSummary`, and `onFinish` props
- When `finished` is `false`: renders a "Finish Scene" button that calls `onFinish()`
- When `finished` is `true`: renders the `sceneSummary` text (or a placeholder if summary is null)

What is NOT included (deferred):
- Actual finish API call (M6)
- Confirmation dialog before finishing

## Deliverable

`frontend/src/components/SceneActions.jsx` — a functional React component.

```
frontend/src/components/SceneActions.jsx
```

## Acceptance Criteria

- [ ] When `finished` is `false`: "Finish Scene" button is visible and calls `onFinish` when clicked
- [ ] When `finished` is `true`: button is not rendered; scene summary text is shown instead
- [ ] When `finished` is `true` and `sceneSummary` is `null`: shows a placeholder like "No summary available."
- [ ] Component is the default export

## Test Notes

Render with `finished={false}` and `onFinish={console.log}`; verify button appears and click logs. Then render with `finished={true}` and `sceneSummary="The hero escaped."` and verify summary text appears.

## Dependencies

None
