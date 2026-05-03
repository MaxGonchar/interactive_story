# Task 010: Message Edit and Delete Endpoint Stubs

**Feature:** M2 — API Contract Stubs
**Status:** TODO

## Description

Add two message-mutation stub endpoints to the scenes router:
- `PUT /stories/{story_id}/scenes/{scene_id}/messages/{message_id}` — edit a message
- `DELETE /stories/{story_id}/scenes/{scene_id}/messages/{message_id}` — delete a message

Both return hardcoded responses. No storage access. Pydantic validates the PUT request body.

## Scope

What IS included:
- `PUT` route: accepts `UpdateMessageRequest`, returns hardcoded `UpdateMessageResponse` (HTTP 200)
- `DELETE` route: no body, returns hardcoded `DeleteMessageResponse` (`{"success": true}`, HTTP 200)
- `message_id` and `scene_id` typed as `int`, `story_id` as `str`
- Pydantic 422 on invalid PUT body

What is NOT included (deferred):
- 404 when message/scene/story not found — M6
- 409 scene-finished guard — M6
- Real data mutation — M4/M6

## Deliverable

Two new route functions added to:

```
app/api/routers/scenes.py
```

## Acceptance Criteria

- [ ] `PUT /api/stories/{story_id}/scenes/{scene_id}/messages/{message_id}` with valid body returns HTTP 200 with `UpdateMessageResponse` shape
- [ ] PUT with `{"content": ""}` or `{}` returns HTTP 422
- [ ] `DELETE /api/stories/{story_id}/scenes/{scene_id}/messages/{message_id}` returns HTTP 200 with `{"success": true}`
- [ ] `response_model` declared on both routes
- [ ] Module imports without errors

## Test Notes

After task 012 (router wiring) is complete:

```bash
# PUT — expect 200
curl -X PUT http://localhost:8000/api/stories/any-id/scenes/3/messages/2 \
  -H "Content-Type: application/json" \
  -d '{"content": "I carefully inspect the lantern."}'

# PUT invalid — expect 422
curl -X PUT http://localhost:8000/api/stories/any-id/scenes/3/messages/2 \
  -H "Content-Type: application/json" \
  -d '{"content": ""}'

# DELETE — expect 200
curl -X DELETE http://localhost:8000/api/stories/any-id/scenes/3/messages/2
```

## Dependencies

006-api-pydantic-models, 008-get-scene-endpoint-stub (scenes router file must exist)
