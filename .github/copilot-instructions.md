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

## Frontend Styles

Full reference: [`docks/dev/frontend_styles_guide.md`](../docks/dev/frontend_styles_guide.md)

Four rules — follow them for every component you create or modify:

1. **No magic values.** Every color, spacing size, font, and radius must reference a CSS variable token (e.g. `var(--accent)`, `var(--space-sm)`). Never write raw hex, raw `px` sizes for spacing/radius, or raw color names.
2. **CSS classes for static styles.** Layout, spacing, color, and typography that don't depend on runtime props or state belong in a CSS class in `frontend/src/index.css`.
3. **Inline `style={{}}` only for dynamic values.** Use inline styles exclusively for values computed from props or state (e.g. `alignItems: isUser ? 'flex-end' : 'flex-start'`).
4. **`styles.js` for shared JS-side style objects.** If the same style object is needed in two or more components, export it from `frontend/src/styles.js` and import it — do not duplicate.

Do not introduce CSS Modules, styled-components, Tailwind, or any other styling tooling.
