# Task 055: Wire playScene and finishScene in ScenePage

**Feature:** Fix non-working Send and Finish buttons on scene page
**Status:** TODO

## Description

`ScenePage.jsx` contains stub handlers (`() => console.log('send')` and `() => console.log('finish')`) that were left over from the M3 mocked phase. Neither `playScene` nor `finishScene` is imported. This task replaces both stubs with real API calls, adds a `sending` loading state to prevent duplicate submissions, and updates state from the server responses.

## Scope

What IS included:
- `frontend/src/pages/ScenePage.jsx`:
  - Import `playScene` and `finishScene` from `../api/scenes`.
  - Add a `sending` boolean state (default `false`).
  - `handleSend(content)`: set `sending = true`, call `playScene(storyId, sceneId, content)`, append `response.data.user_message` and `response.data.assistant_message` to `scene.messages` in state, set `sending = false` in a `finally` block.
  - `handleFinish(summary)`: call `finishScene(storyId, sceneId, summary)`, update `scene.finished` and `scene.scene_summary` in state from `response.data`.
  - Pass `onSend={handleSend}` and `disabled={scene.finished || sending}` to `<MessageComposer>`.
  - Pass `onFinish={handleFinish}` to `<SceneActions>`.
  - Display an inline error message (`opError` state) if either call fails, cleared on next attempt.

What is NOT included (deferred):
- Changes to `SceneActions.jsx` (covered in Task 054 — must be completed first so `onFinish` receives a summary string).
- Changes to `MessageComposer.jsx` (already correct).
- Frontend tests (out of MVP scope).

## Deliverable

Updated `ScenePage.jsx` with real `handleSend` and `handleFinish` handlers wired to the API, a `sending` state, and error display.

```
frontend/src/pages/ScenePage.jsx
```

## Acceptance Criteria

- [ ] `playScene` and `finishScene` are imported from `../api/scenes`.
- [ ] Pressing Send (with text in the composer) triggers `POST /api/stories/{storyId}/scenes/{sceneId}/play`; the two returned messages are appended to the message list in the UI.
- [ ] The `<MessageComposer>` `disabled` prop is `true` while a play request is in flight, preventing duplicate sends.
- [ ] State is updated only after a successful response (no optimistic update).
- [ ] Pressing Finish (after Task 054 adds the summary textarea) triggers `POST /api/stories/{story_id}/scenes/{sceneId}/finish`; the scene transitions to `finished: true` and `scene_summary` is shown.
- [ ] An error message is rendered in the UI if `playScene` or `finishScene` rejects.
- [ ] No console-log stubs remain.

## Test Notes

Manual end-to-end verification (requires backend running):
1. Start the backend (`make run-backend` or equivalent).
2. Open an active scene in the browser.
3. Type a message and press Send. Confirm two new message bubbles appear (user + assistant).
4. Confirm the composer is disabled while the request is in flight and re-enabled after.
5. Type a summary in the finish textarea and press Finish Scene. Confirm the scene shows `finished` status and the summary text.
6. Confirm that after finishing, the composer and Finish button are disabled/hidden.
7. Kill the backend, attempt to send — confirm an error message appears.

## Dependencies

Task 054 (SceneActions must pass `summaryText` to `onFinish` before the finish flow can be tested end-to-end).
