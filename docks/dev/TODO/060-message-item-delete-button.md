# Task 060: MessageItem Delete Button

**Feature:** Delete message — UI layer
**Status:** TODO

## Description

Add an `onDelete` prop to `MessageItem`. When `onDelete` is provided (truthy), render a delete icon button on the message bubble (hidden by default, visible on hover via CSS). Clicking the button calls `onDelete(message.id)`.

## Scope

What IS included:
- `onDelete` prop: `(messageId) => void`
- Delete icon button (e.g. "✕" or trash icon) rendered when `onDelete` is truthy
- Button hidden by default; visible on `.message-bubble:hover` via CSS class `delete-btn` (see task 063)
- Clicking the button calls `onDelete(message.id)`
- No `onDelete` prop provided → no delete button rendered (backward-compatible default)

What is NOT included (deferred):
- Confirmation dialog before deletion
- Disabled-during-busy state wiring — that belongs in task 062
- CSS hover rules — task 063
- Tests

## Deliverable

Modified `frontend/src/components/MessageItem.jsx` with a conditional delete button.

```
frontend/src/components/MessageItem.jsx
```

## Acceptance Criteria

- [ ] Delete button renders on the bubble when `onDelete` is provided
- [ ] Delete button is absent when `onDelete` is not provided
- [ ] Clicking the delete button calls `onDelete(message.id)` with the correct id
- [ ] Button has the CSS class `delete-btn` so the hover rule in task 063 can target it
- [ ] Existing render output is unchanged when `onDelete` is not passed

## Test Notes

Manual verification:
1. Open a non-finished scene. Hover the last user message bubble — a delete icon should appear.
2. Click the icon — `onDelete` should be invoked (check via console log or network tab in later tasks).
3. Hover an assistant message or a non-last user message — no delete icon should appear (controlled by the caller, not this component).

## Dependencies

none
