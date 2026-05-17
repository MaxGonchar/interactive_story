# Task 043: SceneMessageService

**Feature:** M6 — Services and Full Integration
**Status:** TODO

## Description

Implement `SceneMessageService` in `app/services/scene_message_service.py`. This service handles editing and deleting individual messages within an active (non-finished) scene. Both operations are guarded: they raise `ValueError("scene_finished")` if the scene is already finished.

## Scope

What IS included:
- `SceneMessageService` class with two async methods:
  - `edit_message(story_id: str, scene_id: int, message_id: int, new_content: str) -> Message`
  - `delete_message(story_id: str, scene_id: int, message_id: int) -> None`
- Guard on both methods: load scene metadata, raise `ValueError("scene_finished")` if `finished` is `True`
- Delegation to `SceneRepository.update_message()` and `SceneRepository.delete_message()`
- `KeyError` from repository (message not found) propagates unchanged

What is NOT included (deferred):
- Story existence check (handled in router or query service)
- Router error mapping (task 047)

## Deliverable

A finished service class at `backend/app/services/scene_message_service.py`.

```
backend/app/services/scene_message_service.py
```

## Acceptance Criteria

- [ ] `edit_message` returns the updated `Message` domain object
- [ ] `delete_message` returns `None` on success
- [ ] Both methods raise `ValueError("scene_finished")` when scene is finished
- [ ] Both methods propagate `KeyError` from repository when message not found
- [ ] Unit tests pass: `test_scene_message_service.py` covers success, finished-scene guard, and not-found cases for both methods

## Test Notes

Create `backend/tests/services/test_scene_message_service.py`.

Tests to write:
- `test_edit_message_returns_updated_message` — mock scene not finished, mock `update_message` to return a `Message`; assert returned
- `test_edit_message_raises_when_scene_finished` — mock metadata `finished=True`; assert `ValueError("scene_finished")`
- `test_edit_message_raises_when_message_not_found` — mock `update_message` to raise `KeyError`; assert propagated
- `test_delete_message_succeeds` — mock scene not finished, assert `delete_message` called once
- `test_delete_message_raises_when_scene_finished` — mock metadata `finished=True`; assert `ValueError`
- `test_delete_message_raises_when_message_not_found` — mock `delete_message` to raise `KeyError`; assert propagated

## Dependencies

033 (SceneRepository)
