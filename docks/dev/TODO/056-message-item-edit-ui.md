# Task 056: MessageItem Inline Edit UI

**Feature:** Edit message — UI layer
**Status:** TODO

## Description

Add `onEdit` and `disabled` props to `MessageItem`. When the scene is active (`disabled` is false), render an edit icon button on the message bubble. Clicking it switches the bubble into inline edit mode: a `<textarea>` pre-filled with the current content, plus Save and Cancel buttons. Saving calls `onEdit(message.id, newContent)`; cancelling restores the original content.

## Scope

What IS included:
- `onEdit` prop: `(messageId, newContent) => void`
- `disabled` prop: boolean — when `true`, no edit button is rendered
- Local `editing` state (`useState(false)`) and `draft` state (`useState(message.content)`)
- Edit icon button (visible on hover via CSS class; see task 059)
- Inline `<textarea>` with `maxLength={4000}` pre-filled with `message.content`
- Save button: calls `onEdit(message.id, draft)`, exits edit mode
- Cancel button: resets `draft` to `message.content`, exits edit mode
- Save button disabled when `draft` is empty or unchanged
- No call to `onEdit` while the save is in flight (disable Save during async)

What is NOT included (deferred):
- Lifting edit state to `MessageList` or `ScenePage` (concurrent edit conflicts — post-MVP)
- Shared `busy` state integration — that wiring belongs in task 058
- CSS hover rules — task 059
- Tests

## Deliverable

Modified `frontend/src/components/MessageItem.jsx` with inline edit behaviour.

```
frontend/src/components/MessageItem.jsx
```

## Acceptance Criteria

- [ ] Edit icon button renders on the bubble when `disabled={false}` and is absent when `disabled={true}`
- [ ] Clicking the edit button replaces the `<p>` text with a `<textarea>` pre-filled with `message.content`
- [ ] The `<textarea>` enforces `maxLength={4000}`
- [ ] Clicking Save calls `onEdit(message.id, newContent)` with the edited text
- [ ] Clicking Cancel restores the original content and exits edit mode without calling `onEdit`
- [ ] Save button is disabled when `draft` is empty or equals the original `message.content`
- [ ] No `onEdit` prop provided → no edit button rendered (backward-compatible default)

## Test Notes

Manual verification:
1. Open a non-finished scene. Hover a message bubble — an edit icon should appear.
2. Click the icon — bubble switches to a textarea with pre-filled content.
3. Edit the text, click Save — bubble returns to display mode with updated content.
4. Click edit again, change text, click Cancel — bubble shows original content unchanged.
5. Open a finished scene — no edit icon should appear on any bubble.

## Dependencies

none
