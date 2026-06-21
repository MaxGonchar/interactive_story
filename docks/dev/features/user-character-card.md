# Feature: User Character Card

**Status**: Draft  
**Date**: 2026-06-21

## Summary
Each story has a required user character card stored in the `characters/` directory alongside NPCs. The card uses the same free-form `features` dict format as NPC character cards, with `name` as the only mandatory field. The story metadata file (`story.yaml`) holds a required `user_character_id` reference. The system prompt's hardcoded protagonist block is replaced with the card's dynamically rendered text.

## Value
- The protagonist persona is currently hardcoded as "Emma" in the system prompt template, blocking any role customisation.
- With this feature, the user can define a different character per story by editing a YAML file, same as NPC cards.
- Fits the MVP goal of fast iteration: no UI needed, no new file format, reuses the existing `CharacterCard` model and `to_prompt_text()` rendering already built for NPCs.

**Success criteria**: Starting a scene play with a story that has `user_character_id` set causes the system prompt to render the user character's card content dynamically instead of the hardcoded text.

## Scope

### In scope (first iteration)
- `user_character_id` added as a required field to `story.yaml`.
- User character YAML file stored in `characters/<id>.yaml` — identical format to NPC cards.
- `StoryYaml` storage model gains `user_character_id: str`.
- `StoryMeta` domain model gains `user_character_id: str`.
- `StoryRepository.get_story()` passes `user_character_id` through.
- `SceneContext` gains `user_character: CharacterCard`.
- `ScenePlayService.play()` and `ScenePlayService.regenerate()` load the user character and include it in `SceneContext`.
- `PromptBuilder` replaces the hardcoded Emma block with a `{{ user_character_profile }}` template variable rendered by `user_character.to_prompt_text()`.
- `StoryDetail` API response model gains `user_character_id: str`.
- `GET /api/stories/{story_id}` response includes `user_character_id`.
- Updated tests.
- Update fixture YAML files in `data/` and `data-test/`.

### Out of scope / future
- API endpoint to create or update the user character card.
- UI for editing the user character card.
- Per-scene user character override (same card for all scenes in a story).
- Making `user_character_id` optional (every story is expected to have a protagonist).

## User Flow
This feature has no visible UI change. The author prepares data manually:

1. Author creates `data/stories/<story_id>/characters/<character_id>.yaml` with `name` and any desired `features`.
2. Author sets `user_character_id: <character_id>` in `story.yaml`.
3. User opens the scene and plays. The system prompt now contains the user character's card instead of the hardcoded Emma text.

## API Changes

### Modified: `GET /api/stories/{story_id}`

`user_character_id` is added to the response body.

**Response 200 — before**
```json
{
    "data": {
        "id": "...",
        "title": "The Black Harbor",
        "scenes": [...],
        "active_scene_id": 3
    }
}
```

**Response 200 — after**
```json
{
    "data": {
        "id": "...",
        "title": "The Black Harbor",
        "scenes": [...],
        "active_scene_id": 3,
        "user_character_id": "emma"
    }
}
```

No other endpoints are affected.

## Data Changes

### `story.yaml` — new required field

```yaml
id: "8fa93a9e-8dad-4fcb-b9cf-8e39f1707ec8"
title: "Mila and Sarah"
user_character_id: "emma"
character_ids:
  - mila
  - sarah
  - emma
scenes:
  - id: 1
    finished: false
```

**Constraints:**
- `user_character_id` is required; story fails to load if absent.
- `user_character_id` must have a matching file in `characters/<id>.yaml`.
- The user character can (but does not have to) appear in `character_ids`; it is loaded separately and injected into the system prompt under `# User's Character Profile`, not under `# Character Profiles (NPCs)`.

### User character YAML — format (same as NPC cards)

```yaml
id: "emma"
name: "Emma"
features:
  appearance: "18 years old. Long wavy blonde hair, bright blue eyes."
  traits:
    - "Curious"
    - "Bold"
memory: []
```

No new YAML schema. Reuses the existing character card format.

## Backend Changes

### `app/models/storage.py`
- `StoryYaml`: add `user_character_id: str`.

### `app/models/domain.py`
- `StoryMeta`: add `user_character_id: str`.

### `app/repositories/story_repository.py`
- `StoryRepository.get_story()`: read `story.user_character_id` and pass it through when constructing `StoryMeta`.

### `app/llm/models.py`
- `SceneContext`: add `user_character: CharacterCard`.

### `app/services/scene_play_service.py`
- `ScenePlayService.play()`: after loading `story_meta`, call `await self._character_repo.get_character(story_id, story_meta.user_character_id)` and include the result as `user_character` in `SceneContext`.
- `ScenePlayService.regenerate()`: same — load and pass `user_character` to `SceneContext`.

### `app/llm/prompt_builder.py`
- Remove the hardcoded Emma block from `_SYSTEM_PROMPT_TEMPLATE`.
- Add `{{ user_character_profile }}` variable in its place (restoring the original design intent from task 038).
- Update `PromptBuilder.build_system_prompt()` to pass `user_character_profile=context.user_character.to_prompt_text()` when rendering the template.

### `app/models/api.py`
- `StoryDetail`: add `user_character_id: str`.

### `app/api/routers/stories.py`
- `get_story` handler: include `user_character_id` in the response dict.

## Frontend Changes
None in this iteration. The `user_character_id` field is now present in the story detail response but no frontend component uses it yet.

## Tests to Update

| File | Change |
|---|---|
| `tests/models/test_storage.py` | Add `user_character_id` to `StoryYaml` fixture; assert it round-trips correctly |
| `tests/models/test_domain.py` | Add `user_character_id` to `StoryMeta` fixture and assertions |
| `tests/repositories/test_story_repository.py` | Add `user_character_id` to YAML fixture; assert `StoryMeta.user_character_id` is set correctly |
| `tests/services/test_scene_play_service.py` | Stub `character_repo.get_character` to return a user character; assert it is included in `SceneContext` |
| `tests/llm/test_prompt_builder.py` | Pass `user_character` in `SceneContext`; add test that user character name appears under `# User's Character Profile`; assert hardcoded "Emma" is gone |
| `tests/llm/test_models.py` | Update `SceneContext` construction to include `user_character` |

## Open Questions
None — all design decisions resolved during discussion.

## Risks
- Existing `story.yaml` files in `data/` and `data-test/` do not have `user_character_id`; Pydantic will raise a validation error on load until the YAML files are updated. This is intentional and serves as the migration checklist.
- `character_ids` in `story.yaml` lists characters used by scenes. Whether `user_character_id` must also appear in `character_ids` is left to authoring convention, not enforced by code in this iteration.
