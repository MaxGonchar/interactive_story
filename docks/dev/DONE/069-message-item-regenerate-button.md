# Task 069: Add Regenerate Button to MessageItem

**Feature:** Regenerate last assistant message
**Status:** TODO

## Description

Add an `onRegenerate` prop to `MessageItem`. When the prop is provided (non-null), render a small regenerate icon button (↺) on the assistant message bubble. Clicking the button calls `onRegenerate()`. The button is hidden by default and revealed on hover via a CSS class (`.msg-action-btn`) defined in task 072. No inline editing state is required — this is a single-click action.

## Scope

What IS included:
- `onRegenerate` prop accepted by `MessageItem`
- Regenerate button rendered only when `onRegenerate` is truthy
- Button calls `onRegenerate()` on click
- Button styled with `className="msg-action-btn"` (CSS defined in task 072)
- Button placed inside or adjacent to the bubble `<div>`

What is NOT included (deferred):
- CSS hover rule (task 072)
- `MessageList` forwarding (task 070)
- `ScenePage` handler (task 071)
- Edit or delete buttons — separate tasks already exist

## Deliverable

Updated `frontend/src/components/MessageItem.jsx` accepting the `onRegenerate` prop and conditionally rendering a button:

```
frontend/src/components/MessageItem.jsx
```

## Acceptance Criteria

- [ ] `MessageItem` renders a regenerate button when `onRegenerate` is provided
- [ ] No button rendered when `onRegenerate` is `null` or `undefined`
- [ ] Clicking the button calls `onRegenerate()` exactly once
- [ ] Existing rendering (label, bubble, content) is unchanged
- [ ] Frontend app builds without errors

## Test Notes

Manual: temporarily pass `onRegenerate={() => console.log('regen')}` to a `MessageItem` in ScenePage and verify the button appears and logs on click. Remove the temporary prop after task 071 is done.

## Dependencies

- 072 should be done alongside or immediately after to make the button visible (but not a hard blocker for the component to function)
