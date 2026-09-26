# Feature: App Navigation (Stories NavBar + Story Title Link)

**Status**: Draft
**Date**: 2026-09-24

## Summary
The app currently has no persistent navigation — the only way to move between pages is via in-page actions (clicking a scene in a list, browser back button). This feature adds the first piece of a global navbar (a left vertical bar with a single "Stories" icon) so the user can always jump back to the stories list, and adds a story-title link in the scene header so the user can jump from an active or finished scene back to its story's scene list.

## Value
- Solves the "I'm stuck deep in a scene with no way back" problem — currently the only escape route is the browser back button or manually editing the URL.
- Fits the project's core MVP flow (stories list → story scenes → active scene chat) by making that flow navigable in both directions, not just forward.
- Establishes the foundation for a real navbar as more sections/features are added later.
- Success: from any scene page, a user can reach the stories list and the parent story page in one click each, without using browser back.

## Scope

**In scope for first iteration:**
- A persistent `NavBar` component (left vertical bar), rendered on every page by wrapping `<Routes>` in `App.jsx`.
- One icon button (the provided SVG) linking to `/stories`, with a native `title="Stories"` tooltip on hover.
- `ScenePage` fetches the parent story (`getStory(storyId)`) concurrently with the existing scene/model fetches (added to the existing `Promise.all`), and passes the story title to `SceneHeader`.
- `SceneHeader` renders the story title before the scene title, as a link (`<Link to="/stories/:storyId">`) to the story's scene-list page.
- Styling via `.nav-bar`-style classes in `index.css`, using existing CSS variable tokens (no new colors/spacing values).

**Out of scope / future:**
- Active/current-page highlighting on the navbar.
- Additional nav items beyond "Stories".
- Mobile/responsive collapse behavior for the navbar.
- Custom styled (non-native) tooltip.
- A "back to story" link on the choice-driven-story page (`/stories/:storyId/play`).
- Backend changes (story title is fetched client-side, not added to the `SceneDetail` API response).

## User Flow
1. On any page, the user sees a left vertical navbar with a single icon.
2. Hovering the icon shows a native tooltip reading "Stories".
3. Clicking the icon navigates to `/stories` (the stories list), regardless of which page the user was on.
4. On an active or finished scene page, the header shows the story's title before the scene title.
5. Clicking the story title navigates to `/stories/:storyId` (that story's scene list), letting the user pick a different scene or create a new one.

## API Changes
None. No backend/API changes — this is a frontend-only feature. The story title is obtained by calling the existing `GET /api/stories/{story_id}` endpoint from `ScenePage`.

## Data Changes
None.

## Backend Changes
None.

## Frontend Changes
- **`frontend/src/components/NavBar.jsx`** (new): renders the left vertical navbar with the "Stories" icon button (`Link` to `/stories`, `title="Stories"` for tooltip).
- **`frontend/src/App.jsx`**: wrap `<Routes>` with `NavBar` + a page-content container so the navbar renders on every route, in a flex row layout.
- **`frontend/src/pages/ScenePage.jsx`**: add `getStory(storyId)` to the existing `Promise.all([getScene(...), getModels()])` call; store the story title in state; pass it down to `SceneHeader`.
- **`frontend/src/components/SceneHeader.jsx`**: accept a `storyId` and `storyTitle` prop; render the story title as a `<Link to={`/stories/${storyId}`}>` before the existing `Scene {scene.id}` heading.
- **`frontend/src/index.css`**: add `.nav-bar` / `.nav-bar__icon-button` (or similar) classes for the vertical bar layout and icon sizing, and a small class for the new story-title link in the scene header, all using existing tokens (`--space-*`, `--text`, `--text-h`, `--accent`, etc.).

## Open Questions
- None currently — all major design questions (fetch strategy, layout wrapping, tooltip mechanism, component location, scope boundaries) were resolved during brainstorming.

## Risks
- `Promise.all` in `ScenePage` will now reject if any of the three calls fails (including the new `getStory` call); existing error handling (`.catch(err => setError(...))`) already covers this, but worth confirming the error message stays clear when it's the story fetch that fails.
- Wrapping `App.jsx` in a flex-row layout could interact with `.scene-page--fixed-frame`'s `100dvh` sizing; needs a quick visual check that the scene page still fills the viewport correctly next to the navbar column.
