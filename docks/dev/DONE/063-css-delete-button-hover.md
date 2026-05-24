# Task 063: CSS Hover Styles for Delete Button

**Feature:** Delete message — UI layer
**Status:** TODO

## Description

Add CSS rules to `index.css` so the delete icon button inside a message bubble is hidden by default and revealed on hover. Uses the existing CSS variable palette (`--accent`, `--border`, `--text`, etc.). This keeps the chat uncluttered while making delete actions discoverable on hover, matching the same pattern used for the edit button.

## Scope

What IS included:
- `.message-bubble .delete-btn` — hidden by default (`opacity: 0`)
- `.message-bubble:hover .delete-btn` — made visible (`opacity: 1`)
- Button appearance: transparent background, `--accent` icon color (or a danger-tinted variant using existing variables), no border, `cursor: pointer`
- Smooth opacity transition (e.g. `transition: opacity 0.15s`)
- Positioning consistent with the edit button (if both exist on the same bubble, they should not overlap)

What is NOT included (deferred):
- Edit button styles — already covered by task 059
- Any style changes to non-button message bubble elements

## Deliverable

New CSS rules added to `frontend/src/index.css`.

```
frontend/src/index.css
```

## Acceptance Criteria

- [ ] Delete button is not visible when the cursor is not over the message bubble
- [ ] Delete button becomes visible when hovering the message bubble
- [ ] Button uses existing CSS variable colours (no hardcoded hex values)
- [ ] Delete button does not overlap the edit button when both are rendered on the same bubble
- [ ] No existing styles are broken

## Test Notes

Manual: hover the last user message bubble in a non-finished scene and verify the delete icon fades in. Move the cursor away — icon fades out. If the edit feature is also implemented (task 059), both icons should be visible on hover without overlapping.

## Dependencies

060, 059
