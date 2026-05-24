# Task 057: MessageList Forward Edit Props

**Feature:** Edit message — UI layer
**Status:** TODO

## Description

Add `onEdit` and `disabled` props to `MessageList` and forward them to every `<MessageItem>` it renders. This is the required intermediary wiring between `ScenePage` (which owns the handler) and `MessageItem` (which renders the edit button).

## Scope

What IS included:
- `onEdit` prop: `(messageId, newContent) => void` — forwarded to each `<MessageItem>`
- `disabled` prop: boolean — forwarded to each `<MessageItem>`
- Both props optional with no default (backward-compatible)

What is NOT included (deferred):
- Any logic for selecting which message to make editable — all messages receive `onEdit` equally (deletion scoping belongs to the delete feature)
- Tests

## Deliverable

Modified `frontend/src/components/MessageList.jsx` that accepts and forwards `onEdit` and `disabled`.

```
frontend/src/components/MessageList.jsx
```

## Acceptance Criteria

- [ ] `MessageList` accepts `onEdit` and `disabled` props
- [ ] Every `<MessageItem>` rendered by `MessageList` receives `onEdit` and `disabled`
- [ ] When neither prop is supplied, existing render behaviour is unchanged
- [ ] No other logic changes

## Test Notes

Manual: opening a scene page should still render all messages without errors after this change (smoke test via browser console).

## Dependencies

056
