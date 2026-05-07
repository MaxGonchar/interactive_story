# Task 015: StoryList Component

**Feature:** M3 — Frontend UI Pages (Mocked)
**Status:** TODO

## Description

Implement the `StoryList` presentational component. Receives an array of story objects as a prop and renders a clickable list. Calls an `onSelect` callback when a story is clicked.

## Scope

What IS included:
- `StoryList` component that accepts `stories: [{ id, title }]` and `onSelect(storyId)` props
- Renders each story as a list item with its title
- Calls `onSelect(story.id)` on click

What is NOT included (deferred):
- Fetching data (done in `StoriesPage`, task 016)
- Routing/navigation (done in page-level tasks)
- Styling beyond minimal structure

## Deliverable

`frontend/src/components/StoryList.jsx` — a functional React component that renders a `<ul>` of story titles.

```
frontend/src/components/StoryList.jsx
```

## Acceptance Criteria

- [ ] Component renders a list item for each story in the `stories` prop
- [ ] Clicking a list item calls `onSelect` with the correct story `id`
- [ ] Renders an empty state message (e.g. "No stories available") when `stories` is empty
- [ ] Component is the default export

## Test Notes

Render in isolation with `stories=[{id:"1", title:"Test Story"}]` and `onSelect={console.log}`; verify the title appears and clicking logs the id.

## Dependencies

None
