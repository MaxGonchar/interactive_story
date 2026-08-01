# Backend Code Convention

This document is the authoritative reference for all backend code in this project. It is used by the `implement-be-task` and `review-be` skills.

---

## Layered Architecture

The backend follows a strict 4-layer architecture. Never skip a layer or mix responsibilities.

| Layer | Package | Responsibility |
|---|---|---|
| API | `app/api/routers/` | Request parsing, response shaping, HTTP routing |
| Service | `app/services/` | Business rules and use-case orchestration |
| Repository | `app/repositories/` | YAML file read/write, storage validation |
| LLM | `app/llm/` | Prompt construction, model invocation, output parsing |

---

## Dependency Injection

- All services and repositories are **constructed in `app/api/dependencies.py`** and injected via FastAPI `Depends()`.
- Nothing outside `dependencies.py` may instantiate a service or repository directly.
- Routers declare dependencies with `svc: MyService = Depends(get_my_service)`.

```python
# dependencies.py
def get_scene_play_service(
    scene_repo: SceneRepository = Depends(get_scene_repository),
    character_repo: CharacterRepository = Depends(get_character_repository),
    llm_client: SceneLLMClient = Depends(get_scene_llm_client),
) -> ScenePlayService:
    return ScenePlayService(scene_repo, character_repo, llm_client)
```

---

## Models: Three Separate Layers

Always keep the three model namespaces separate. Never reuse a model across layers.

| File | Purpose | Example |
|---|---|---|
| `app/models/domain.py` | Business objects | `SceneMetadata`, `Message` |
| `app/models/storage.py` | YAML-shaped Pydantic (read/write) | `SceneMetadataYaml`, `MessageYaml` |
| `app/models/api.py` | Request/response shapes | `PlayRequest`, `PlayResponse` |

All model files start with `from __future__ import annotations`.

---

## Response Shape

Every successful response wraps its payload in a `data` key. Never return a bare object.

```python
return {"data": {"id": scene_ref.id, "finished": scene_ref.finished}}
```

---

## Error Handling

- Domain rule violations: raise a subclass of `DomainError` from `app/exceptions.py`.
- Missing records: repositories raise `NotFoundError` — never return `None`.
- LLM/upstream failures: raise `LLMError`.
- Global handlers in `app/main.py` convert all three to JSON responses.
- **Routers and services never raise `HTTPException`.**

```python
# exceptions.py pattern
class SceneFinishedError(DomainError):
    error_code = "scene_finished"
    message = "Scene is already finished"
```

To add a new error: subclass `DomainError`, set `error_code`, `message`, and optionally `http_status` (default `409`).

---

## Services

- All service methods are `async`.
- Services receive their dependencies via constructor injection.
- Services contain business logic only — no file I/O, no HTTP concerns.

```python
class ScenePlayService:
    def __init__(self, scene_repo: SceneRepository, ...) -> None:
        self._scene_repo = scene_repo

    async def play(self, story_id: str, scene_id: int, user_content: str) -> tuple[Message, Message]:
        ...
```

---

## Repositories

- All repository methods are `async`.
- Repositories wrap YAML file access using `app/utils/yaml_storage` and `app/utils/file_paths`.
- Map from storage models (`*Yaml`) to domain models inside the repository — services always receive domain objects.
- All writes use `atomic_write` from `app/utils/atomic_write`.
- Raise `NotFoundError` on missing records (never return `None`).

```python
async def get_metadata(self, story_id: str, scene_id: int) -> SceneMetadata:
    try:
        data = await yaml_storage.read_yaml(file_paths.scene_metadata_file(story_id, scene_id))
    except FileNotFoundError:
        raise NotFoundError(f"Scene '{scene_id}' not found")
    raw = SceneMetadataYaml(**data)
    return SceneMetadata(...)
```

---

## LLM Layer

### Client structure

Each LLM use case has its own client class (e.g. `SceneLLMClient`, `SummarizeLLMClient`).  
The client constructs the model and loads templates in `__init__`, invokes them in an `async invoke(...)` method.

```python
class SummarizeLLMClient:
    def __init__(self) -> None:
        api_key = os.environ["VENICE_API_KEY"]
        model = os.environ.get("SUMMARY_MODEL", _DEFAULT_MODEL)
        self._model = VeniceAIChatModel(model=model, api_key=api_key)
        env = Environment(loader=FileSystemLoader(str(_TEMPLATES_DIR)), keep_trailing_newline=True)
        self._system_template = env.get_template("summary_system.j2")
```

### Templates

- All prompt templates are **Jinja2 `.j2` files** stored in `app/llm/templates/`.
- Load them with `jinja2.Environment(loader=FileSystemLoader(...))` — never use inline `jinja2.Template(...)` strings.
- Use `Path(__file__).parent / "templates"` to locate the templates directory.

```python
_TEMPLATES_DIR = Path(__file__).parent / "templates"
env = Environment(loader=FileSystemLoader(str(_TEMPLATES_DIR)), keep_trailing_newline=True)
```

### Structured output

Use `langchain_core.output_parsers.PydanticOutputParser` when the LLM must return structured data. Pass `format_instructions` into the template via `parser.get_format_instructions()`.

---

## File Header

Every Python module starts with:

```python
from __future__ import annotations
```

---

## Test Structure

Tests live in `backend/tests/` mirroring `backend/app/`:

```
backend/app/services/scene_play_service.py
backend/tests/services/test_scene_play_service.py

backend/app/api/routers/scenes.py
backend/tests/api/test_scenes_router.py
```

### Router tests

Use `fastapi.testclient.TestClient` and override dependencies via `app.dependency_overrides`. Overrides are cleared automatically by the autouse `clear_dependency_overrides` fixture in `tests/conftest.py` — never call `.clear()` manually.

