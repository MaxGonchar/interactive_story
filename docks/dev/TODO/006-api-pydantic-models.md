# Task 006: API Pydantic Models

**Feature:** M2 — API Contract Stubs
**Status:** TODO

## Description

Define all Pydantic request and response models for the 7 MVP endpoints, plus the standard `ErrorResponse` model. These models are the single source of truth for API shapes and drive FastAPI's automatic validation and OpenAPI schema generation.

## Scope

What IS included:
- `app/models/api.py` with every request and response model for the 7 MVP endpoints
- `ErrorResponse` and nested `ErrorDetail` models
- Field-level validation constraints (e.g. `max_length`, `min_length`) matching `endpoints.md`
- All models exported from `app/models/__init__.py`

What is NOT included (deferred):
- Domain / storage models (`domain.py`, `storage.py`) — M4
- Any database or YAML I/O — M4
- Business logic — M6

## Deliverable

`app/models/api.py` containing:

```
app/models/api.py
app/models/__init__.py   (re-export new models)
```

Models to define:

| Class | Used by |
|---|---|
| `ErrorDetail` | all error responses |
| `ErrorResponse` | all 4xx/5xx responses |
| `StoryListItem` | GET /stories |
| `StoryListResponse` | GET /stories |
| `SceneListItem` | GET /stories/{story_id} |
| `StoryDetailResponse` | GET /stories/{story_id} |
| `SceneDescriptionModel` | GET scene |
| `MessageModel` | GET scene, POST play |
| `SceneDetailResponse` | GET scene |
| `PlayRequest` | POST play |
| `PlayResponse` | POST play |
| `UpdateMessageRequest` | PUT message |
| `UpdateMessageResponse` | PUT message |
| `DeleteMessageResponse` | DELETE message |
| `FinishSceneRequest` | POST finish |
| `FinishSceneResponse` | POST finish |

## Acceptance Criteria

- [ ] `app/models/api.py` exists and imports without errors
- [ ] `ErrorResponse` has shape `{"error": {"code": str, "message": str}}`
- [ ] `PlayRequest.content` has `min_length=1, max_length=4000`
- [ ] `UpdateMessageRequest.content` has `min_length=1, max_length=4000`
- [ ] `FinishSceneRequest.scene_summary` has `min_length=1, max_length=2000`
- [ ] All field names and types match the JSON shapes in `endpoints.md` exactly
- [ ] `python -c "from app.models.api import *"` exits 0

## Test Notes

Run from the `backend/` directory:

```bash
python -c "from app.models.api import ErrorResponse, PlayRequest, FinishSceneRequest; print('OK')"
```

Also verify validation rejects bad input:

```python
from app.models.api import PlayRequest
PlayRequest(content="")          # should raise ValidationError
PlayRequest(content="x" * 4001)  # should raise ValidationError
PlayRequest(content="hello")     # should succeed
```

## Dependencies

005-env-example (M1 complete — app package exists and is importable)
