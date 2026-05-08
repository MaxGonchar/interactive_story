# Task 021: MessageList Component

**Feature:** M3 — Frontend UI Pages (Mocked)
**Status:** TODO

## Description

Implement the `MessageList` presentational component. Accepts an array of messages and renders them in order using `MessageItem`.

## Scope

What IS included:
- `MessageList` component accepting `messages: [{ id, role, content }]` prop
- Renders a `MessageItem` for each message in order
- Empty state when `messages` is empty

What is NOT included (deferred):
- Auto-scroll behaviour (can be added in M6)
- Edit/delete actions (M6)

## Deliverable

`frontend/src/components/MessageList.jsx` — a functional React component.

```
frontend/src/components/MessageList.jsx
```

## Acceptance Criteria

- [ ] Renders one `MessageItem` per entry in `messages`
- [ ] Messages are rendered in the order provided (ascending by array index)
- [ ] Shows "No messages yet." when `messages` is empty or undefined
- [ ] Component is the default export

## Test Notes

Render with 3 messages alternating user/assistant roles; verify all three appear in the correct order.

## Dependencies

- 020 (MessageItem component)
