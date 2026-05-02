# Task 002: FastAPI App Entry Point and Health Check

**Feature:** M1 — Project Skeleton
**Status:** TODO

## Description

Create `backend/app/main.py` — the FastAPI application entry point. The app must boot without errors and expose `GET /health` returning `{"status": "ok"}` with HTTP 200. This is the only exit criterion for the backend portion of M1.

## Scope

What IS included:
- `backend/app/main.py` with a `FastAPI` app instance
- `GET /health` route returning `{"status": "ok"}`
- CORS middleware configured for local development (allow `http://localhost:5173` and `http://localhost:3000`)
- `backend/.env` loading via `python-dotenv` at startup (loads from project root or `backend/.env`)

What is NOT included (deferred):
- Any router registration (tasks in M2)
- Any service or repository wiring
- Any model definitions
- Production CORS policy

## Deliverable

Finished `backend/app/main.py` that boots and serves the health check.

```
backend/app/main.py
```

## Acceptance Criteria

- [ ] `uvicorn app.main:app --reload` starts without errors from the `backend/` directory
- [ ] `GET http://localhost:8000/health` returns HTTP 200 with body `{"status": "ok"}`
- [ ] Swagger UI is accessible at `http://localhost:8000/docs`
- [ ] CORS headers allow requests from `http://localhost:5173`

## Test Notes

Manual smoke test:
```bash
cd backend
uvicorn app.main:app --reload
curl http://localhost:8000/health
# expected: {"status":"ok"}
```

## Dependencies

001-backend-package-layout
