# Task 052: Add Startup Validation for VENICE_API_KEY

**Feature:** Absent env configs for LLM adapter
**Status:** TODO

## Description

`SceneLLMClient.__init__` uses `os.environ["VENICE_API_KEY"]` (hard dict access), so a missing key raises a raw `KeyError` at the first `POST /play` request — not at startup. This makes the failure late and opaque. A startup check in `main.py` converts this into an explicit, early `RuntimeError` with a clear message, caught the moment the server boots.

## Scope

What IS included:
- Add a guard in `backend/app/main.py` — after `load_dotenv()` — that raises `RuntimeError` if `VENICE_API_KEY` is not set in the environment
- The check must be conditional: skip it when `TESTING` env var is set to `"1"` (or equivalent), so existing test suites that boot the app without a real key continue to work

What is NOT included (deferred):
- Changing `.env.example` (task 051)
- Adding tests for the missing-key scenario in `SceneLLMClient` (task 053)
- Converting `os.environ["VENICE_API_KEY"]` to `os.getenv(...)` in `scene_llm_client.py` — the startup check makes the error occur at boot instead; the `KeyError` path becomes unreachable in normal operation

## Deliverable

Modified `backend/app/main.py` with a startup validation block:

```python
# backend/app/main.py  (after load_dotenv())
if not os.environ.get("TESTING") and not os.getenv("VENICE_API_KEY"):
    raise RuntimeError(
        "VENICE_API_KEY environment variable is required but not set. "
        "Copy backend/.env.example to backend/.env and supply a valid key."
    )
```

```
backend/app/main.py
```

## Acceptance Criteria

- [ ] Starting the backend without `VENICE_API_KEY` set raises `RuntimeError` with a message that names the missing variable and refers to `.env.example`
- [ ] Starting the backend with `VENICE_API_KEY` set (any non-empty string) succeeds without error
- [ ] Running the full test suite (`pytest`) with `TESTING=1` (or with the key set via the existing `autouse` fixture) passes without the new guard raising
- [ ] `load_dotenv()` is called before the guard, so a `.env` file with the key is honoured correctly

## Test Notes

Manual verification:
1. Unset `VENICE_API_KEY` in the shell and run `uvicorn app.main:app` — confirm startup fails with the `RuntimeError` message.
2. Set `VENICE_API_KEY=dummy` and re-run — confirm the server starts.
3. Run `pytest` — all existing tests continue to pass (the `autouse` fixture in `test_scene_llm_client.py` sets the key; other test modules do not import `main.py` at module level).

## Dependencies

051-update-env-example-llm-vars.md
