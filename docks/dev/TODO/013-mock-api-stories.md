# Task 013: Mocked API Client — stories.js

**Feature:** M3 — Frontend UI Pages (Mocked)
**Status:** TODO

## Description

Create the `api/stories.js` module with mocked implementations of all story-related API calls. This module provides the data contract the frontend pages will consume, with hardcoded return values matching the real endpoint shapes from `endpoints.md`.

## Scope

What IS included:
- `getStories()` — returns a hardcoded array of story objects `[{ id, title }]`
- `getStory(storyId)` — returns a hardcoded story object `{ id, title, scenes, active_scene_id }`

What is NOT included (deferred):
- Real HTTP calls (task for M6)
- `api/scenes.js` (task 014)

## Deliverable

`frontend/src/api/stories.js` with two exported async functions returning hardcoded data matching `endpoints.md` response shapes.

```
frontend/src/api/stories.js
```

## Acceptance Criteria

- [ ] `getStories()` is exported and returns a resolved promise with `{ data: [{ id, title }] }`
- [ ] `getStory(storyId)` is exported and returns a resolved promise with `{ data: { id, title, scenes: [{id, finished}], active_scene_id } }`
- [ ] Hardcoded values contain at least 2 stories and at least 3 scenes (one active) to exercise all UI states
- [ ] Functions are async (return a Promise)

## Test Notes

Import the module in a browser console or component and call each function; verify the resolved value matches the expected shape.

## Dependencies

None
