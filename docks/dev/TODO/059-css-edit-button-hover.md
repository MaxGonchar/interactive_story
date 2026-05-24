# Task 059: CSS Hover Styles for Edit Button

**Feature:** Edit message — UI layer
**Status:** TODO

## Description

Add CSS rules to `index.css` so the edit icon button inside a message bubble is hidden by default and revealed on hover. Uses the existing CSS variable palette (`--accent`, `--border`, `--text`, etc.). This keeps the chat uncluttered while still making edit actions discoverable.

## Scope

What IS included:
- `.message-bubble .edit-btn` — hidden by default (`opacity: 0`, or `visibility: hidden`)
- `.message-bubble:hover .edit-btn` — made visible (`opacity: 1`)
- Button appearance: transparent background, `--accent` icon color, no border, `cursor: pointer`
- Smooth transition on opacity (e.g. `transition: opacity 0.15s`)

What is NOT included (deferred):
- Edit textarea / Save / Cancel button styles (those can use existing button/input defaults or minimal inline styles in the component)
- Styles for the delete button (separate feature)

## Deliverable

New CSS rules added to `frontend/src/index.css`.

```
frontend/src/index.css
```

## Acceptance Criteria

- [ ] Edit button is not visible when the user's cursor is not over the message bubble
- [ ] Edit button becomes visible when hovering the message bubble
- [ ] Button uses existing CSS variable colours (no hardcoded hex values)
- [ ] No existing styles are broken

## Test Notes

Manual: hover a message bubble in a non-finished scene and verify the edit icon fades in. Move the cursor away — icon fades out.

## Dependencies

056
