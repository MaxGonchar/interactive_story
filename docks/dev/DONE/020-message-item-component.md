# Task 020: MessageItem Component

**Feature:** M3 — Frontend UI Pages (Mocked)
**Status:** TODO

## Description

Implement the `MessageItem` presentational component. Renders a single chat message with role label and content text.

## Scope

What IS included:
- `MessageItem` component accepting `message: { id, role, content }` prop
- Visually distinguishes `role: "user"` from `role: "assistant"` (e.g. alignment or label)
- Renders message content text

What is NOT included (deferred):
- Edit/delete controls (M6 feature, out of M3 scope)
- Markdown rendering

## Deliverable

`frontend/src/components/MessageItem.jsx` — a functional React component rendering one message bubble.

```
frontend/src/components/MessageItem.jsx
```

## Acceptance Criteria

- [ ] Renders message `content`
- [ ] Shows a role label ("You" for user, "Narrator" or "Assistant" for assistant)
- [ ] User and assistant messages are visually distinguishable (different alignment or background)
- [ ] Component is the default export

## Test Notes

Render with `message={id:1, role:"user", content:"Hello"}` and `message={id:2, role:"assistant", content:"Welcome."}` side-by-side; verify visual distinction.

## Dependencies

None
