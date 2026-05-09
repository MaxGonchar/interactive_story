# Task 027: file_paths Utility

**Feature:** M4 — Data Access Layer
**Status:** TODO

## Description

Implement `app/utils/file_paths.py`, a module of pure functions that build absolute filesystem paths to every YAML file type defined in the storage schema. Centralising path logic means repositories never construct paths inline.

## Scope

What IS included:
- `FilePaths` class (or module-level functions) for:
  - `stories_index()` → path to `data/stories/index.yaml`
  - `story_file(story_id)` → path to `data/stories/<story_id>/story.yaml`
  - `character_file(story_id, character_id)` → path to `data/stories/<story_id>/characters/<character_id>.yaml`
  - `scene_metadata_file(story_id, scene_id)` → path to `data/stories/<story_id>/scenes/<scene_id>/metadata.yaml`
  - `scene_messages_file(story_id, scene_id)` → path to `data/stories/<story_id>/scenes/<scene_id>/messages.yaml`
- `DATA_ROOT` configurable via environment variable `DATA_ROOT` (defaults to `<repo_root>/data`)

What is NOT included (deferred):
- File existence checks (responsibility of the caller)
- Directory creation
- Any I/O operations

## Deliverable

`backend/app/utils/file_paths.py` — a finished module with all five path functions and configurable `DATA_ROOT`.

```
backend/app/utils/file_paths.py
```

## Acceptance Criteria

- [ ] `stories_index()` returns a `pathlib.Path` ending in `data/stories/index.yaml`
- [ ] `story_file("abc")` returns a path ending in `data/stories/abc/story.yaml`
- [ ] `character_file("abc", "captain-mora")` returns a path ending in `data/stories/abc/characters/captain-mora.yaml`
- [ ] `scene_metadata_file("abc", 1)` returns a path ending in `data/stories/abc/scenes/1/metadata.yaml`
- [ ] `scene_messages_file("abc", 1)` returns a path ending in `data/stories/abc/scenes/1/messages.yaml`
- [ ] `DATA_ROOT` can be overridden by setting the `DATA_ROOT` environment variable
- [ ] All functions return `pathlib.Path` objects (not strings)

## Test Notes

Unit test each function with a fixed `DATA_ROOT` and assert the returned path string ends with the expected suffix. No filesystem I/O required.

## Dependencies

026 (fixture files establish the directory layout this module must reflect)
