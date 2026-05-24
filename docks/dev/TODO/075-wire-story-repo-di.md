# Task 075: Inject StoryRepository into ScenePlayService via Dependency Injection

**Feature:** System prompt correction — DI wiring
**Status:** TODO

## Description

`ScenePlayService` now requires a `StoryRepository` constructor argument (added in task 074). The FastAPI dependency function `get_scene_play_service()` in `dependencies.py` must be updated to construct and inject a `StoryRepository` instance, keeping the dependency graph consistent.

## Scope

What IS included:
- `backend/app/api/dependencies.py`: update `get_scene_play_service()` to instantiate `StoryRepository` and pass it to `ScenePlayService`

What is NOT included (deferred):
- Any other dependency functions
- Changes to `ScenePlayService` itself (covered by task 074)

## Deliverable

Updated `backend/app/api/dependencies.py` — `get_scene_play_service()` constructs `StoryRepository` and passes it as the `story_repo` argument:

```python
def get_scene_play_service() -> ScenePlayService:
    return ScenePlayService(
        scene_repo=SceneRepository(),
        character_repo=CharacterRepository(),
        llm_client=get_scene_llm_client(),
        story_repo=StoryRepository(),
    )
```

```
backend/app/api/dependencies.py
```

## Acceptance Criteria

- [ ] `get_scene_play_service()` passes a `StoryRepository` instance as `story_repo` to `ScenePlayService`
- [ ] `StoryRepository` is imported in `dependencies.py` (if not already present)
- [ ] The app starts without errors (`uvicorn app.main:app`)
- [ ] `POST /stories/{story_id}/scenes/{scene_id}/play` returns a valid response end-to-end (manual smoke test)
- [ ] All existing tests still pass (`pytest backend/`)

## Test Notes

Manual smoke test:
1. Start the backend: `cd backend && uvicorn app.main:app --reload`
2. `POST /api/stories/{story_id}/scenes/{scene_id}/play` with `{"content": "hello"}` — expect 200 with `user_message` and `assistant_message` fields.

Unit test confirmation:
```
pytest backend/ -v
```

## Dependencies

074
