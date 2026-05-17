# Task 046: Wire Stories Router to Services

**Feature:** M6 — Services and Full Integration
**Status:** TODO

## Description

Replace the hardcoded stub responses in `app/api/routers/stories.py` with real calls to `StoryQueryService` via FastAPI dependency injection. Handle `KeyError` (story not found) and map it to a 404 `ErrorResponse`.

## Scope

What IS included:
- `GET /api/stories` → `StoryQueryService.list_stories()`
- `GET /api/stories/{story_id}` → `StoryQueryService.get_story(story_id)`
- 404 error response when `get_story` raises `KeyError`
- Both handlers converted to `async def`

What is NOT included (deferred):
- Scene endpoints (task 047)
- Adding new story endpoints

## Deliverable

Updated `backend/app/api/routers/stories.py` with both endpoints wired to `StoryQueryService`.

```
backend/app/api/routers/stories.py
```

## Acceptance Criteria

- [ ] `GET /api/stories` returns data read from YAML (fixture story appears in list)
- [ ] `GET /api/stories/{story_id}` returns correct story detail for valid id
- [ ] `GET /api/stories/{story_id}` returns 404 with `{"error": {"code": "not_found", ...}}` for unknown id
- [ ] Both handlers use `Depends(get_story_query_service)` — no direct repository instantiation
- [ ] All hardcoded stub data removed from the router

## Test Notes

Manual verification with the backend running:

```bash
curl http://localhost:8000/api/stories
curl http://localhost:8000/api/stories/8fa93a9e-8dad-4fcb-b9cf-8e39f1707ec8
curl http://localhost:8000/api/stories/nonexistent-id   # expect 404
```

## Dependencies

040 (StoryQueryService), 045 (dependencies.py)
