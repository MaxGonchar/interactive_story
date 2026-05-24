# Task 062: ScenePage Wire Delete Handler

**Feature:** Delete message — UI layer
**Status:** TODO

## Description

Import `deleteMessage` from `../api/scenes` in `ScenePage`. Add a `handleDeleteLastExchange` handler that deletes the target user message and the immediately following assistant message via two sequential API calls, then removes both from local state. Wire `onDelete` and `disabled` props to `<MessageList>`.

## Scope

What IS included:
- Import `deleteMessage` from `../api/scenes`
- `handleDeleteLastExchange(userMessageId)` handler:
  - Finds the user message index in `scene.messages`
  - Identifies the immediately following message as `assistantMsg` (if it exists and follows)
  - Calls `deleteMessage(storyId, sceneId, userMessageId)`
  - If `assistantMsg` exists, calls `deleteMessage(storyId, sceneId, assistantMsg.id)`
  - On success, removes both messages from `scene.messages` via `setScene`
  - Shows an error (console or UI) if the second delete fails; reflects partial state (user message already gone)
- `<MessageList onDelete={handleDeleteLastExchange} disabled={scene.finished} />`
- Delete button disabled while another async operation is in flight (reuse existing `busy` state if present, or add one)

What is NOT included (deferred):
- Atomic backend deletion (two separate calls, sequential — acceptable for MVP)
- Confirmation dialog
- Tests

## Deliverable

Modified `frontend/src/pages/ScenePage.jsx` with `deleteMessage` import, `handleDeleteLastExchange` handler, and updated `<MessageList>` props.

```
frontend/src/pages/ScenePage.jsx
```

## Acceptance Criteria

- [ ] `deleteMessage` is imported from `../api/scenes`
- [ ] Clicking the delete button on the last user message bubble calls `DELETE /api/stories/{storyId}/scenes/{sceneId}/messages/{userMessageId}`
- [ ] If a following assistant message exists, a second `DELETE` call is made for that message's id
- [ ] Both messages are removed from the rendered message list on success
- [ ] If only the user message has no following assistant message, only one `DELETE` is called and only that message is removed
- [ ] Delete button is absent (or disabled) when `scene.finished === true`
- [ ] Delete button is disabled while a play/finish/edit request is in flight (busy state)

## Test Notes

Manual verification:
1. Open a non-finished scene with at least one user + assistant exchange.
2. Click the delete icon on the last user message. Both the user and assistant bubbles should disappear. Reload — messages should still be gone (YAML updated).
3. Open a finished scene — no delete icon should be visible.
4. Trigger a trailing-user-message scenario (YAML edit): delete icon should appear and only remove the user message.

## Dependencies

061
