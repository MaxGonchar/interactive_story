# Task 058: ScenePage Wire Edit Handler

**Feature:** Edit message — UI layer
**Status:** TODO

## Description

Wire the edit message feature into `ScenePage`. Import `editMessage` from the API client, create a `handleEditMessage` handler that calls the API and updates `scene.messages` in state on success, and pass `onEdit={handleEditMessage}` and `disabled={scene.finished}` to `<MessageList>`. Also integrate a shared `busy` state so the Save button in `MessageItem` is disabled while any other async operation (play, finish) is in flight.

## Scope

What IS included:
- Import `editMessage` from `../api/scenes`
- `handleEditMessage(messageId, content)` async handler:
  - Calls `editMessage(storyId, sceneId, messageId, content)`
  - On success: updates `scene.messages` by replacing the matching message with `res.data`
  - On error: surfaces error (console or existing error state)
- `onEdit={handleEditMessage}` prop passed to `<MessageList>`
- `disabled={scene.finished}` prop passed to `<MessageList>`
- Shared `busy` state: set `true` before any async call (play, finish, edit), reset to `false` in `finally`; pass `disabled={scene.finished || busy}` to `<MessageList>` and `<MessageComposer>`

What is NOT included (deferred):
- Full error UI (toast / modal) — out of scope
- Tests

## Deliverable

Modified `frontend/src/pages/ScenePage.jsx` with `editMessage` imported, `handleEditMessage` implemented, `<MessageList>` wired with `onEdit` and `disabled`, and `busy` state integrated.

```
frontend/src/pages/ScenePage.jsx
```

## Acceptance Criteria

- [ ] `editMessage` is imported from `../api/scenes`
- [ ] `handleEditMessage(messageId, content)` calls `editMessage` with correct `storyId`, `sceneId`, `messageId`, `content`
- [ ] After a successful response, the edited message is updated in `scene.messages` state (server-confirmed, not optimistic)
- [ ] `<MessageList>` receives `onEdit={handleEditMessage}` and `disabled={scene.finished || busy}`
- [ ] While any async operation is in flight (`busy === true`), the edit Save button (via `disabled` prop) is not usable
- [ ] No state update occurs if `editMessage` throws (error is caught)

## Test Notes

Manual verification:
1. Open a non-finished scene. Click edit on a message, change the content, click Save.
2. The bubble should update to the new content without a page reload.
3. Open browser DevTools → Network. Confirm a `PUT /api/stories/.../messages/...` request was sent with `{ content: "..." }`.
4. While the play/finish request is in flight, attempt to save an edit — the Save button should be disabled.

## Dependencies

057, 055 (ScenePage play/finish wiring — `busy` state needs to be shared)
