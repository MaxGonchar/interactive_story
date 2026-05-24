# Task 070: Forward Regenerate Props Through MessageList

**Feature:** Regenerate last assistant message
**Status:** TODO

## Description

Update `MessageList` to accept `onRegenerate` and `disabled` props, compute the index of the last assistant message, and pass `onRegenerate` only to the `MessageItem` at that index (and only when `!disabled`). All other `MessageItem`s receive no `onRegenerate` prop. Also skip passing `onRegenerate` if the last assistant message has no preceding user message (i.e. it is the first message at index 0) — in that case no button should appear.

## Scope

What IS included:
- `onRegenerate` and `disabled` props on `MessageList`
- Computation: `const lastAssistantIdx = messages.map(m => m.role).lastIndexOf('assistant')`
- Guard: do not pass `onRegenerate` if `lastAssistantIdx === 0` (entry-point message, no prior user message)
- `onRegenerate` forwarded only to the `MessageItem` at `lastAssistantIdx` when `!disabled && lastAssistantIdx > 0`

What is NOT included (deferred):
- Forwarding `onEdit` / `onDelete` props — handled in separate tasks 057 and 061
- ScenePage handler (task 071)

## Deliverable

Updated `frontend/src/components/MessageList.jsx`:

```
frontend/src/components/MessageList.jsx
```

## Acceptance Criteria

- [ ] `MessageList` accepts `onRegenerate` and `disabled` props
- [ ] Exactly one `MessageItem` receives `onRegenerate` — the last assistant message with index > 0
- [ ] No `MessageItem` receives `onRegenerate` when `disabled={true}`
- [ ] No `MessageItem` receives `onRegenerate` when the last assistant message is at index 0 (entry-point)
- [ ] All other `MessageItem` props (key, message) are unchanged
- [ ] Frontend builds without errors

## Test Notes

Manual: pass `onRegenerate={() => console.log('regen')}` and `disabled={false}` from ScenePage after task 071 and verify only the last assistant bubble shows the button.

## Dependencies

- 069 (MessageItem must accept `onRegenerate`)
