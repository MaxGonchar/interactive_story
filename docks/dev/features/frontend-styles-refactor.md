# Feature: Frontend Styles Refactor

**Status**: Draft  
**Date**: 2026-07-18

## Summary

The frontend has accumulated styling inconsistencies across components: duplicate inline style objects, missing CSS tokens, magic hardcoded values, one confirmed CSS scoping bug, and no shared convention for deciding where styles live. This refactor establishes a clear, maintainable styling convention and brings the UI into a consistent state through three sequential phases: visual normalization, structural cleanup, and documentation.

## Value

- Eliminates visual inconsistencies that make the app feel unpolished
- Removes duplicated style code that will diverge further as components grow
- Fixes one real CSS bug (action buttons always visible in `StepItem`)
- Establishes a shared convention so future AI-assisted and manual work stays consistent
- Success: every "same kind of thing" looks identical, no magic values in component code, one place to change a token

## Scope

**In scope for first iteration (all three phases)**
- Define missing CSS tokens (`--error`, `--space-*`, `--radius-*`)
- Fix `msg-action-btn` CSS bug
- Normalize all error text, inline-edit textarea, Save/Cancel button pair
- Add missing button base style
- Add `story-type-badge` CSS class
- Add layout to `SceneHeader`
- Create `src/styles.js` with shared JS-side style constants
- Move render-function style objects to module level or `styles.js`
- Extract `FinishModal` overlay/panel to CSS classes
- Add `ul`/`li` reset for `StoryList`
- Align `ChoicesGrid` values with spacing tokens
- Align `MessageComposer` textarea with input token
- Write `frontend_styles_guide.md`
- Update `copilot-instructions.md` with frontend styles rules

**Out of scope**
- CSS Modules, styled-components, Tailwind, or any new styling library
- Visual redesign — only normalize what already exists
- Touching backend or API layer
- Animation or transition improvements

## User Flow

This is an internal refactor — no user-visible flow change. The goal is that the app looks identical before and after Phase 1, and has cleaner code after Phases 2 and 3.

## API Changes

None.

## Data Changes

None.

## Issues Found

All issues that drive the task list below.

### Confirmed bugs

| # | Issue | Location |
|---|---|---|
| B1 | `msg-action-btn` CSS selector is `.message-bubble .msg-action-btn` — scoped to `.message-bubble` parent. `StepItem` uses the class without that parent, so its edit/return buttons are always visible, never hide/reveal on hover. | `index.css`, `StepItem.jsx` |

### Visual inconsistencies

| # | What | Where | Problem |
|---|---|---|---|
| V1 | Error text | `FinishModal` (×2), `NewScenePage` (×1) `ChoiceDrivenStoryPage` (×1) | `color: 'red'` hardcoded. Font size `14px` in some, implicit in others. |
| V2 | Inline-edit textarea | `MessageItem`, `StepItem` | Identical 10-property style objects duplicated in two components. |
| V3 | Save/Cancel button spacing | `MessageItem` (no spacing), `StepItem` (`marginLeft: 8px` on Cancel) | Same pattern, different spacing. |
| V4 | Textarea appearance | `MessageComposer`, `NewScenePage` (`inputBaseStyle`), `FinishModal` (`BulletTextarea`) | Three independent textarea definitions; `MessageComposer` applies no font or color tokens, using browser defaults. |
| V5 | `story-type-badge` | `StoryList.jsx` | Class referenced but never defined in `index.css` — renders unstyled. |
| V6 | `SceneHeader` | `SceneHeader.jsx` | No padding, no layout — renders differently from all other page section headers. |
| V7 | `ChoicesGrid` buttons vs `.clickable` list items | `ChoicesGrid.jsx`, `StoryList.jsx` | Both are "pick one of these" UI but styled differently. Choice buttons are accent-styled inline; list items use the `.clickable` CSS class. These serve different interaction models (permanent list vs one-time pick), so they **should stay visually distinct** — but `ChoicesGrid` should still use spacing tokens instead of magic values. |
| V8 | No base button style | All components | Buttons use browser defaults everywhere. No `.btn` base or `button { }` reset defined. |
| V9 | `StoryList` `<ul>`/`<li>` unstyled | `StoryList.jsx` | Browser default bullet points and left padding not reset. |
| V10 | `SceneActions` textarea | `SceneActions.jsx` | Bare `<textarea>` with no styling whatsoever. |

