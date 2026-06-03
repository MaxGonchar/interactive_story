# Project: Interactive Story

## Stack
- Backend: FastAPI + Python, YAML file storage, LangChain/Venice AI
- Frontend: React + Vite
- Tests: pytest (backend only)

## Environment Setup
- Python venv is at `backend/.venv` — **never install packages globally**
- Install all deps: `make install`
- If venv is missing, run `make install` before anything else

## Commands (always run from project root)
| Task | Command |
|---|---|
| Install deps | `make install` |
| Run backend | `make be` |
| Run frontend | `make fe` |
| Run both | `make dev` |
| Run backend tests | `make test-be` |

## Testing Rules
- Always run tests via `make test-be` from the **project root**
- Do NOT run `pytest` directly — it may pick up the wrong interpreter
- Do NOT run pytest from inside the `backend/` directory
- Test files live in `backend/tests/`, mirroring the `backend/app/` structure

## Python Execution
- Use `backend/.venv/bin/python` for one-off scripts
- Use `backend/.venv/bin/pip` if you must install manually (prefer `make install`)

## Key Docs
- `docks/dev/plan.md` — milestone plan and current progress
- `docks/dev/requirements.md` — functional requirements
- `docks/dev/endpoints.md` — API contract
- `docks/dev/data_storage_structure.md` — YAML storage format
- `docks/dev/progect_structure.md` — package layout and module responsibilities
