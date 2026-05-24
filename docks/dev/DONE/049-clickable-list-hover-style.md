# Task 049: Clickable List Item Hover Style

**Feature:** On hover cursor — interactive affordance for story and scene list items
**Status:** TODO

## Description

`StoryList` and `SceneList` render `<li>` elements with `onClick` handlers but no CSS to signal interactivity. Users have no visual affordance that the items are clickable. Add a `.clickable` utility class to `index.css` and apply it to the `<li>` elements in both components so the cursor changes to a pointer and the item highlights on hover.

## Scope

What IS included:
- `frontend/src/index.css` — add `.clickable` rule with `cursor: pointer`, hover text-color change, and optional background highlight using existing CSS variables
- `frontend/src/components/StoryList.jsx` — add `className="clickable"` to the `<li>` element
- `frontend/src/components/SceneList.jsx` — add `className="clickable"` to the `<li>` element

What is NOT included (deferred):
- Different cursor/color for `finished` scenes (out of scope for this fix)
- Styling bare `li` globally (must not affect `MessageList` or other non-clickable lists)
- Frontend component tests / visual regression tests

## Deliverable

Three file edits producing a working hover affordance:

```
frontend/src/index.css           ← add .clickable rule
frontend/src/components/StoryList.jsx   ← add className="clickable" to <li>
frontend/src/components/SceneList.jsx   ← add className="clickable" to <li>
```

Suggested CSS rule:
```css
.clickable {
  cursor: pointer;
}
.clickable:hover {
  color: var(--accent);
  background: var(--accent-bg, transparent);
}
```

## Acceptance Criteria

- [ ] Hovering over a story title in `StoriesPage` changes the cursor to a pointer
- [ ] Hovering over a scene row in `StoryPage` changes the cursor to a pointer
- [ ] Both items visually highlight (color or background change) on hover
- [ ] No other list items (e.g. message bubbles in `MessageList`) are affected by the new rule
- [ ] No existing tests are broken

## Test Notes

Manual browser check:
1. Start the frontend (`npm run dev` in `frontend/`).
2. Navigate to the Stories page — hover each story title; cursor must be a pointer and the title must highlight.
3. Click a story to open its detail page — hover each scene row; same check.
4. Open a scene page and hover over message bubbles — cursor must remain default (not pointer).

## Dependencies

none
