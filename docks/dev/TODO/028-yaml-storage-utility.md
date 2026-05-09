# Task 028: yaml_storage Utility

**Feature:** M4 — Data Access Layer
**Status:** TODO

## Description

Implement `app/utils/yaml_storage.py` with two functions: an async function to read a YAML file and return a Python dict, and a sync function to serialise a dict to YAML bytes. Repositories use these functions for all read and (pre-atomic-write) serialisation steps. File I/O uses `aiofiles` to be non-blocking inside the async FastAPI event loop.

## Scope

What IS included:
- `async read_yaml(path: Path) -> dict` — reads the file at `path` with `aiofiles`, parses the content with `yaml.safe_load`, returns the resulting dict. Raises `FileNotFoundError` if the file does not exist.
- `dump_yaml(data: dict) -> bytes` — **sync** — serialises `data` to YAML using `yaml.safe_dump`, returns UTF-8 encoded bytes ready for `atomic_write`. No I/O; stays synchronous.

What is NOT included (deferred):
- Writing to disk (that is `atomic_write.py`'s responsibility)
- Schema validation (done by Pydantic models in repositories)
- Any caching or in-memory store

## Deliverable

`backend/app/utils/yaml_storage.py` — a finished module with `read_yaml` and `dump_yaml`.

```
backend/app/utils/yaml_storage.py
```

## Acceptance Criteria

- [ ] `read_yaml(path)` is a coroutine (`async def`) and must be awaited
- [ ] `read_yaml(path)` returns a `dict` for a valid YAML file
- [ ] `read_yaml(path)` raises `FileNotFoundError` when the file does not exist
- [ ] `dump_yaml(data)` is synchronous and returns `bytes`
- [ ] A round-trip `await read_yaml` → mutate → `dump_yaml` preserves all keys and values when written back and re-read
- [ ] Uses `yaml.safe_load` / `yaml.safe_dump` (not `yaml.load`)
- [ ] File reading uses `aiofiles.open` (not the built-in `open`)

## Test Notes

Use `pytest-asyncio` with `@pytest.mark.asyncio`. Write a known dict to a temp YAML file, `await read_yaml(path)`, assert equality. Call `dump_yaml`, write bytes to a temp file, `await read_yaml` again, assert round-trip equality.

Ensure `aiofiles` is listed in `requirements.txt`.

## Dependencies

027
