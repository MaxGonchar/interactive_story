# Frontend Styles — 3-Phase Plan

## Phase 1 — Visual Normalization

Goal: find UI elements that _should_ look the same but were styled differently because there was no convention. Fix the visual output without restructuring how styles are managed yet. After this phase, the app has a consistent look and is ready to refactor.

### Inconsistencies found

| # | What | Where | Problem |
|---|---|---|---|
| 1 | Error text | `FinishModal` (×2), `NewScenePage` (×1), `ChoiceDrivenStoryPage` (×1) | Some use `color: 'red'`, one uses `color: 'var(--error, red)'`. Font size and margin vary. |
| 2 | Inline-edit textarea | `MessageItem` and `StepItem` | Identical styles duplicated in two places. |
| 3 | Save/Cancel button pair | `MessageItem` (no gap) vs `StepItem` (`marginLeft: 8px` on Cancel) | Same pattern, different spacing. |
| 4 | Editable card container | `StepItem` (`padding: 12px`, `bg: code-bg`) vs `MessageItem` bubble (`padding: 8px 12px`, `bg: accent-bg` or `code-bg`) | Intentionally different bubbles are fine, but the step card vs assistant message card should be consciously distinct, not accidentally different. |
| 5 | Textarea inputs | `MessageComposer` (`padding: 8px`, `minHeight: 80px`) vs `NewScenePage` (`inputBaseStyle`) vs `FinishModal` BulletTextarea (`padding: 8px`, `fontSize: 16px`, `borderRadius: 4px`) | Three places define textarea appearance independently. |
| 6 | `story-type-badge` | `StoryList.jsx` uses `className="story-type-badge"` | Class is never defined in `index.css` — likely renders as plain text with no styling. |
| 7 | `SceneHeader` | No styling at all (no padding, no layout) | Renders differently than all other page section headers. |
| 8 | Selectable items | `StoryList` / `SceneList` use `.clickable` CSS class (hover: accent bg) vs `ChoicesGrid` uses inline accent button styles | Both are "pick one of these" UI but visually diverge. Consider aligning or consciously differentiating. |

### Tasks for Phase 1

- [ ] Define `--error` token in `index.css` dark/light, replace all `'red'` occurrences
- [ ] Normalize error `<p>` style: same `fontSize`, `margin`, `color` in all 4 places
- [ ] Normalize Save/Cancel spacing: pick one pattern (`gap` on wrapper or `marginLeft`) and apply both to `MessageItem` and `StepItem`
- [ ] Define `.story-type-badge` in `index.css` (it's referenced but never defined)
- [ ] Add minimal layout to `SceneHeader` (padding, alignment)
- [ ] Review `ChoicesGrid` buttons vs `.clickable` list items — decide if they should converge or stay intentionally different (document the decision)

---

## Phase 2 — Style Convention Refactor

Goal: restructure how styles are written without changing visual output. After Phase 1, the app is visually consistent — Phase 2 reorganizes that into a maintainable system.

### Convention rules

1. **CSS variables** are the single source of truth for design tokens.
2. **CSS classes** (in `index.css`) for all static structural styles — layout, spacing, colors that don't depend on component state or props.
3. **Inline `style={{}}`** only for values that are dynamically computed from props or state (e.g. `isUser ? 'flex-end' : 'flex-start'`).
4. **`src/styles.js`** for JS-side style constants that must be shared across components (the `inputBaseStyle` pattern, extended).
5. No CSS Modules, no styled-components — just plain CSS + the above rules.

### New tokens to add to `index.css` `:root`

```css
--space-xs:  4px;
--space-sm:  8px;
--space-md:  12px;
--space-lg:  16px;
--space-xl:  24px;
--radius-sm: 4px;
--radius-md: 8px;
--error:     #dc2626;
```

Add to dark mode block:
```css
--error: #f87171;
```

### New file: `src/styles.js`

Shared JS-side style constants (for patterns that need spreading or JS composition):

```js
export const inputBase = { ... }       // shared textarea/input appearance
export const inlineEditTextarea = { ... } // shared between MessageItem and StepItem
export const cardBase = { ... }        // base for card containers
```

### Tasks for Phase 2

- [ ] Add spacing + radius + error tokens to `index.css`
- [ ] Create `src/styles.js` with `inputBase`, `inlineEditTextarea`, `cardBase`
- [ ] Replace `inputBaseStyle` in `NewScenePage` with import from `styles.js`
- [ ] Replace duplicated inline-edit textarea styles in `MessageItem` and `StepItem` with shared constant
- [ ] Extract `FinishModal` overlay + panel inline styles → `.modal-overlay` / `.modal-panel` CSS classes
- [ ] Extract `MessageItem` wrapper/bubble inline styles → CSS classes (keeping only the dynamic `isUser` conditionals inline)
- [ ] Replace hardcoded spacing values with CSS variable references (`'var(--space-sm)'` etc.)

---

## Phase 3 — Document & AI Harness

Goal: write a short style guide and wire it into the copilot instructions so future AI-assisted work follows the convention.

### Style guide doc

Create `docks/dev/frontend_styles_guide.md` with:
- Token reference (all `--*` variables with their intent)
- The 3-rule decision table (CSS class vs inline vs styles.js)
- Component anatomy examples (a card, a form input, a modal)

### AI harness

Update `.github/copilot-instructions.md`:
- Add a "Frontend Styles" section pointing to the guide
- Add rules: no magic color/spacing values, reference tokens, follow the 3-rule table

### Tasks for Phase 3

- [ ] Write `docks/dev/frontend_styles_guide.md`
- [ ] Update `.github/copilot-instructions.md` with frontend styles section
