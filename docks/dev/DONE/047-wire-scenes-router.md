# Task 047: Wire Scenes Router to Services

**Feature:** M6 — Services and Full Integration
**Status:** TODO

## Description

Replace all hardcoded stub responses in `app/api/routers/scenes.py` with real service calls via FastAPI dependency injection. Five endpoints must be wired: get scene, play, edit message, delete message, and finish scene. All handlers must handle `KeyError` (→ 404), `ValueError("scene_finished")` (→ 409), and LLM exceptions (→ 502 for play only).

## Scope

What IS included:
- `GET /{story_id}/scenes/{scene_id}` → `SceneQueryService.get_scene()`
- `POST /{story_id}/scenes/{scene_id}/play` → `ScenePlayService.play()`
- `PUT /{story_id}/scenes/{scene_id}/messages/{message_id}` → `SceneMessageService.edit_message()`
- `DELETE /{story_id}/scenes/{scene_id}/messages/{message_id}` → `SceneMessageService.delete_message()`
- `POST /{story_id}/scenes/{scene_id}/finish` → `SceneLifecycleService.finish_scene()`
- Error mapping for all five endpoints:
  - `KeyError` → 404 `not_found`
  - `ValueError("scene_finished")` → 409 `scene_finished`
  - LLM exception in play → 502 `llm_error`
- All handlers converted to `async def`
- All hardcoded stubs removed

What is NOT included (deferred):
- Stories endpoints (task 046)
- Adding new scene endpoints

## Deliverable

Updated `backend/app/api/routers/scenes.py` with all five endpoints wired to their respective services.

```
backend/app/api/routers/scenes.py
```

## Acceptance Criteria

- [ ] `GET /scenes/{scene_id}` returns real scene data (metadata + messages from YAML)
- [ ] `POST /play` with valid content returns `user_message` and `assistant_message` from LLM
- [ ] `POST /play` on finished scene returns 409 with `scene_finished` error code
- [ ] `POST /play` when LLM fails returns 502 with `llm_error` error code and scene is unchanged
- [ ] `PUT /messages/{id}` updates message and returns updated message
- [ ] `DELETE /messages/{id}` deletes message and returns `{"success": true}`
- [ ] `POST /finish` marks scene finished and returns `{id, finished: true, scene_summary}`
- [ ] `POST /finish` on already-finished scene returns 409
- [ ] All handlers use `Depends(...)` — no direct service instantiation in handler bodies

## Test Notes

Manual verification with backend running against fixture data:

```bash
# Get scene
curl http://localhost:8000/api/stories/8fa93a9e-8dad-4fcb-b9cf-8e39f1707ec8/scenes/1

# Play
curl -X POST http://localhost:8000/api/stories/8fa93a9e-.../scenes/1/play \
  -H "Content-Type: application/json" -d '{"content": "I look around."}'

# Finish
curl -X POST http://localhost:8000/api/stories/8fa93a9e-.../scenes/1/finish \
  -H "Content-Type: application/json" -d '{"scene_summary": "The hero left."}'

# Finish again (expect 409)
curl -X POST http://localhost:8000/api/stories/8fa93a9e-.../scenes/1/finish \
  -H "Content-Type: application/json" -d '{"scene_summary": "Again."}'
```

## Dependencies

041 (SceneQueryService), 042 (ScenePlayService), 043 (SceneMessageService), 044 (SceneLifecycleService), 045 (dependencies.py)
