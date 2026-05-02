# Task 004: Dev Scripts (install and run)

**Feature:** M1 — Project Skeleton
**Status:** TODO

## Description

Create `install.sh` and `run.sh` scripts (or a `Makefile`) at the project root that install dependencies and start both the backend and frontend with a single command. This satisfies the M1 exit criterion "both apps start from a single command".

## Scope

What IS included:
- `Makefile` at the project root with targets:
  - `make install` — creates Python venv in `backend/.venv`, installs `requirements.txt`, runs `npm install` in `frontend/`
  - `make dev` — starts `uvicorn` (backend) and `vite` (frontend) concurrently in the same terminal session
  - `make be` — starts backend only
  - `make fe` — starts frontend only
- Backend venv path: `backend/.venv`
- `.gitignore` entry for `backend/.venv` and `frontend/node_modules` added if not present

What is NOT included (deferred):
- Production build targets (`make build`, `make start`)
- Docker / containerization
- `install.sh` / `run.sh` shell scripts (Makefile covers the requirement)
- CI/CD pipeline configuration

## Deliverable

`Makefile` at the project root with `install` and `dev` targets verified to work on macOS.

```
Makefile          (project root)
.gitignore        (project root, created or updated)
```

## Acceptance Criteria

- [ ] `make install` completes without errors: venv exists at `backend/.venv`, `frontend/node_modules` is populated
- [ ] `make dev` starts both `uvicorn` on port 8000 and `vite` on port 5173 in parallel; both remain running
- [ ] `GET http://localhost:8000/health` returns `{"status": "ok"}` after `make dev`
- [ ] `http://localhost:5173` serves the React index page after `make dev`
- [ ] `make be` and `make fe` start only the respective app
- [ ] `backend/.venv` and `frontend/node_modules` are listed in `.gitignore`

## Test Notes

Manual smoke test:
```bash
make install
make dev
# in another terminal:
curl http://localhost:8000/health   # → {"status":"ok"}
# open http://localhost:5173        # → "Interactive Story" heading
```
Stop with `Ctrl+C`.

## Dependencies

001-backend-package-layout, 002-fastapi-app-health-check, 003-react-frontend-scaffold
