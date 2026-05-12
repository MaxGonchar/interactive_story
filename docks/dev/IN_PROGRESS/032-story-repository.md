# Task 032: StoryRepository

**Feature:** M4 — Data Access Layer
**Status:** TODO

## Description

Implement `app/repositories/story_repository.py` with `StoryRepository`, a class that reads story data from YAML files and returns domain objects. Covers the stories index and individual story metadata.

## Scope

What IS included:
- `StoryRepository` class with:
  - `async list_stories() -> list[StoryIndexItem]` — reads `index.yaml`, returns entries sorted by `order` ascending
  - `async get_story(story_id: str) -> StoryMeta` — reads `story.yaml`, returns `StoryMeta`; raises `KeyError` if the file does not exist
- Uses `file_paths`, `yaml_storage`, and storage/domain models internally
- All methods are coroutines; I/O is delegated to `await yaml_storage.read_yaml`

What is NOT included (deferred):
- Writing story data (out of MVP scope)
- Scene finished-status aggregation (done in service layer, M6)
- Character data (handled by `CharacterRepository`, task 034)

## Deliverable

`backend/app/repositories/story_repository.py` — a finished class with `list_stories` and `get_story`.

```
backend/app/repositories/story_repository.py
```

## Acceptance Criteria

- [ ] Both methods are coroutines (`async def`) and must be awaited
- [ ] `await StoryRepository().list_stories()` returns a `list[StoryIndexItem]` sorted by `order` when called against the fixture files (task 026)
- [ ] `await StoryRepository().get_story("<fixture_story_id>")` returns a `StoryMeta` with correct id, title, and scene list
- [ ] `await StoryRepository().get_story("nonexistent-id")` raises `KeyError`
- [ ] Return values are domain model instances, not raw dicts or storage models
- [ ] No direct `open()` calls in the class; all I/O goes through `await yaml_storage.read_yaml`

## Test Notes

Use `pytest-asyncio` with `@pytest.mark.asyncio` on all test functions. Point `DATA_ROOT` at the fixture `data/` directory via monkeypatch or env variable.

## Dependencies

026, 027, 028, 030, 031
