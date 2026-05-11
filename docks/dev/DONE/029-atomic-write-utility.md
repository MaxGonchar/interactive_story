# Task 029: atomic_write Utility

**Feature:** M4 — Data Access Layer
**Status:** TODO

## Description

Implement `app/utils/atomic_write.py` with a single async function `atomic_write(path: Path, data: bytes)` that writes bytes to a file atomically using the write-to-temp-then-rename strategy defined in `data_storage_structure.md`. File writing uses `aiofiles` to be non-blocking; the final `os.replace` rename is sync (kernel atomic op, negligible latency).

## Scope

What IS included:
- `async atomic_write(path: Path, data: bytes) -> None`:
  1. Create parent directories if they don't exist (`path.parent.mkdir(parents=True, exist_ok=True)` — sync, fast)
  2. Write `data` to `<path>.tmp` via `aiofiles.open` in the same directory
  3. `await f.flush()` then `os.fsync(f.fileno())` the temp file
  4. `os.replace(<path>.tmp, path)` (atomic rename, sync kernel call)
- The function must ensure the temp file is cleaned up (`unlink`) if an exception occurs mid-write

What is NOT included (deferred):
- Per-scene locking (defined in the concurrency model; deferred to M6)
- Any YAML serialisation (done by `yaml_storage.py`)
- Reading files

## Deliverable

`backend/app/utils/atomic_write.py` — a finished module with `atomic_write`.

```
backend/app/utils/atomic_write.py
```

## Acceptance Criteria

- [ ] `atomic_write` is a coroutine (`async def`) and must be awaited
- [ ] `await atomic_write(path, data)` creates the file with correct content when the target does not exist
- [ ] `await atomic_write(path, data)` overwrites an existing file with correct content
- [ ] No `.tmp` file is left on disk after a successful write
- [ ] Parent directories are created automatically if missing
- [ ] If an exception occurs during write, the original file (if it existed) is not corrupted
- [ ] File writing uses `aiofiles.open` (not the built-in `open`)

## Test Notes

Use `pytest-asyncio` with `@pytest.mark.asyncio`. `await atomic_write(path, data)`, then assert file content with a plain sync read; assert no `.tmp` sibling exists. Test overwrite: write once, write again with different bytes, assert final content is the second write. Test directory creation: use a nested path that does not exist yet.

## Dependencies

027, 028
