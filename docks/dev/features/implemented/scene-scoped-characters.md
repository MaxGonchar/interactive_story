# Feature: Scene-Scoped Characters

**Status**: Draft  
**Date**: 2026-07-03

## Summary

Currently character references are split across two storage layers: `story.yaml` holds a global registry (`character_ids`) and the player character pointer (`user_character_id`), while each `scene/metadata.yaml` holds its own character subset. This duplication creates a cross-layer dependency — scene play must fetch story metadata at runtime just to resolve `user_character_id`, coupling the scene data access path to the story repository. This redesign removes the story-level character fields, making the scene fully self-contained for play, and treating the `characters/` directory as the implicit character registry.

## Motivation

### Problem 1 — Redundant character registry

`story.yaml` maintains `character_ids` as a manifest of all characters that exist for a story. This list serves one runtime purpose: a validation constraint that `scene.character_ids` must be a subset of it. In practice:
- The constraint is not enforced by any service-layer logic; it is only a documented invariant.
- The `characters/` directory already implicitly defines the available character set — if a file is missing, `CharacterRepository` raises `NotFoundError` at load time.
- No scene-driven play path reads `story.character_ids` at runtime.

The field adds manual maintenance burden (keep story and scene in sync) with no runtime value.

### Problem 2 — Cross-repository coupling in scene play

`user_character_id` lives on `story.yaml`, but it is needed during scene play. As a result, `ScenePlayService` fetches `StoryRepository.get_story()` on every `play()` and `regenerate()` call — solely to extract this one field. This is:
- An extra I/O call per play operation.
- A cross-boundary dependency: the scene play path depends on story-level storage being consistent.
- An obstacle to scene autonomy — a scene cannot be played without a correctly populated story file.

Moving `user_character_id` to `scene/metadata.yaml` eliminates this dependency entirely.

## Decisions

1. **Remove `character_ids` from `story.yaml`**. The `characters/` directory is the character registry. Characters are loaded on-demand by scene reference; a missing file surfaces as a `NotFoundError`.

2. **Remove `user_character_id` from `story.yaml`**. Move it to `scene/metadata.yaml`. Each scene explicitly declares which character the player inhabits. This also opens the door for per-scene character evolution post-MVP.

3. **Drop the invariant** _"scene character_ids must always be a subset of story character_ids"_. Integrity is enforced implicitly at file load time.

4. **Standardize scene character field name to `character_ids`**. The storage doc and the Pydantic model (`SceneMetadataYaml`) use `characters_ids` (with an extra `s`), while the doc schema examples use `character_ids`. Resolve by renaming the model field and all YAML files to `character_ids` consistently.

5. **Choice-driven stories are out of scope** for this change. They use a separate data path and repository.

## New YAML Schemas

### story.yaml (after)

```yaml
id: "8fa93a9e-8dad-4fcb-b9cf-8e39f1707ec8"
title: "The Black Harbor"
scenes:
  - id: 1
    finished: true
  - id: 2
    finished: false
```

Removed fields: `character_ids`, `user_character_id`.

### scene/metadata.yaml (after)

```yaml
id: 3
finished: false
user_character_id: "max"
character_ids:
  - "captain-mora"
scene_description:
  general_scene_guide: "..."
  writing_style: "..."
scene_summary: null
context:
  - "..."
```

Added field: `user_character_id`.

## Expected Changes

### Storage models (`models/storage.py`)
- `StoryYaml`: remove `user_character_id`, remove `character_ids`
- `SceneMetadataYaml`: rename `characters_ids` → `character_ids`; add `user_character_id: str`

### Domain models (`models/domain.py`)
- `StoryMeta`: remove `user_character_id`, remove `character_ids`
- `SceneMetadata`: add `user_character_id: str`

### Repositories
- `StoryRepository.get_story()`: stop mapping the removed fields
- `SceneRepository.get_metadata()`: map `user_character_id` from YAML to domain model
- `SceneRepository.save_metadata()`: include `user_character_id` in serialization

### Services
- `ScenePlayService`:
  - Remove `StoryRepository` constructor dependency
  - In `play()` and `regenerate()`: replace `story_meta.user_character_id` with `metadata.user_character_id`; remove `story_repo.get_story()` call

### DI wiring (`api/dependencies.py`)
- `get_scene_play_service()`: remove `story_repo` parameter and `Depends(get_story_repository)` injection

### YAML data files
- `data/stories/<id>/story.yaml` and `data-test/stories/<id>/story.yaml`: remove `character_ids` and `user_character_id` fields
- `data/stories/<id>/scenes/<scene_id>/meta.yaml` and test equivalents: rename `characters_ids` → `character_ids`; add `user_character_id` field

### Tests
Files that reference `user_character_id` or `character_ids` on story-level models and need updating:
- `tests/models/test_storage.py`
- `tests/models/test_domain.py`
- `tests/models/test_api.py`
- `tests/repositories/test_story_repository.py`
- `tests/services/test_scene_play_service.py`
- `tests/services/test_story_query_service.py`

### Documentation
- `docks/dev/data_storage_structure.md`: update story.yaml schema and constraints, update scene metadata schema and constraints, remove the superseded repository invariant, update file responsibilities descriptions

## Out of Scope

- Choice-driven story character handling (separate data path, not changed)
- Post-MVP: character evolution between scenes (the schema change enables it; logic is not part of this work)
- In-app character management

## Open Questions

None — all design decisions are resolved.

## Risks

- **Data migration**: existing `story.yaml` files and `scene/meta.yaml` files must be updated manually before deploying the new code. Running old code against new files (or vice versa) will cause validation errors. The migration is a one-time manual edit per file; no automated migration script is planned.
- **Data migration**: existing `story.yaml` files and `scene/meta.yaml` files must be updated manually before deploying the new code. Running old code against new files (or vice versa) will cause validation errors. The migration is a one-time manual edit per file; no automated migration script is planned.
