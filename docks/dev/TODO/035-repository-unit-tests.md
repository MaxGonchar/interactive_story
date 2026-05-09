# Task 035: Repository Unit Tests

**Feature:** M4 — Data Access Layer
**Status:** TODO

## Description

Write pytest unit tests for all three repositories (`StoryRepository`, `SceneRepository`, `CharacterRepository`) and the three utility modules (`file_paths`, `yaml_storage`, `atomic_write`). Tests run against the fixture files created in task 026, with mutable tests operating on temp copies.

## Scope

What IS included:
- `backend/tests/test_file_paths.py` — asserts all five path functions return correct `Path` values with a fixed `DATA_ROOT`
- `backend/tests/test_yaml_storage.py` — round-trip read/write tests using `tmp_path`
- `backend/tests/test_atomic_write.py` — create, overwrite, directory-creation, and no-leftover-tmp tests
- `backend/tests/test_story_repository.py` — `list_stories` sort order, `get_story` happy path, `get_story` missing id error
- `backend/tests/test_scene_repository.py` — `get_metadata`, `get_messages`, `save_messages` round-trip, `update_message` preserves others, `delete_message` preserves others, `update_message` missing id error, `delete_message` missing id error
- `backend/tests/test_character_repository.py` — `get_character` happy path, `get_character` missing id error, `get_characters` list

What is NOT included (deferred):
- Integration tests hitting real HTTP endpoints (M6)
- LLM-related tests (M5)
- Service-layer tests (M6)

## Deliverable

Six pytest test files under `backend/tests/`, all passing with `pytest backend/tests/`. All async tests use `pytest-asyncio` with `@pytest.mark.asyncio`.

```
backend/tests/
  test_file_paths.py
  test_yaml_storage.py
  test_atomic_write.py
  test_story_repository.py
  test_scene_repository.py
  test_character_repository.py
```

## Acceptance Criteria

- [ ] `pytest backend/tests/` exits with code 0 (all tests pass)
- [ ] Each test file contains at least the test cases listed in Scope above
- [ ] All async test functions are decorated with `@pytest.mark.asyncio`
- [ ] Mutable tests (write/update/delete) operate on `tmp_path` copies and do not modify `data/` fixture files
- [ ] `DATA_ROOT` is pointed at the fixture `data/` directory via monkeypatch or env variable, not hardcoded
- [ ] No test imports production service or router code

## Test Notes

Run with: `cd backend && pytest tests/ -v`

Ensure `pytest`, `pytest-asyncio`, `aiofiles`, and `pyyaml` are listed in `requirements.txt` (or a `requirements-dev.txt`).

## Dependencies

026, 027, 028, 029, 030, 031, 032, 033, 034
