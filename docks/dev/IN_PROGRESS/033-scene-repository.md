# Task 033: SceneRepository

**Feature:** M4 — Data Access Layer
**Status:** TODO

## Description

Implement `app/repositories/scene_repository.py` with `SceneRepository`, the most complex repository in M4. It covers all read and write operations for scene metadata and messages, using atomic writes for every mutation.

## Scope

What IS included:
- `SceneRepository` class with:
  - `async get_metadata(story_id, scene_id) -> SceneMetadata` — reads `metadata.yaml`; raises `KeyError` if not found
  - `async save_metadata(story_id, scene_id, metadata: SceneMetadata) -> None` — serialises and atomically writes `metadata.yaml`
  - `async get_messages(story_id, scene_id) -> list[Message]` — reads `messages.yaml`; returns `[]` if file missing
  - `async save_messages(story_id, scene_id, messages: list[Message]) -> None` — serialises and atomically writes `messages.yaml`
  - `async update_message(story_id, scene_id, message_id: int, new_content: str) -> Message` — reads messages, updates the matching entry, saves, returns updated `Message`; raises `KeyError` if `message_id` not found
  - `async delete_message(story_id, scene_id, message_id: int) -> None` — reads messages, removes matching entry, saves; raises `KeyError` if `message_id` not found
- All methods are coroutines; I/O delegated to `await yaml_storage.read_yaml` and `await atomic_write`

What is NOT included (deferred):
- Scene-level locking (M6 concurrency model)
- Validation of finished-state guard (service layer, M6)
- Creating new message ids (service layer, M6)

## Deliverable

`backend/app/repositories/scene_repository.py` — a finished class with all six methods.

```
backend/app/repositories/scene_repository.py
```

## Acceptance Criteria

- [ ] All six methods are coroutines (`async def`) and must be awaited
- [ ] `await get_metadata(...)` returns a `SceneMetadata` domain object for the fixture scene
- [ ] `await get_messages(...)` returns a `list[Message]` sorted by id for the fixture scene
- [ ] `await save_messages(...)` followed by `await get_messages(...)` returns the saved messages (round-trip test)
- [ ] `await update_message(...)` changes only the targeted message's content; all other messages remain unchanged
- [ ] `await delete_message(...)` removes only the targeted message; all other messages remain unchanged
- [ ] `await update_message(...)` and `await delete_message(...)` raise `KeyError` for a non-existent `message_id`
- [ ] All writes use `await atomic_write`; no direct `open(..., 'w')` calls for mutation

## Test Notes

Use `pytest-asyncio` with `@pytest.mark.asyncio` on all test functions. Use `tmp_path` + `shutil.copytree` for a writable copy of fixtures. Test read methods against the fixture directly. Test write methods against temp copies, then re-read and assert correctness.

## Dependencies

026, 027, 028, 029, 030, 031
