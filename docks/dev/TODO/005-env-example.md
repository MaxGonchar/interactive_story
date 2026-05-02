# Task 005: Environment Configuration File

**Feature:** M1 — Project Skeleton
**Status:** TODO

## Description

Create `backend/.env.example` documenting every environment variable the backend application requires or will require through M6. This file is the single source of truth for configuration; developers copy it to `backend/.env` and fill in real values. No secrets are committed.

## Scope

What IS included:
- `backend/.env.example` with all required keys and inline comments explaining each
- Variables to document at minimum:
  - `LLM_PROVIDER` — LLM provider identifier (e.g. `openai`)
  - `LLM_MODEL` — model name (e.g. `gpt-4o`)
  - `OPENAI_API_KEY` — API key (value left blank)
  - `DATA_DIR` — path to the YAML data directory (default: `../data`)
  - `LOG_LEVEL` — logging verbosity (default: `INFO`)
  - `CORS_ORIGINS` — comma-separated allowed origins (default: `http://localhost:5173`)
- `backend/.env` added to `.gitignore` (project root) if not already present

What is NOT included (deferred):
- Actual secret values
- Frontend environment variables (no `.env.example` needed for frontend in M1)
- Secret rotation or vault integration

## Deliverable

`backend/.env.example` with all keys documented.

```
backend/.env.example
```

## Acceptance Criteria

- [ ] `backend/.env.example` exists and is committed to version control
- [ ] Every key listed in the Scope section is present with a comment
- [ ] Blank or safe placeholder values only (no real API keys)
- [ ] `backend/.env` is present in `.gitignore`
- [ ] Copying the file to `backend/.env` and filling in `OPENAI_API_KEY` is sufficient to run the app end-to-end (no undocumented variables required)

## Test Notes

Manual review: open `backend/.env.example` and verify all keys are present, commented, and have no real secret values. Confirm `backend/.env` appears in `.gitignore`.

## Dependencies

001-backend-package-layout