```python
from fastapi.testclient import TestClient
from app.main import app

# --- POST /play ---

def test_play_success():
    svc = _make_play_service(play_return=(user_msg, assistant_msg))
    app.dependency_overrides[get_scene_play_service] = lambda: svc
    client = TestClient(app)
    response = client.post("/api/stories/s1/scenes/1/play", json={"content": "hi"})
    assert response.status_code == 200
    assert response.json() == {"data": {...}}
```

Use private factory functions to build mock services:

```python
def _make_play_service(play_side_effect=None, play_return=None) -> MagicMock:
    svc = MagicMock()
    svc.play = AsyncMock(side_effect=play_side_effect) if play_side_effect else AsyncMock(return_value=play_return)
    return svc
```

### Service tests

Use `@pytest.mark.asyncio` and `AsyncMock` for all repository and LLM client dependencies.  
Use factory functions from `tests/factories.py` to build domain objects and service instances:

```python
def make_scene_metadata(finished: bool = False, ...) -> SceneMetadata:
    return SceneMetadata(id=1, story_id="story-123", ...)

def make_service(...) -> tuple[ScenePlayService, AsyncMock, AsyncMock]:
    scene_repo = AsyncMock()
    scene_repo.get_metadata.return_value = make_scene_metadata()
    ...
    return ScenePlayService(scene_repo, ...), scene_repo, ...
```

### Running tests

```bash
make test-be
```

Always run from the project root via `make test-be`. Never run `pytest` directly.

---

## BE Tests

This section is the authoritative reference for backend test conventions. See also: `docks/dev/features/be_tests_conventions.md` for the full rationale.

---

### Support Files

```
tests/
  conftest.py          # pytest fixtures shared by all unit tests
  factories.py         # pure make_*() functions building domain objects — no pytest dependency
  utils.py             # shared helpers (custom assertions, data loaders, etc.)
  api/
  services/
  repositories/
  llm/
  models/
  utils/
  functional/
    conftest.py        # functional-test-only fixtures (temp data dir, LLM mock, TestClient)
    test_scene_play_flow.py
    test_scene_finish_flow.py
```

| File | Role |
|---|---|
| `tests/conftest.py` | Autouse fixtures shared by all unit tests. At minimum the `clear_dependency_overrides` fixture. |
| `tests/factories.py` | Pure `make_*()` functions that build domain objects. No pytest dependency — importable anywhere. |
| `tests/utils.py` | Shared helpers that are neither factories nor fixtures (e.g. assert standard error shape, load YAML fixtures). |
| `tests/functional/conftest.py` | Functional-test environment: temp data dir, repos wired to it, LLM client mocked, `TestClient` ready. |

#### `tests/conftest.py` — minimum content

```python
import pytest
from app.main import app

@pytest.fixture(autouse=True)
def clear_dependency_overrides():
    yield
    app.dependency_overrides.clear()
```

#### `tests/factories.py` — pattern

```python
def make_scene_metadata(finished: bool = False, context: list[str] | None = None) -> SceneMetadata:
    ...

def make_message(id: int = 1, role: str = "user", content: str = "Hello") -> Message:
    ...
```

---

### Conventions

#### Functions over classes

Use standalone `def test_*` functions. Do **not** group tests in classes. Use a comment separator to group related tests instead:

```python
# --- POST /play ---

def test_play_success(): ...
def test_play_scene_finished_returns_409(): ...

# --- GET /scenes ---

def test_list_scenes_success(): ...
```

#### One file per resource / service

- API tests: one file per REST resource (e.g. `test_scenes.py` covers all `/scenes` endpoints).
- Service tests: one file per service class.

#### AAA pattern

All tests follow Arrange → Act → Assert. Separate each phase with a blank line:

```python
def test_play_success():
    svc = _make_play_service(play_return=(user_msg, assistant_msg))
    app.dependency_overrides[get_scene_play_service] = lambda: svc

    response = TestClient(app).post("/api/.../play", json={"content": "hi"})

    assert response.status_code == 200
    assert response.json() == {"data": {...}}
```

#### Structured assertions

Compare the full expected structure rather than asserting individual fields. This makes failures self-describing and merges multiple narrow tests into one:

```python
# Avoid
assert resp.status_code == 200
body = resp.json()
assert "data" in body
assert len(body["data"]) == 3

# Prefer
expected = {"data": [{"id": "mila"}, {"id": "bun"}, {"id": "max"}]}
assert resp.status_code == 200
assert resp.json() == expected
```

#### Parametrized tests

Use `@pytest.mark.parametrize` when multiple inputs produce structurally similar outcomes (e.g. multiple error cases that all return 4xx). Avoid near-identical separate test functions:

```python
@pytest.mark.parametrize("exc,expected_status", [
    (NotFoundError(), 404),
    (SceneFinishedError(), 409),
])
def test_play_errors(exc, expected_status):
    svc = _make_play_service(play_side_effect=exc)
    app.dependency_overrides[get_scene_play_service] = lambda: svc
    response = TestClient(app).post("/api/.../play", json={"content": "hi"})
    assert response.status_code == expected_status
```

---

### Functional Tests

**Intent:** verify usage flows through HTTP endpoints. All assertions go through subsequent endpoint calls — never assert against storage directly.

**LLM handling:** mock LLM clients at the client level (in `functional/conftest.py`) to return deterministic strings. Functional tests do not test LLM behavior.

**Example flow — scene play:**

```
POST /api/stories/{id}/scenes/{id}/play  → assert 200, response has user_message + assistant_message
GET  /api/stories/{id}/scenes/{id}       → assert messages appear in scene data
```

**Flows to cover (first iteration):**
- Scene play: send a message, verify response and scene state.
- Scene finish: finish a scene, verify it can no longer be played.
