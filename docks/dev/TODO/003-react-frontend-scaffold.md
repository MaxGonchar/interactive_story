# Task 003: React Frontend Scaffold

**Feature:** M1 — Project Skeleton
**Status:** TODO

## Description

Bootstrap the React frontend application using Vite. The app must boot without errors, serve an index page with visible placeholder text, and be reachable in a browser at `http://localhost:5173`. No real API calls or routing logic are included.

## Scope

What IS included:
- `frontend/` directory created via `npm create vite@latest frontend -- --template react`
- Default Vite/React boilerplate cleaned up: remove sample counter and CSS clutter
- `frontend/src/main.jsx` — Vite entry point (unchanged from scaffold)
- `frontend/src/App.jsx` — renders a single `<h1>Interactive Story</h1>` placeholder
- `frontend/index.html` — Vite HTML entry (unchanged from scaffold)
- `frontend/package.json` with `react`, `react-dom`, `vite` dependencies

What is NOT included (deferred):
- Any routing library installation or configuration (M3)
- Any component beyond `App.jsx`
- API client setup (M3)
- CSS frameworks or design system (M3)

## Deliverable

A Vite + React project in `frontend/` that renders `<h1>Interactive Story</h1>` on the index page.

```
frontend/
  index.html
  vite.config.js
  package.json
  src/
    main.jsx
    App.jsx
```

## Acceptance Criteria

- [ ] `npm install && npm run dev` runs without errors from `frontend/`
- [ ] Browser at `http://localhost:5173` displays the text "Interactive Story" without console errors
- [ ] `frontend/package.json` has `"dev"` script pointing to `vite`
- [ ] No TypeScript errors (project uses plain JavaScript/JSX)

## Test Notes

Manual smoke test:
```bash
cd frontend
npm install
npm run dev
# open http://localhost:5173 in browser
# verify "Interactive Story" heading is visible
```

## Dependencies

none
