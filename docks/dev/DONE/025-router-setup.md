# Task 025: React Router Setup and Navigation Wiring

**Feature:** M3 — Frontend UI Pages (Mocked)
**Status:** TODO

## Description

Configure React Router in the app entry point and wire up the three page routes. After this task the full navigation flow — stories list → story detail → scene view — works in the browser.

## Scope

What IS included:
- Install `react-router-dom` (if not already present)
- Configure `BrowserRouter` in `main.jsx` (or `App.jsx`)
- Define three routes:
  - `/` or `/stories` → `StoriesPage`
  - `/stories/:storyId` → `StoryPage`
  - `/stories/:storyId/scenes/:sceneId` → `ScenePage`
- Redirect `/` to `/stories` if using a separate root path

What is NOT included (deferred):
- 404 / catch-all route
- Auth-gated routes

## Deliverable

Updated `frontend/src/App.jsx` (or equivalent entry) with `<Routes>` defined. Running the dev server and visiting each URL renders the correct page.

```
frontend/src/App.jsx   (or main.jsx)
```

## Acceptance Criteria

- [ ] `react-router-dom` is listed in `package.json` dependencies
- [ ] Visiting `/stories` renders `StoriesPage`
- [ ] Visiting `/stories/:storyId` renders `StoryPage`
- [ ] Visiting `/stories/:storyId/scenes/:sceneId` renders `ScenePage`
- [ ] Clicking a story in `StoriesPage` navigates to the correct `StoryPage` URL
- [ ] Clicking a scene in `StoryPage` navigates to the correct `ScenePage` URL

## Test Notes

Start the dev server and manually walk the full flow: open `/stories`, click a story, click a scene, verify the scene view loads with mocked data.

## Dependencies

- 016 (StoriesPage)
- 018 (StoryPage)
- 024 (ScenePage)
