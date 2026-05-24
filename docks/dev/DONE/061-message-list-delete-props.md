# Task 061: MessageList Delete Props

**Feature:** Delete message — UI layer
**Status:** TODO

## Description

Add `onDelete` and `disabled` props to `MessageList`. Compute the index of the last user message in the list and pass `onDelete` only to that `MessageItem`. All other items receive no `onDelete`. When `disabled` is true (scene finished or in-flight), no item receives `onDelete`.

## Scope

What IS included:
- `onDelete` prop: `(messageId) => void` — forwarded from `ScenePage`
- `disabled` prop: boolean — when `true`, no `MessageItem` receives `onDelete`
- Last-user-message detection: `const lastUserIdx = messages.map(m => m.role).lastIndexOf('user')`
- `onDelete` passed only to the `MessageItem` at `lastUserIdx` (and only when `!disabled`)
- All other `MessageItem`s receive no `onDelete`

What is NOT included (deferred):
- Identifying the "following assistant message" — that logic belongs in the `ScenePage` handler (task 062)
- Busy/in-flight state — shared `disabled` flag from task 062 covers this
- Tests

## Deliverable

Modified `frontend/src/components/MessageList.jsx` with `onDelete` and `disabled` props forwarded selectively.

```
frontend/src/components/MessageList.jsx
```

## Acceptance Criteria

- [ ] `MessageList` accepts `onDelete` and `disabled` props without errors
- [ ] When `disabled={false}`, the `MessageItem` at the last user message index receives `onDelete`
- [ ] No other `MessageItem` receives `onDelete`
- [ ] When `disabled={true}`, no `MessageItem` receives `onDelete`
- [ ] When there are no user messages (`lastUserIdx === -1`), no item receives `onDelete`
- [ ] Existing render output is unchanged when neither prop is passed (backward-compatible)

## Test Notes

Manual verification:
1. Open a non-finished scene with multiple exchanges. Only the last user message bubble should show a delete icon on hover.
2. Open a finished scene — no delete icon on any bubble.
3. A scene with only the entry-point assistant message (no user messages) — no delete icon.

## Dependencies

060