### Code quality issues

| # | What | Where | Problem |
|---|---|---|---|
| C1 | `inputBaseStyle`, `fieldStyle`, `labelStyle`, `errorStyle` defined inside render | `NewScenePage.jsx` | New object instances created on every render; not reusable. |
| C2 | `FinishModal` overlay and panel as inline objects | `FinishModal.jsx` | 10+ property style objects inline in JSX; can be CSS classes. |
| C3 | `MessageItem` `wrapperStyle`, `labelStyle`, `bubbleStyle` defined inside render | `MessageItem.jsx` | `labelStyle` and the static parts of `bubbleStyle` can be extracted; only the `isUser`-conditional values need to stay inline. |
| C4 | `ChoicesGrid` all magic spacing values | `ChoicesGrid.jsx` | `marginTop: '16px'`, `gap: '12px'`, `padding: '12px'` — none reference tokens. |

## Frontend Changes

### Phase 1 — Visual normalization

**Goal**: consistent look without restructuring how styles are managed yet.

Tasks:

1. **Fix `msg-action-btn` CSS bug (B1)**  
   Change selector from `.message-bubble .msg-action-btn` to `.msg-action-btn` (or add a second rule for `StepItem`'s wrapper). Verify hover show/hide works in both `MessageItem` and `StepItem`.

2. **Add `--error` token + normalize error `<p>` (V1)**  
   Add to `index.css` `:root`: `--error: #dc2626;`  
   Add to dark mode block: `--error: #f87171;`  
   In all 4 error `<p>` elements: `color: var(--error)`, `fontSize: '14px'`, `margin: 0`.

3. **Add base button style (V8)**  
   Add a `button { }` rule to `index.css` that sets `font: inherit`, `cursor: pointer`, and a minimal consistent appearance (border, padding, border-radius using tokens once Phase 2 tokens exist — use raw values in Phase 1).

4. **Define `.story-type-badge` (V5)**  
   Add to `index.css`: small font size, accent color, subtle border or background, some left margin.

5. **Add layout to `SceneHeader` (V6)**  
   Add padding, flex row, align-items, and a visual separator (border-bottom or margin) so it matches other section headers.

6. **Reset `StoryList` `<ul>`/`<li>` (V9)**  
   Either add a scoped CSS class (`.story-list`) with `list-style: none; padding: 0; margin: 0` and matching `li` styles, or move to a `<div>`-based layout. Make `li`/item display consistent with how other list-style UIs look.

7. **Normalize Save/Cancel button spacing (V3)**  
   Pick one pattern: a flex `gap` on the wrapper `<div>`. Apply the same pattern to both `MessageItem` and `StepItem`.

8. **Style `SceneActions` textarea (V10)**  
   Apply the same base input appearance as other textareas (font, border, padding, border-radius, color, background).

---

### Phase 2 — Style convention refactor

**Goal**: restructure where styles live without changing visual output.

#### Convention rules

1. **CSS variables** — single source of truth for design tokens. No raw color or spacing values in component code.
2. **CSS classes** (in `index.css`) — all static structural styles: layout, spacing, colors that don't depend on component state or props.
3. **Inline `style={{}}`** — only for values computed from props or state (e.g. `isUser ? 'flex-end' : 'flex-start'`).
4. **`src/styles.js`** — shared JS-side style constants that multiple components need or that must be composed with spread (`...inputBase`).
5. No CSS Modules, no styled-components.

#### New tokens to add to `index.css` `:root`

```css
--space-xs:   4px;
--space-sm:   8px;
--space-md:   12px;
--space-lg:   16px;
--space-xl:   24px;
--radius-sm:  4px;
--radius-md:  8px;
```

These have no dark-mode variants — spacing and radius are theme-neutral.

#### New file: `src/styles.js`

```js
export const inputBase = {
  fontFamily: 'var(--sans)',
  fontSize: '16px',
  border: '1px solid var(--border)',
  borderRadius: 'var(--radius-sm)',
  padding: 'var(--space-sm)',
  color: 'var(--text)',
  background: 'var(--bg)',
}

export const inlineEditTextarea = {
  width: '100%',
  boxSizing: 'border-box',
  background: 'transparent',
  border: 'none',
  borderBottom: '1px solid var(--border)',
  outline: 'none',
  resize: 'none',
  overflow: 'hidden',
  font: 'inherit',
  color: 'inherit',
  padding: '0',
}
```

Tasks:

9. **Add spacing + radius tokens to `index.css` (new tokens)**

10. **Create `src/styles.js` with `inputBase` and `inlineEditTextarea`**

11. **Move `NewScenePage` style consts to module level (C1)**  
    Move `inputBaseStyle`, `fieldStyle`, `labelStyle`, `errorStyle` out of the render function. Replace `inputBaseStyle` with import of `inputBase` from `styles.js` (or alias it locally).

12. **Replace duplicated `inlineEditTextarea` styles (V2, C)**  
    In `MessageItem` and `StepItem`, replace the 10-property inline textarea object with `style={inlineEditTextarea}` imported from `styles.js`.

13. **Extract `FinishModal` overlay + panel to CSS classes (C2)**  
    Add `.modal-overlay` and `.modal-panel` to `index.css`. Keep only dynamic values inline in `FinishModal`.

14. **Extract `MessageItem` static wrapper/bubble styles to CSS classes (C3)**  
    Add `.message-wrapper` (static flex column layout) and `.message-bubble--user` / `.message-bubble--narrator` classes. Keep only `alignItems: isUser ? 'flex-end' : 'flex-start'` and the conditional border/background as inline.

15. **Replace hardcoded spacing in `ChoicesGrid` with token references (C4)**  
    Replace `16px`, `12px`, `8px` with `var(--space-lg)`, `var(--space-md)`, `var(--space-sm)`.

16. **Replace `inputBaseStyle` spread in `FinishModal` BulletTextarea**  
    Use `style={{ ...inputBase, resize: 'vertical' }}` from `styles.js`.

---

### Phase 3 — Document and AI harness

**Goal**: write a style guide and wire it into the Copilot instructions so future work follows the convention.

Tasks:

17. **Write `docks/dev/frontend_styles_guide.md`**  
    Contents:
    - Full token reference (all `--*` variables with their intent)
    - The 4-rule decision table (CSS class vs inline vs `styles.js` vs CSS variable)
    - Component anatomy examples: a card (`StepItem`), a form input, a modal

18. **Update `.github/copilot-instructions.md` with a Frontend Styles section**  
    Rules:
    - No raw color or spacing values — reference a `--token`
    - Static styles go in `index.css` as a class
    - Dynamic styles (prop/state-dependent) go inline
    - Shared JS-side constants go in `src/styles.js`
    - Pointer to `frontend_styles_guide.md`

## Open Questions

- Should `ChoicesGrid` buttons eventually converge with `.clickable` list items, or stay intentionally distinct? Current call: keep them distinct (different interaction model) but document the decision in the style guide.
- Should `button { }` base style apply globally or use a `.btn` class? Global reset is simpler for this codebase size.
- `SceneActions` appears to have dead code (the textarea with `summaryText` state is never used — `onFinish` is called with `summaryText.trim()` but the page uses `FinishModal` for the finish flow). Confirm before styling `SceneActions` in detail.

## Risks

- Phase 1 CSS changes (`.msg-action-btn` selector, `button {}` base) affect all components globally — test all pages after applying.
- `BulletTextarea` uses `...rest` spread to pass `style` from callers. The `inputBase` refactor must keep this working correctly — `style` from the caller must still override BulletTextarea defaults.
- Phase 2 inline→class extraction in `MessageItem` requires care: the `isUser` conditional must remain inline; only the static parts move to CSS.
