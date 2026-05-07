# Task 016: StoriesPage

**Feature:** M3 — Frontend UI Pages (Mocked)
**Status:** TODO

## Description

Implement the `StoriesPage` page component. On mount it calls `getStories()` from `api/stories.js` and renders a `StoryList`. Navigates to `StoryPage` when a story is selected.

## Scope

What IS included:
- `StoriesPage` component: calls `getStories()` on mount, stores result in state, passes it to `StoryList`
- Navigates to `/stories/:storyId` on story selection using React Router's `useNavigate`
- Loading state while fetch is pending
- Error state if fetch rejects

What is NOT included (deferred):
- `StoryList` implementation (task 015)
- Routing configuration (task 025)

## Deliverable

`frontend/src/pages/StoriesPage.jsx` — a functional React component that fetches and displays the stories list.

```
frontend/src/pages/StoriesPage.jsx
```

## Acceptance Criteria

- [ ] Calls `getStories()` on mount (via `useEffect`)
- [ ] Renders `StoryList` with the fetched stories
- [ ] Shows a loading indicator while data is loading
- [ ] Shows an error message if `getStories()` rejects
- [ ] Navigates to `/stories/:storyId` when `StoryList` calls `onSelect`
- [ ] Component is the default export

## Test Notes

Open the page in a browser; verify the mocked story titles appear and clicking one navigates to the story detail URL.

## Dependencies

- 013 (mock stories API)
- 015 (StoryList component)
