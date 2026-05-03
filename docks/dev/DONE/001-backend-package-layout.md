# Task 001: Backend Package Layout

**Feature:** M1 — Project Skeleton
**Status:** TODO

## Description

Create the full backend directory structure for the FastAPI application. This task produces all package directories with `__init__.py` files and a top-level `requirements.txt`, so every subsequent backend task has the correct import paths available from the start.

## Scope

What IS included:
- `backend/` root directory
- `backend/app/__init__.py`
- `backend/app/api/__init__.py`
- `backend/app/api/routers/__init__.py`
- `backend/app/services/__init__.py`
- `backend/app/repositories/__init__.py`
- `backend/app/llm/__init__.py`
- `backend/app/models/__init__.py`
- `backend/app/utils/__init__.py`
- `backend/requirements.txt` with `fastapi`, `uvicorn[standard]`, `pydantic`, `python-dotenv`, `pyyaml`, `langchain` pinned to minimum workable versions

What is NOT included (deferred):
- Any module content beyond empty `__init__.py` files
- Virtual environment setup (handled by install script, task 004)
- `main.py` (task 002)

## Deliverable

All package directories created with empty `__init__.py` files; `requirements.txt` present.

```
backend/
  app/
    __init__.py
    api/
      __init__.py
      routers/
        __init__.py
    services/
      __init__.py
    repositories/
      __init__.py
    llm/
      __init__.py
    models/
      __init__.py
    utils/
      __init__.py
  requirements.txt
```

## Acceptance Criteria

- [ ] All directories listed above exist in the repository
- [ ] Every `__init__.py` file is present (can be empty)
- [ ] `requirements.txt` lists at minimum: `fastapi`, `uvicorn[standard]`, `pydantic`, `python-dotenv`, `pyyaml`, `langchain`
- [ ] `python -c "from app.api import routers"` succeeds from `backend/` after `pip install -r requirements.txt`

## Test Notes

Manual: activate a virtual environment, `pip install -r requirements.txt`, then run:
```
cd backend
python -c "import app.api.routers; import app.services; import app.repositories; import app.llm; import app.models; import app.utils; print('OK')"
```
Expected output: `OK` with no errors.

## Dependencies

none
