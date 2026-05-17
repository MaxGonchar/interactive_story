# Task 045: FastAPI Dependency Injection File

**Feature:** M6 — Services and Full Integration
**Status:** TODO

## Description

Create `app/api/dependencies.py` containing FastAPI dependency provider functions for all five services and their repository/LLM dependencies. Routers import these providers and declare them via `Depends()`. This centralises instantiation and makes each service trivially replaceable for testing.

## Scope

What IS included:
- `dependencies.py` with one provider function per injectable:
  - `get_story_repository() -> StoryRepository`
  - `get_scene_repository() -> SceneRepository`
  - `get_character_repository() -> CharacterRepository`
  - `get_scene_llm_client() -> SceneLLMClient`
  - `get_story_query_service(repo=Depends(get_story_repository)) -> StoryQueryService`
  - `get_scene_query_service(...) -> SceneQueryService`
  - `get_scene_play_service(...) -> ScenePlayService`
  - `get_scene_message_service(...) -> SceneMessageService`
  - `get_scene_lifecycle_service(...) -> SceneLifecycleService`
- All providers are plain functions (not `@lru_cache`); instantiation is per-request

What is NOT included (deferred):
- Router wiring (tasks 046, 047)
- Any caching or singleton logic

## Deliverable

A finished module at `backend/app/api/dependencies.py`.

```
backend/app/api/dependencies.py
```

## Acceptance Criteria

- [ ] All five service provider functions exist and return the correct type
- [ ] All repository and LLM client providers exist
- [ ] Service providers receive their dependencies via `Depends()` — no hardcoded instantiation inside service providers
- [ ] File imports without errors (`python -c "from app.api.dependencies import get_story_query_service"`)
- [ ] No unit tests required; verify by importing in a Python shell

## Test Notes

Manual verification: activate the backend venv and run:

```bash
cd backend
python -c "from app.api.dependencies import get_story_query_service, get_scene_play_service; print('OK')"
```

## Dependencies

040 (StoryQueryService), 041 (SceneQueryService), 042 (ScenePlayService), 043 (SceneMessageService), 044 (SceneLifecycleService)
