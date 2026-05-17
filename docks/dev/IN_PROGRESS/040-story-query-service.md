# Task 040: StoryQueryService

**Feature:** M6 — Services and Full Integration
**Status:** TODO

## Description

Implement `StoryQueryService` in `app/services/story_query_service.py`. This service wraps `StoryRepository` and provides the two story-related query operations needed by the API: listing all stories and fetching a single story with its scene statuses.

## Scope

What IS included:
- `StoryQueryService` class with two async methods:
  - `list_stories() -> list[StoryIndexItem]`
  - `get_story(story_id: str) -> StoryMeta`
- `get_story` re-raises `KeyError` from the repository unchanged (callers handle 404)

What is NOT included (deferred):
- Story creation or mutation
- Filtering / pagination
- Router wiring (task 046)

## Deliverable

A finished service class at `backend/app/services/story_query_service.py`.

```
backend/app/services/story_query_service.py
```

## Acceptance Criteria

- [ ] `list_stories()` delegates to `StoryRepository.list_stories()` and returns the result unchanged
- [ ] `get_story(story_id)` delegates to `StoryRepository.get_story(story_id)` and returns a `StoryMeta`
- [ ] `get_story` raises `KeyError` when story is not found (propagated from repository)
- [ ] Unit tests pass: `test_story_query_service.py` covers both methods with a mocked `StoryRepository`

## Test Notes

Create `backend/tests/services/test_story_query_service.py`.

Tests to write:
- `test_list_stories_returns_repository_result` — mock `StoryRepository.list_stories` to return a list; assert service returns the same list
- `test_get_story_returns_story_meta` — mock `StoryRepository.get_story` to return a `StoryMeta`; assert service returns it
- `test_get_story_raises_key_error_when_not_found` — mock `StoryRepository.get_story` to raise `KeyError`; assert service propagates it

## Dependencies

032 (StoryRepository)
