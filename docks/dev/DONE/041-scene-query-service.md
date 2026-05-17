# Task 041: SceneQueryService

**Feature:** M6 — Services and Full Integration
**Status:** TODO

## Description

Implement `SceneQueryService` in `app/services/scene_query_service.py`. This service loads scene metadata and message history together, providing the combined data required by the `GET /api/stories/{story_id}/scenes/{scene_id}` endpoint. It also validates that the parent story exists before fetching the scene.

## Scope

What IS included:
- `SceneQueryService` class with one async method:
  - `get_scene(story_id: str, scene_id: int) -> tuple[SceneMetadata, list[Message]]`
- Story existence check via `StoryRepository.get_story` (raises `KeyError` if story not found)
- Scene metadata and messages fetched via `SceneRepository`

What is NOT included (deferred):
- Writing or mutating messages (task 043)
- LLM interaction (task 042)
- Router wiring (task 047)

## Deliverable

A finished service class at `backend/app/services/scene_query_service.py`.

```
backend/app/services/scene_query_service.py
```

## Acceptance Criteria

- [ ] `get_scene(story_id, scene_id)` returns a `(SceneMetadata, list[Message])` tuple
- [ ] Raises `KeyError` with story_id if story does not exist
- [ ] Raises `KeyError` with scene_id if scene does not exist
- [ ] Messages are included from `SceneRepository.get_messages()`
- [ ] Unit tests pass: `test_scene_query_service.py` covers success path and both not-found cases

## Test Notes

Create `backend/tests/services/test_scene_query_service.py`.

Tests to write:
- `test_get_scene_returns_metadata_and_messages` — mock both repos to return valid data; assert correct tuple
- `test_get_scene_raises_when_story_not_found` — mock `StoryRepository.get_story` to raise `KeyError(story_id)`; assert propagated
- `test_get_scene_raises_when_scene_not_found` — mock `SceneRepository.get_metadata` to raise `KeyError(scene_id)`; assert propagated

## Dependencies

032 (StoryRepository), 033 (SceneRepository)
