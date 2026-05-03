# Task 012: Register Routers in Main App

**Feature:** M2 — API Contract Stubs
**Status:** TODO

## Description

Register the `stories` and `scenes` routers in `app/main.py` under the `/api` prefix. Also register a global exception handler that converts unhandled exceptions into the standard `ErrorResponse` shape. This wiring task makes all 7 stub endpoints reachable.

## Scope

What IS included:
- `app.include_router(stories_router, prefix="/api")` in `app/main.py`
- `app.include_router(scenes_router, prefix="/api")` in `app/main.py`
- A global `@app.exception_handler` (or FastAPI middleware) that catches unhandled `HTTPException` and returns `ErrorResponse` JSON, preserving the status code
- CORS middleware configured for local dev (`http://localhost:5173`)

What is NOT included (deferred):
- Any new router or endpoint — tasks 007–011
- Service or repository wiring — M6
- Production CORS configuration

## Deliverable

Modified file:

```
app/main.py
```

After this task, all 7 endpoints are reachable at `http://localhost:8000/api/...` and all error responses use the standard `ErrorResponse` shape.

## Acceptance Criteria

- [ ] `uvicorn app.main:app --reload` starts without errors
- [ ] `GET /api/stories` returns HTTP 200 (stub data)
- [ ] `GET /api/stories/{id}` returns HTTP 200 (stub data)
- [ ] `GET /api/stories/{id}/scenes/{id}` returns HTTP 200 (stub data)
- [ ] `POST /api/stories/{id}/scenes/{id}/play` with valid body returns HTTP 200
- [ ] `PUT /api/stories/{id}/scenes/{id}/messages/{id}` with valid body returns HTTP 200
- [ ] `DELETE /api/stories/{id}/scenes/{id}/messages/{id}` returns HTTP 200
- [ ] `POST /api/stories/{id}/scenes/{id}/finish` with valid body returns HTTP 200
- [ ] All 7 endpoints visible in Swagger UI at `http://localhost:8000/docs`
- [ ] Sending an invalid request body returns JSON with shape `{"detail": [...]}` (FastAPI default 422) — acceptable at stub stage; full `ErrorResponse` wrapping deferred to M6

## Test Notes

Start the backend and verify each endpoint manually:

```bash
cd backend
uvicorn app.main:app --reload
```

Then run the curl commands documented in tasks 007–011. Check `/docs` to confirm all 7 routes appear.

## Dependencies

007-stories-router-stubs, 008-get-scene-endpoint-stub, 009-play-endpoint-stub, 010-message-edit-delete-stubs, 011-finish-scene-endpoint-stub
