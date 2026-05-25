# Task 066: Add Regenerate Endpoint to Scenes Router

**Feature:** Regenerate last assistant message
**Status:** TODO

## Description

Add `POST /api/stories/{story_id}/scenes/{scene_id}/regenerate` to `backend/app/api/routers/scenes.py`. The endpoint takes no request body, delegates to `ScenePlayService.regenerate`, and returns the updated assistant message. Error mapping follows the existing pattern in the router.

## Scope

What IS included:
- New `@router.post("/{story_id}/scenes/{scene_id}/regenerate", response_model=RegenerateResponse)` handler
- No request body
- Return shape: `{"data": {"assistant_message": {"id": ..., "role": "assistant", "content": "..."}}}`
- Error mapping:
  - `KeyError` → 404 `not_found`
  - `ValueError("scene_finished")` → 409 `scene_finished`
  - `ValueError("no_assistant_message")` → 409 `no_assistant_message`
  - Any other exception → 502 `llm_error`
- `RegenerateResponse` imported from `app.models.api`
- `get_scene_play_service` dependency reused (no new DI factory needed)

What is NOT included (deferred):
- Service implementation (task 065)
- Response model definition (task 064)
- Frontend wiring

## Deliverable

New route handler added to `backend/app/api/routers/scenes.py`:

```
backend/app/api/routers/scenes.py
```

## Acceptance Criteria

- [ ] `POST /api/stories/{story_id}/scenes/{scene_id}/regenerate` is registered and appears in `/docs`
- [ ] Returns 200 `{"data": {"assistant_message": {id, role, content}}}` on success
- [ ] Returns 404 when story or scene is not found
- [ ] Returns 409 with code `scene_finished` when scene is finished
- [ ] Returns 409 with code `no_assistant_message` when no assistant message exists
- [ ] Returns 502 on LLM failure
- [ ] All existing backend tests still pass

## Test Notes

Manual: `curl -X POST http://localhost:8000/api/stories/{id}/scenes/{id}/regenerate` on an active scene with at least one assistant message. Verify response shape and HTTP status codes for each error case via Swagger UI at `/docs`.

## Dependencies

- 064 (RegenerateResponse model)
- 065 (ScenePlayService.regenerate method)
