# Task 030: Domain Models

**Feature:** M4 — Data Access Layer
**Status:** TODO

## Description

Define `app/models/domain.py` containing Pydantic models that represent the in-memory domain objects returned by repositories. These are the application's internal data types, decoupled from both the API response shapes and the YAML storage layout.

## Scope

What IS included:
- `StoryIndexItem` — id, title, order
- `StoryMeta` — id, title, character_ids, scene_ids (ordered), active_scene_id
- `SceneRef` — id, order (used inside StoryMeta)
- `CharacterCard` — id, story_id, name, appearance, traits, speech_patterns, body_language, likes, fears, memory
- `SceneMetadata` — id, story_id, finished, character_ids, scene_description (nested), scene_summary
- `SceneDescription` — entry_point, general_scene_guide, writing_style
- `Message` — id, role (Literal["user","assistant"]), content

What is NOT included (deferred):
- API response models (already in `app/models/api.py`)
- Storage-layer models (`app/models/storage.py`, task 031)
- Any business logic or validation beyond field types

## Deliverable

`backend/app/models/domain.py` — a finished module with all seven Pydantic models.

```
backend/app/models/domain.py
```

## Acceptance Criteria

- [ ] All seven models are importable from `app.models.domain`
- [ ] `Message.role` is constrained to `Literal["user", "assistant"]`
- [ ] `SceneMetadata.scene_summary` allows `None`
- [ ] `CharacterCard` optional list fields (`appearance`, `traits`, `speech_patterns`, `body_language`, `likes`, `fears`, `memory`) accept empty lists or None without error
- [ ] Models are plain Pydantic `BaseModel` subclasses (no ORM mode, no validators beyond type constraints)

## Test Notes

Import each model and instantiate with valid data; assert no ValidationError. Instantiate `Message` with an invalid role and assert `ValidationError` is raised.

## Dependencies

none
