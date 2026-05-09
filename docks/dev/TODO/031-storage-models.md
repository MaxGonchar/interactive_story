# Task 031: Storage Models

**Feature:** M4 — Data Access Layer
**Status:** TODO

## Description

Define `app/models/storage.py` containing Pydantic models that mirror the YAML file schemas exactly. Repositories parse raw YAML dicts into these models first, then map them to domain objects. This separates storage concerns from domain logic.

## Scope

What IS included:
- `StoriesIndex` — wraps `list[StoriesIndexEntry]` (field: `stories`)
- `StoriesIndexEntry` — id, title, order
- `StoryYaml` — id, title, character_ids, scenes (list of `SceneRefYaml`), active_scene_id
- `SceneRefYaml` — id, order
- `CharacterYaml` — id, story_id, name, and all optional character fields matching the YAML schema
- `SceneMetadataYaml` — id, story_id, finished, character_ids, scene_description (`SceneDescriptionYaml`), scene_summary
- `SceneDescriptionYaml` — entry_point, general_scene_guide, writing_style
- `MessagesYaml` — wraps `list[MessageYaml]` (field: `messages`)
- `MessageYaml` — id, role, content

What is NOT included (deferred):
- Mapping logic to domain models (done inside repositories)
- Any write serialisation helpers (done by `yaml_storage.py`)

## Deliverable

`backend/app/models/storage.py` — a finished module with all nine Pydantic models.

```
backend/app/models/storage.py
```

## Acceptance Criteria

- [ ] All nine models are importable from `app.models.storage`
- [ ] `StoriesIndex(**yaml.safe_load(open("data/stories/index.yaml")))` parses the fixture file without error (task 026 fixture required)
- [ ] `MessagesYaml(**yaml.safe_load(open("data/.../messages.yaml")))` parses the fixture messages file without error
- [ ] `SceneMetadataYaml.scene_summary` is `Optional[str]` (allows null from YAML)
- [ ] Models use `model_validator` or `field_validator` only where strictly necessary to enforce YAML constraints; keep validation minimal

## Test Notes

Instantiate each model with data loaded from fixture files (task 026). Assert no `ValidationError`. Test that a missing required field raises `ValidationError`.

## Dependencies

026, 030
