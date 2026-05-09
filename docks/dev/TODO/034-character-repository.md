# Task 034: CharacterRepository

**Feature:** M4 — Data Access Layer
**Status:** TODO

## Description

Implement `app/repositories/character_repository.py` with `CharacterRepository`, a read-only repository that loads character card YAML files and returns domain objects.

## Scope

What IS included:
- `CharacterRepository` class with:
  - `async get_character(story_id: str, character_id: str) -> CharacterCard` — reads `characters/<character_id>.yaml`; raises `KeyError` if not found
  - `async get_characters(story_id: str, character_ids: list[str]) -> list[CharacterCard]` — awaits `get_character` for each id in order, propagates `KeyError` if any character is missing
- All methods are coroutines; I/O delegated to `await yaml_storage.read_yaml`

What is NOT included (deferred):
- Writing or creating character files (out of MVP scope)
- Listing all characters without explicit ids

## Deliverable

`backend/app/repositories/character_repository.py` — a finished class with `get_character` and `get_characters`.

```
backend/app/repositories/character_repository.py
```

## Acceptance Criteria

- [ ] Both methods are coroutines (`async def`) and must be awaited
- [ ] `await get_character("<fixture_story_id>", "captain-mora")` returns a `CharacterCard` with correct id, story_id, and name
- [ ] `await get_character(...)` with a non-existent `character_id` raises `KeyError`
- [ ] `await get_characters(...)` with a list of one id returns a list with one `CharacterCard`
- [ ] `await get_characters(...)` with a missing id raises `KeyError`
- [ ] Return values are `CharacterCard` domain model instances, not raw dicts

## Test Notes

Use `pytest-asyncio` with `@pytest.mark.asyncio`. Await all repository calls. Read the fixture character and assert field values. Test missing-character error path.

## Dependencies

026, 027, 028, 030, 031
