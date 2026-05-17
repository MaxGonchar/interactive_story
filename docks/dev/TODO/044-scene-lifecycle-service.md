# Task 044: SceneLifecycleService

**Feature:** M6 — Services and Full Integration
**Status:** TODO

## Description

Implement `SceneLifecycleService` in `app/services/scene_lifecycle_service.py`. This service handles finishing a scene: it validates the scene is not already finished, sets `finished=True`, records the summary, and persists the updated metadata via `SceneRepository.save_metadata()`.

## Scope

What IS included:
- `SceneLifecycleService` class with one async method:
  - `finish_scene(story_id: str, scene_id: int, summary: str) -> SceneMetadata`
- Guard: raises `ValueError("scene_finished")` if scene is already finished
- Updates `SceneMetadata.finished = True` and `SceneMetadata.scene_summary = [summary]`
- Persists via `SceneRepository.save_metadata()`
- Returns updated `SceneMetadata`

What is NOT included (deferred):
- Story existence check (handled upstream)
- Creating new scenes
- Router error mapping (task 047)

## Deliverable

A finished service class at `backend/app/services/scene_lifecycle_service.py`.

```
backend/app/services/scene_lifecycle_service.py
```

## Acceptance Criteria

- [ ] `finish_scene` returns `SceneMetadata` with `finished=True` and `scene_summary` set
- [ ] Raises `ValueError("scene_finished")` when scene is already finished
- [ ] `SceneRepository.save_metadata` is called with the updated metadata
- [ ] Unit tests pass: `test_scene_lifecycle_service.py` covers success and already-finished cases

## Test Notes

Create `backend/tests/services/test_scene_lifecycle_service.py`.

Tests to write:
- `test_finish_scene_returns_updated_metadata` — mock metadata `finished=False`; assert returned metadata has `finished=True` and correct summary
- `test_finish_scene_calls_save_metadata` — assert `SceneRepository.save_metadata` is called once with updated data
- `test_finish_scene_raises_when_already_finished` — mock metadata `finished=True`; assert `ValueError("scene_finished")`

## Dependencies

033 (SceneRepository)
