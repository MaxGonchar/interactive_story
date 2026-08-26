# Feature: Remove index.yaml

**Status**: Draft  
**Date**: 2026-07-15

## Summary
`data/stories/index.yaml` duplicates data already available in individual `story.yaml` files (`title`) and acts as the only source for fields (`created_at`, `type`) that belong there anyway. Removing it simplifies the storage model: stories are discovered by scanning the `data/stories/` directory and reading each `story.yaml` concurrently — the same async pattern already used to read scene metadata.

## Value
- Eliminates `title` duplication between `index.yaml` and `story.yaml`.
- Removes the need to keep `index.yaml` in sync with the filesystem on any future story creation.
- Makes `story.yaml` the single authoritative source for story-level metadata.
- Aligns both story types with the project's existing ID convention: IDs derived from folder names, not stored inside files.

**Success criteria**: `GET /stories` returns the correct list without reading `index.yaml`; no other behaviour changes.

## Scope
**In scope:**
- Remove `index.yaml` from both scene-driven and choice-driven storage layouts.
- Add `created_at` and `type` to scene-driven `story.yaml`.
- Add `created_at` to choice-driven `story.yaml`; remove `id` field.
- Update `list_stories` to scan `data/stories/` dirs and read each `story.yaml` concurrently.
- Update all affected storage models, repositories, and tests.
- Update `data_storage_structure.md` and `features/ChoiceDrivenStory/design.md`.

**Out of scope / future:**
- Any change to `GET /stories` API response shape — it stays the same.
- In-app story creation (would need to write `story.yaml` instead of updating `index.yaml`).

## User Flow
No user-facing change. The stories list page continues to work identically.

## API Changes
None. `GET /stories` response shape is unchanged.

## Data Changes

### Removed
`data/stories/index.yaml` — deleted entirely.

### Scene-driven `story.yaml` — add `created_at` and `type`
```yaml
title: "Mila and Bun"
type: "scene"
created_at: "2024-06-01T12:00:00Z"
```

### Choice-driven `story.yaml` — add `created_at`, remove `id`
```yaml
title: "The Black Harbor"
type: "choice_driven"
created_at: "2024-06-01T12:00:00Z"
character_ids:
  - "john"
writing_style: "dark, suspenseful, first-person"
plot_directions:
  - "Romance with Sarah"
  - "Betrayal by the Ally"
```

**Constraints:**
- `created_at` is required in all `story.yaml` files.
- `type` is required; valid values: `"scene"` | `"choice_driven"`.
- Story ID continues to be derived from the enclosing folder name — not stored in the file.
- Stories are sorted by `created_at` desc when returned from `list_stories`.

## Backend Changes

### `app/models/storage.py`
- Remove `StoriesIndexEntry` and `StoriesIndex` models.
- Add `StoryYaml` fields: `type: StoryType` and `created_at: str`.
- Update `ChoiceDrivenStoryYaml`: add `created_at: str`, remove `id: str`.

### `app/repositories/story_repository.py` — `list_stories`
Replace single `index.yaml` read with:
1. Async dir scan of `data/stories/` to collect UUID folder names.
2. `asyncio.gather` read of each `story.yaml`.
3. Sort results by `created_at` desc.

Pattern mirrors the existing `get_story` scene scan.

### `app/utils/file_paths.py`
- Remove `stories_index()` helper.
- Add `stories_dir()` helper (returns `data/stories/` path) if not already present.

### `app/repositories/choice_driven_story_repository.py`
- `get_story_meta`: stop reading/using `raw.id`; pass `story_id` (from caller) as the domain object's `id`.

### Tests
- Remove fixtures and tests for `StoriesIndex` / `StoriesIndexEntry`.
- Remove `stories_index()` path tests.
- Update `story_repository` tests: replace `index.yaml` fixture setup with per-story `story.yaml` fixtures containing `created_at` and `type`.
- Update `choice_driven_story_repository` tests: remove `id` from fixture YAMLs.
- Update `data-test/` fixture files to match new schemas.

## Frontend Changes
None. API contract is unchanged.

## Open Questions
- Should `created_at` be validated as ISO 8601 on read (Pydantic `datetime` type) or kept as a plain string for simplicity? Current `index.yaml` stores it as a string. - Answer - keep current string
- Migration: existing `story.yaml` files need `created_at` and `type` added manually before deploying. Should a migration script be written, or is manual edit acceptable given single-user local usage? - Answer - manual.

## Risks
- **Data migration**: existing `story.yaml` files lack `created_at` and `type`. Reading them without migration will cause a Pydantic validation error. Must migrate data files before or alongside the code change.
- **Choice-driven `id` removal**: `ChoiceDrivenStoryRepository.get_story_meta` currently uses `raw.id`. After removal, the caller-supplied `story_id` must be used instead — straightforward but must not be missed.
