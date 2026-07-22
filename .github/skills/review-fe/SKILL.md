---
name: review-fe
description: "Review frontend React code quality. Use when: reviewing frontend code, checking code quality, scanning for anti-patterns, checking style convention violations, checking component responsibility, checking test coverage gaps, auditing React practices, code review, quality report."
argument-hint: "Optional: specific component, page, or path to review (e.g. 'components/MessageItem' or 'all'). Defaults to full frontend src."
---

# Frontend React Code Review

## Purpose

Scan the React frontend for quality issues across three dimensions:

1. **Style convention violations** — magic values, wrong inline style usage, missing CSS variable tokens
2. **React/component anti-patterns** — prop drilling, missing key props, side effects in render, large undecomposed components
3. **Test coverage gaps** — components or API modules with missing or insufficient RTL tests

No third-party tools. Pure code reading and reasoning.

At the end: discuss findings with the user, then produce a structured report file.

---

## Procedure

### Step 1 — Determine Scope

If the user specified a path, restrict the review to that module. Otherwise review the full `frontend/src/` tree.

Start by reading the convention docs — these define what is *expected*; violations are findings:

| Doc | What it defines |
|---|---|
| [fe-conventions.md](../implement-fe-task/fe-conventions.md) | Test tooling, file location, naming, what/what-not to test, mocking, factories |
| [frontend_styles_guide.md](../../../../docks/dev/frontend_styles_guide.md) | Styling rules — CSS variables, no magic values, static vs dynamic styles, `styles.js` |

### Step 2 — Collect Source Files

List all `.jsx` and `.js` files under the target scope. Group them by type:

| Type | Path pattern |
|---|---|
| Components | `frontend/src/components/*.jsx` |
| Pages | `frontend/src/pages/*.jsx` |
| API modules | `frontend/src/api/*.js` |
| Shared styles | `frontend/src/index.css`, `frontend/src/styles.js` |
| Test files | `*.test.jsx`, `*.test.js` |

### Step 3 — Run the Checklist

Read each file and apply all checks below.

For every finding record:

| Field | Content |
|---|---|
| **File** | Relative path |
| **Line(s)** | Approximate line range |
| **Rule** | Which check was triggered |
| **Severity** | `blocking` / `warning` / `note` |
| **Evidence** | Exact code snippet |
| **Fix** | Concrete suggestion |

#### Style Convention Checks

- **No magic values**: every color, spacing, font, and border-radius must use a `var(--token)` CSS variable. Raw hex, raw `px` sizes for spacing/radius, or raw color names are violations.
- **CSS classes for static styles**: layout, spacing, color, and typography that don't depend on runtime props or state must live in a CSS class in `index.css`, not inline.
- **Inline `style={{}}` only for dynamic values**: inline styles must be justified by a prop or state value. Static inline styles are violations.
- **`styles.js` for shared JS-side objects**: if the same style object appears in two or more components, it must be exported from `styles.js`.
- **No external styling tooling**: CSS Modules, styled-components, Tailwind, or similar libraries must not be introduced.

#### React / Component Checks

- **Single responsibility**: a component should do one thing. A component that fetches data, transforms it, *and* renders complex UI is a candidate for splitting.
- **Prop drilling depth**: passing props through more than two intermediate components without them being used is a smell — consider context or lifting state.
- **Key props**: list items rendered with `.map()` must have stable, unique `key` props (not array index unless the list is static and never reordered).
- **Side effects in render**: no `fetch`, `localStorage` reads, or other side effects outside `useEffect`.
- **Stale closure / missing deps**: `useEffect` and `useCallback` hooks should include all referenced variables in their dependency arrays.
- **Error and loading states**: components that fetch data should handle loading and error states visibly.

#### Test Coverage Checks

Refer to [fe-conventions.md](../implement-fe-task/fe-conventions.md) for what should be tested.

- Every component file should have a colocated `.test.jsx` file.
- Every API module file should have a colocated `.test.js` file.
- Tests must cover: render output, user interactions, state transitions, and error paths.
- Tests must use factory functions from `factories.js`, not inline raw objects.
- API module tests must mock `fetch` and assert on non-ok responses.

### Step 4 — Discuss With the User

Present findings **grouped by severity**, then by type (Style → React → Tests). For each finding:
- Briefly explain *why* it matters
- Show the evidence snippet
- Propose a fix

Ask the user to confirm, dismiss, or reclassify each finding before writing the report. Questions to ask:
- "Is this intentional? Should I mark it as accepted?"
- "Is this out of scope for now?"

### Step 5 — Write the Report

After discussion, create the report file at:

```
docks/dev/quality-reports/fe-review-YYYY-MM-DD.md
```

Use the report template below. Include only findings that were confirmed or left unresolved. Mark dismissed items as **Accepted / Won't fix** with the user's reason.

---

## Report Template

```markdown
# Frontend Code Quality Report — YYYY-MM-DD

## Summary

| Severity | Count |
|---|---|
| Blocking | N |
| Warning | N |
| Note | N |
| Accepted / Won't fix | N |

---

## Blocking

### [FILE:LINE] Rule name
**Evidence**
```jsx
// snippet
```
**Fix**: ...

---

## Warning

...

---

## Note

...

---

## Accepted / Won't fix

| File | Rule | Reason |
|---|---|---|
| ... | ... | ... |
```

---

## Severity Guide

| Level | Meaning |
|---|---|
| `blocking` | Correctness risk, broken convention contract, or a test gap that directly hides a known regression class — must fix before merge |
| `warning` | Maintainability or reliability degradation, style violation likely to spread — should fix soon |
| `note` | Minor smell or improvement opportunity — fix when touching the code |
