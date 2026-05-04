# Task 008: Get Scene Endpoint Stub

**Feature:** M2 — API Contract Stubs
**Status:** TODO

## Description

Add the `GET /stories/{story_id}/scenes/{scene_id}` stub endpoint to the scenes router. Returns a hardcoded `SceneDetailResponse` with full message history. No data access — all data is hardcoded.

## Scope

What IS included:
- `app/api/routers/scenes.py` created with an `APIRouter`
- `GET /stories/{story_id}/scenes/{scene_id}` returning a hardcoded `SceneDetailResponse`
- Hardcoded response includes `scene_description`, `scene_summary: null`, and two example messages

What is NOT included (deferred):
- POST /play, PUT/DELETE message, POST /finish — handled in tasks 009–011
- Real data access — M4

## Deliverable

```
app/api/routers/scenes.py
```

The router must:
- Use `APIRouter(prefix="/stories", tags=["scenes"])`
- Import `SceneDetailResponse`, `ErrorResponse` from `app.models.api`
- Declare `response_model=SceneDetailResponse` on the route

## Acceptance Criteria

- [ ] `GET /api/stories/{story_id}/scenes/{scene_id}` returns HTTP 200
- [ ] Response body matches the `SceneDetailResponse` shape from `endpoints.md` exactly (includes `scene_description` object, `scene_summary: null`, `messages` list)
- [ ] `scene_id` path param is typed as `int`
- [ ] `story_id` path param is typed as `str`
- [ ] Module imports without errors

## Test Notes

After task 012 (router wiring) is complete:

```bash
curl http://localhost:8000/api/stories/8fa93a9e-8dad-4fcb-b9cf-8e39f1707ec8/scenes/3
```

Expected: HTTP 200, body matches `endpoints.md` scene detail shape.

## Dependencies

006-api-pydantic-models
