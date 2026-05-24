# Task 054: Add Summary Input to SceneActions

**Feature:** Fix non-working Send and Finish buttons on scene page
**Status:** TODO

## Description

`SceneActions` currently renders only a "Finish Scene" button that calls `onFinish()` with no arguments. `POST /finish` requires a non-empty `scene_summary` string, so the page can never collect that value. This task adds a controlled `<textarea>` inside `SceneActions` for the user to type the summary, and changes the button to pass the text to `onFinish(summaryText)` — but only when the field is non-empty.

## Scope

What IS included:
- `frontend/src/components/SceneActions.jsx` — add `useState` for summary text, add a `<textarea maxLength={2000}>`, change `<button onClick={onFinish}>` to `<button onClick={() => onFinish(summaryText)} disabled={!summaryText.trim()}>`.
- `maxLength={2000}` enforced on the textarea (API constraint).

What is NOT included (deferred):
- Styling / CSS for the textarea (may be left unstyled for now).
- Error display within `SceneActions`.
- Any changes to `ScenePage.jsx` (covered in Task 055).

## Deliverable

Updated `SceneActions.jsx` that:
- When scene is not finished: renders a `<textarea>` for summary input and a "Finish Scene" button that is disabled while the textarea is empty.
- When scene is already finished: renders the existing read-only `sceneSummary` paragraph (unchanged).

```
frontend/src/components/SceneActions.jsx
```

## Acceptance Criteria

- [ ] `SceneActions` renders a `<textarea>` when `finished` is `false`.
- [ ] The "Finish Scene" button is disabled when the textarea is empty or whitespace-only.
- [ ] Clicking the button calls `onFinish` with the trimmed summary string.
- [ ] `maxLength={2000}` is set on the textarea.
- [ ] The finished-state rendering (read-only `sceneSummary` paragraph) is unchanged.

## Test Notes

Manual verification:
1. Open a scene that is not finished.
2. Confirm a textarea is visible above (or below) the "Finish Scene" button.
3. Confirm the button is disabled when the textarea is empty.
4. Type a summary and confirm the button becomes enabled.
5. Click the button; the `onFinish` callback should receive the typed summary string (verify via console.log wired in `ScenePage` or after Task 055 is applied).

## Dependencies

None (can be implemented independently; Task 055 depends on this task).
