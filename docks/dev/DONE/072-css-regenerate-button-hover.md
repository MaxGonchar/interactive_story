# Task 072: CSS Hover Style for Regenerate Button

**Feature:** Regenerate last assistant message
**Status:** TODO

## Description

Add CSS rules to `frontend/src/index.css` so the regenerate button (`.msg-action-btn` inside a `.message-bubble`) is hidden by default and revealed on hover, keeping the chat uncluttered. The rule reuses existing CSS variables (`--accent`, `--border`, `--text`). This is the same pattern as the planned edit/delete button hover rules (tasks 059, 063).

## Scope

What IS included:
- `.message-bubble` wrapper gets `position: relative` so action buttons can be positioned absolutely
- `.msg-action-btn` default state: hidden (`opacity: 0`) or `display: none`
- `.message-bubble:hover .msg-action-btn`: visible, `cursor: pointer`
- Button inherits or is styled with `--accent` / `--text` color variables
- Rule is scoped to `.msg-action-btn` inside `.message-bubble` — does not affect other buttons in the app

What is NOT included (deferred):
- Adding the `message-bubble` or `msg-action-btn` classes to JSX — that is part of the component tasks (069 for regenerate, 056 for edit, 060 for delete). This task adds only the CSS.

## Deliverable

New CSS rules appended to `frontend/src/index.css`:

```
frontend/src/index.css
```

## Acceptance Criteria

- [ ] `.message-bubble:hover .msg-action-btn` is defined in `index.css`
- [ ] Regenerate button is not visible on a message bubble at rest
- [ ] Regenerate button becomes visible when the user hovers over the bubble
- [ ] Rule does not affect any buttons outside `.message-bubble`
- [ ] Frontend builds and renders without errors

## Test Notes

Manual: hover over a message bubble in the scene page; verify the regenerate button (↺) appears. Move the cursor away; verify it disappears.

## Dependencies

- 069 (MessageItem must apply `className="message-bubble"` to the wrapper and `className="msg-action-btn"` to the button for the CSS to take effect)
