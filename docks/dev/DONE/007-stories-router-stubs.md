# Task 007: Stories Router Stubs

**Feature:** M2 — API Contract Stubs
**Status:** TODO

## Description

Create `app/api/routers/stories.py` with two hardcoded stub endpoints for listing all stories and fetching a single story's detail. No database or YAML access — all responses are hardcoded literals that match `endpoints.md` shapes exactly.

## Scope

What IS included:
- `app/api/routers/stories.py` with an `APIRouter`
- `GET /stories` — returns a hardcoded list of one `StoryListItem`
- `GET /stories/{story_id}` — returns a hardcoded `StoryDetailResponse`; 404 is never triggered in the stub

What is NOT included (deferred):
- Real data access (YAML / repositories) — M4
- Business logic — M6
- Any other endpoint — handled in tasks 008–011

## Deliverable

```
app/api/routers/stories.py
```

The router must:
- Use `APIRouter(prefix="/stories", tags=["stories"])`
- Import and use `StoryListResponse`, `StoryDetailResponse`, `ErrorResponse` from `app.models.api`
- Return hardcoded data that matches the exact JSON shapes in `endpoints.md`

## Acceptance Criteria

- [ ] `GET /api/stories` returns HTTP 200 with body `{"data": [{"id": "...", "title": "..."}]}`
- [ ] `GET /api/stories/{story_id}` returns HTTP 200 with body matching the `StoryDetailResponse` shape including `scenes` list and `active_scene_id`
- [ ] Response models are declared on each route (`response_model=...`)
- [ ] Module imports without errors: `python -c "from app.api.routers.stories import router"`
- [ ] Swagger UI (`/docs`) shows both endpoints under the "stories" tag after router is registered

## Test Notes

After task 012 (router wiring) is complete, verify manually:

```bash
curl http://localhost:8000/api/stories
curl http://localhost:8000/api/stories/8fa93a9e-8dad-4fcb-b9cf-8e39f1707ec8
```

Both should return 200 with valid JSON matching `endpoints.md`.

## Dependencies

006-api-pydantic-models
