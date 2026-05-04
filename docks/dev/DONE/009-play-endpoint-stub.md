# Task 009: Play Endpoint Stub

**Feature:** M2 — API Contract Stubs
**Status:** TODO

## Description

Add the `POST /stories/{story_id}/scenes/{scene_id}/play` stub endpoint to the scenes router. Accepts a `PlayRequest` body, validates it via Pydantic, and returns a hardcoded `PlayResponse` containing a user message and an assistant message. No LLM call, no storage.

## Scope

What IS included:
- `POST /stories/{story_id}/scenes/{scene_id}/play` added to `app/api/routers/scenes.py`
- Request body parsed and validated as `PlayRequest` (content: non-empty, max 4000 chars)
- Hardcoded `PlayResponse` returned on success (HTTP 200)
- FastAPI's automatic 422 response on Pydantic validation failure

What is NOT included (deferred):
- LLM call — M5
- Scene-finished 409 guard — M6
- Actual message persistence — M4/M6

## Deliverable

New route function added to:

```
app/api/routers/scenes.py
```

Hardcoded response must mirror the `endpoints.md` shape:

```json
{
  "data": {
    "user_message": {"id": 2, "role": "user", "content": "<echoed from request>"},
    "assistant_message": {"id": 3, "role": "assistant", "content": "A lantern swings near a wooden post..."}
  }
}
```

The stub may echo `request.content` back into `user_message.content` so testers can see the input round-trip.

## Acceptance Criteria

- [ ] `POST /api/stories/{story_id}/scenes/{scene_id}/play` with valid JSON body returns HTTP 200
- [ ] Response body matches `PlayResponse` shape with `data.user_message` and `data.assistant_message`
- [ ] Sending `{"content": ""}` or `{}` returns HTTP 422 (Pydantic validation error)
- [ ] Sending `{"content": "x" * 4001}` returns HTTP 422
- [ ] `response_model=PlayResponse` declared on the route

## Test Notes

After task 012 (router wiring) is complete:

```bash
# Valid request — expect 200
curl -X POST http://localhost:8000/api/stories/any-id/scenes/3/play \
  -H "Content-Type: application/json" \
  -d '{"content": "I look for the nearest light source."}'

# Empty content — expect 422
curl -X POST http://localhost:8000/api/stories/any-id/scenes/3/play \
  -H "Content-Type: application/json" \
  -d '{"content": ""}'
```

## Dependencies

006-api-pydantic-models, 008-get-scene-endpoint-stub (scenes router file must exist)
