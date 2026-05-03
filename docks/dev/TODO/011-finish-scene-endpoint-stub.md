# Task 011: Finish Scene Endpoint Stub

**Feature:** M2 — API Contract Stubs
**Status:** TODO

## Description

Add the `POST /stories/{story_id}/scenes/{scene_id}/finish` stub endpoint to the scenes router. Accepts a `FinishSceneRequest` body, validates it via Pydantic, and returns a hardcoded `FinishSceneResponse`. No storage writes.

## Scope

What IS included:
- `POST /stories/{story_id}/scenes/{scene_id}/finish` added to `app/api/routers/scenes.py`
- Request body parsed and validated as `FinishSceneRequest` (scene_summary: non-empty, max 2000 chars)
- Hardcoded `FinishSceneResponse` returned (HTTP 200) with `finished: true` and the echoed summary
- FastAPI's automatic 422 on Pydantic validation failure

What is NOT included (deferred):
- 409 guard for already-finished scene — M6
- Real persistence of the finished state — M4/M6

## Deliverable

New route function added to:

```
app/api/routers/scenes.py
```

Hardcoded response must mirror the `endpoints.md` shape:

```json
{
  "data": {
    "id": 3,
    "finished": true,
    "scene_summary": "<echoed from request>"
  }
}
```

The stub may echo `request.scene_summary` back into the response.

## Acceptance Criteria

- [ ] `POST /api/stories/{story_id}/scenes/{scene_id}/finish` with valid body returns HTTP 200
- [ ] Response body matches `FinishSceneResponse` shape with `data.id`, `data.finished = true`, `data.scene_summary`
- [ ] Sending `{"scene_summary": ""}` or `{}` returns HTTP 422
- [ ] Sending a summary longer than 2000 characters returns HTTP 422
- [ ] `response_model=FinishSceneResponse` declared on the route

## Test Notes

After task 012 (router wiring) is complete:

```bash
# Valid — expect 200
curl -X POST http://localhost:8000/api/stories/any-id/scenes/3/finish \
  -H "Content-Type: application/json" \
  -d '{"scene_summary": "The hero discovered the map and escaped the harbor."}'

# Empty summary — expect 422
curl -X POST http://localhost:8000/api/stories/any-id/scenes/3/finish \
  -H "Content-Type: application/json" \
  -d '{"scene_summary": ""}'
```

## Dependencies

006-api-pydantic-models, 008-get-scene-endpoint-stub (scenes router file must exist)
