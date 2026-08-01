# Feature: BE Tests Standardization and Conventions

**Status**: Draft  
**Date**: 2026-08-01

## Summary

Define a consistent set of conventions for writing backend tests, establish a clean support file structure, and introduce functional (end-to-end via HTTP) flow tests for the core usage flows. The goal is to make tests easier to read, maintain, and extend — and to give AI tooling a clear harness to follow when generating or modifying tests.

## Value

- Inconsistent assertion styles and duplicated setup code make tests harder to read and maintain.
- Missing functional tests leave usage flows (play, finish) uncovered as integrated behaviors.
- `app.dependency_overrides.clear()` called manually is a silent leak risk when tests fail.
- Success criteria: new tests written by hand or AI follow a single consistent shape; flows are covered; no override leaks.

## Scope

**In scope for first iteration**
- Define and document all conventions below.
- Update AI instructions (`copilot-instructions.md` or a skill) to enforce this shape.
- Refactor existing tests across all test folders to match conventions.
- Add `tests/factories.py`, `tests/utils.py`, `tests/conftest.py`.
- Add `tests/functional/` folder with `conftest.py` and first flow tests for scene play and finish.

**Out of scope / future**
- Refactoring service/repository/LLM unit tests (lower priority, already reasonable).
- Coverage reporting or CI enforcement.
- Tests for story/scene creation via UI (not yet an API flow).

## Conventions

### AAA Pattern
All tests follow Arrange → Act → Assert. Each section is visually separated by a blank line.

### Test Functions over Classes
Use standalone `def test_*` functions. Do **not** use classes unless multiple tests in the same file share non-trivial `setup_method` / `teardown_method` state (rare). Group related tests with a comment separator instead:

```python
# --- POST /play ---

def test_play_success(): ...
def test_play_scene_finished_returns_409(): ...
```

### One File per Resource / Service
- API tests: one file per REST resource (e.g., `test_scenes.py` covers all `/scenes` endpoints).
- Service tests: one file per service class.

### Assertion Style: Structured Comparison
Prefer comparing full expected structures over asserting individual fields. This makes failures self-describing and eliminates the need for multiple narrow tests covering the same call.

**Avoid:**
```python
assert resp.status_code == 200
body = resp.json()
assert "data" in body
assert len(body["data"]) == 3
ids = {item["id"] for item in body["data"]}
assert ids == {"mila", "bun", "max"}
```

**Prefer:**
```python
expected = {
    "data": [
        {"id": "mila", "name": "Mila"},
        {"id": "bun", "name": "Bun"},
        {"id": "max", "name": "Max"},
    ]
}
assert resp.status_code == 200
assert resp.json() == expected
```

This also allows merging `test_returns_200`, `test_returns_3_items`, `test_items_have_id_and_name` into a single `test_success`.

### Parametrized Tests
Use `@pytest.mark.parametrize` when multiple inputs are expected to produce structurally similar outcomes (e.g., multiple error cases that all return 4xx). Avoid separate near-identical test functions for each case.

## Support File Structure

```
tests/
  conftest.py          # pytest fixtures shared by all unit tests
  factories.py         # pure make_*() functions building domain objects — no pytest dependency
  utils.py             # shared test helpers (custom assertions, data loaders, etc.)
  api/                 # unit tests for routers
  services/            # unit tests for services
  repositories/        # unit tests for repositories
  llm/                 # unit tests for LLM clients
  models/              # unit tests for models
  utils/               # unit tests for utils
  functional/
    conftest.py        # functional-test-only fixtures (temp data dir, LLM mock, TestClient)
    test_scene_play_flow.py
    test_scene_finish_flow.py
    ...
```

### `tests/conftest.py`
Contains pytest fixtures shared by unit tests. At minimum:

```python
import pytest
from app.main import app

@pytest.fixture(autouse=True)
def clear_dependency_overrides():
    yield
    app.dependency_overrides.clear()
```

This prevents override leaks when a test raises before reaching a manual `.clear()` call.

### `tests/factories.py`
Pure Python factory functions for domain objects. Importable anywhere without pytest.

```python
def make_scene_metadata(finished: bool = False, context: list[str] | None = None) -> SceneMetadata:
    ...

def make_message(id: int = 1, role: str = "user", content: str = "Hello") -> Message:
    ...
```

### `tests/utils.py`
Shared helpers that are neither factories nor fixtures — e.g., functions that assert a standard error shape, load fixture YAML files, etc.

### `tests/functional/conftest.py`
Provides the wired-up test environment for functional tests:
- A `tmp_path`-based data directory populated with seed YAML fixtures.
- `app.dependency_overrides` wiring repos to point at the temp dir.
- LLM client mocked to return deterministic responses.
- A `TestClient` fixture ready to use.

## Functional Tests

### Intent
Functional tests verify **usage flows through HTTP endpoints**. They do not assert against storage directly — all assertions go through subsequent endpoint calls.

### LLM Handling
LLM calls are mocked at the client level to return deterministic strings. Functional tests do not test LLM behavior — that belongs in unit tests.

### Example Flow: Scene Play
```
POST /api/stories/{id}/scenes/{id}/play  → assert 200, response has user_message + assistant_message
GET  /api/stories/{id}/scenes/{id}       → assert messages appear in scene data
```

### Flows to Cover (first iteration)
- Scene play: send a message, verify response and scene state.
- Scene finish: finish a scene, verify it can no longer be played.

## Open Questions

- Should `factories.py` be split by domain (`scene_factories.py`, `story_factories.py`) as the codebase grows? Defer until the single file exceeds ~150 lines.
- Which seed YAML fixture should functional tests use — a copy of `data-test/` or a freshly generated minimal fixture in `conftest.py`?

## Risks

- Refactoring existing API tests to flatten classes and merge split tests may surface hidden assumptions — run the full suite after each file is updated.
- Functional tests with real YAML storage are sensitive to seed data shape; keep the seed minimal and explicit.
