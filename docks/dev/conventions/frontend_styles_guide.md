# Frontend Styles Guide

Single reference for anyone (human or AI) adding or modifying frontend components.
Follow these rules so the app stays visually consistent and the codebase stays maintainable.

---

## 1. Token Reference

All design values live as CSS custom properties in `frontend/src/index.css` `:root`.
**Never write raw hex colors, raw pixel sizes, or raw font names in component code.** Always reference a token.

### Colors

| Token | Light value | Dark value | Intent |
|---|---|---|---|
| `--text` | `#6b6375` | `#9ca3af` | Default body text |
| `--text-h` | `#08060d` | `#f3f4f6` | Headings and high-emphasis text |
| `--bg` | `#fff` | `#16171d` | Page / component background |
| `--border` | `#e5e4e7` | `#2e303a` | Borders, dividers, subtle outlines |
| `--code-bg` | `#f4f3ec` | `#1f2028` | Code blocks; also used for neutral card backgrounds |
| `--accent` | `#aa3bff` | `#c084fc` | Brand accent — interactive labels, icons, badges |
| `--accent-bg` | `rgba(170,59,255,0.10)` | `rgba(192,132,252,0.15)` | Accent tinted surface (hover state, selected items, choice buttons) |
| `--accent-border` | `rgba(170,59,255,0.50)` | `rgba(192,132,252,0.50)` | Accent tinted border |
| `--error` | `#dc2626` | `#f87171` | Validation and error messages |

### Typography

| Token | Value | Intent |
|---|---|---|
| `--sans` | `system-ui, 'Segoe UI', Roboto, sans-serif` | Body and UI text |
| `--heading` | same as `--sans` | Heading elements (`h1`, `h2`) |
| `--mono` | `ui-monospace, Consolas, monospace` | Code, technical strings |

### Spacing

| Token | Value | Use for |
|---|---|---|
| `--space-xs` | `4px` | Tight internal gaps (icon rows, badge padding) |
| `--space-sm` | `8px` | Default padding inside controls; small gaps |
| `--space-md` | `12px` | Card padding; grid gaps |
| `--space-lg` | `16px` | Section padding; larger gaps |
| `--space-xl` | `24px` | Modal padding; page-level spacing |

### Border radius

| Token | Value | Use for |
|---|---|---|
| `--radius-sm` | `4px` | Inputs, buttons, badges, code blocks |
| `--radius-md` | `8px` | Cards, modals, message bubbles |

---

## 2. Decision Table — Where Do Styles Live?

Use this table to decide where to put every style you write:

| Situation | Where to put it | Example |
|---|---|---|
| Design token (color, size, font) | CSS variable in `index.css` `:root` | `--accent: #aa3bff` |
| Static structural style (layout, spacing, color that never changes at runtime) | CSS class in `index.css` | `.modal-panel { padding: var(--space-xl); }` |
| Value computed from props or state at runtime | Inline `style={{}}` on the element | `style={{ alignItems: isUser ? 'flex-end' : 'flex-start' }}` |
| JS style object reused by ≥ 2 components | Named export in `src/styles.js` | `export const inputBase = { ... }` |

**Rules:**
1. No raw values in component code — every color, size, and font must reference a CSS variable token.
2. Prefer CSS classes over inline styles — inline `style={{}}` is only for genuinely dynamic values.
3. Do not duplicate style objects across components — move shared objects to `styles.js`.
4. Do not introduce CSS Modules, styled-components, Tailwind, or any new styling tooling — the project uses plain CSS + the above four layers only.

---

## 3. Icons

Use a single shared source of truth for SVG icons in [frontend/src/components/icons.jsx](frontend/src/components/icons.jsx).

- Icons should be implemented as React components, not inline SVG markup inside components.
- Prefer icons from Heroicons: https://heroicons.com/
- Use the same stroke color and sizing pattern across the app: `stroke="currentColor"`, `width/height` controlled by the component or a shared class.
- Keep icon usage semantic: buttons should expose an accessible label via `aria-label` or `title` even when the icon is visual-only.

### Icon conventions

- Edit actions: use the edit icon component.
- Regenerate / refresh actions: use the refresh icon component.
- Delete actions: use the delete icon component.
- Step-back / previous-step actions: use the step-back icon component.

## 4. Component Anatomy Examples

### 4a. Card component — `StepItem`

`StepItem` renders a history step as a neutral card with an inline-edit mode.

```jsx
// Container: CSS class handles all static layout.
// The "step-item" class is defined in index.css.
<div className="step-item">

  {editing ? (
    <>
      {/* Inline-edit textarea: shared style object from styles.js.
          Used identically in MessageItem → lives in styles.js, not inline. */}
      <textarea style={inlineEditTextarea} />

      {/* Action row: inline only because it could vary per edit mode,
          but a CSS class would also be fine here since it's static. */}
      <div style={{ display: 'flex', gap: 'var(--space-sm)', marginTop: 'var(--space-sm)' }}>
        <button>Save</button>
        <button>Cancel</button>
      </div>
    </>
  ) : (
    // Content row: inline because the layout never needs to be
    // shared — one-off flex row.
    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: 'var(--space-sm)' }}>
      <p style={{ margin: 0, flex: 1 }}>{step.text}</p>
    </div>
  )}

</div>
```

**`index.css` class for this card:**
```css
/* Static structure: background, border, radius, spacing. */
/* No raw values — all tokens. */
.step-item {
  margin: var(--space-md) 0;
  padding: var(--space-md);
  border-radius: var(--radius-md);
  background: var(--code-bg);   /* neutral surface, not accent */
  border: 1px solid var(--border);
}
```

**`styles.js` constant used here:**
```js
// Shared between MessageItem and StepItem — kept in styles.js.
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

---

### 4b. Form input — `FinishModal` / `BulletTextarea`

`inputBase` in `styles.js` defines the visual appearance of every textarea or text input in the app. Import and spread it; add only the one-off overrides inline.

```jsx
import { inputBase } from '../styles'

// Good: spread the shared base, add a single override inline.
<BulletTextarea
  style={{ ...inputBase, resize: 'vertical' }}
/>

// Also good: a standalone <textarea> in a form.
<textarea style={{ ...inputBase, minHeight: '80px' }} />
```

**`styles.js` constant:**
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
```

**Do not** redefine input appearance inline in a component — if you need a new shared variation, add a new export to `styles.js`.

---

### 4c. Modal — `FinishModal`

The overlay and panel structure are CSS classes. Only values that are dynamic (none in this case) would be inline.

```jsx
// Both classes defined in index.css — no inline styles on these containers.
<div className="modal-overlay">
  <div className="modal-panel">
    <h3 style={{ margin: 0, color: 'var(--text-h)' }}>Finish Scene</h3>

    {/* Error message: always use --error token; never 'red'. */}
    {error && (
      <p style={{ margin: 0, color: 'var(--error)', fontSize: '14px' }}>
        {error}
      </p>
    )}

    {/* Button row: inline because it's a one-off layout in this component. */}
    <div style={{ display: 'flex', gap: 'var(--space-sm)', justifyContent: 'flex-end' }}>
      <button>Cancel</button>
      <button>Submit</button>
    </div>
  </div>
</div>
```

**`index.css` classes for this modal:**
```css
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.4);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-panel {
  background: var(--bg);
  border: 1px solid var(--border);
  border-radius: var(--radius-md);
  padding: var(--space-xl);
  width: 576px;
  max-width: 90vw;
  display: flex;
  flex-direction: column;
  gap: var(--space-lg);
}
```

---

## 4. ChoicesGrid vs `.clickable` — Intentional Visual Distinction

The app has two "pick one item from a list" patterns that look different on purpose:

### `.clickable` (StoryList, SceneList)

```css
.clickable {
  cursor: pointer;
}
.clickable:hover {
  color: var(--accent);
  background: var(--accent-bg);
}
```

Used for **navigation items** — story titles, scene titles. These start visually neutral (plain text on `--bg`) and only reveal the accent color on hover. The accent is a subtle affordance: "this is clickable." The user is browsing, not committing to an action.

### ChoicesGrid buttons

```jsx
<button style={{
  background: 'var(--accent-bg)',
  border: '1px solid var(--accent-border)',
  // ...
}}>
  {choice.action}
</button>
```

Used for **gameplay choices** — the 2×2 grid of story actions. These are rendered in `--accent-bg` with `--accent-border` **at rest**, not just on hover. The persistent accent weight is intentional: the player must choose, and the UI should make the options visually prominent at all times. The extra visual weight signals "this is the primary interaction right now."

### Rule

Do not align these two patterns. Keep the distinction:
- Navigation / browsable items → `.clickable` (neutral at rest, accent on hover)
- Forced-choice gameplay items → explicit `accent-bg` + `accent-border` on the button itself (accent at rest)

If you add a new "pick one" UI, ask: is the user browsing (use `.clickable`) or being prompted to make a required decision (use accent-at-rest button styles)?
