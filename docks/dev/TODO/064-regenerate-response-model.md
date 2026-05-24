# Task 064: Add RegenerateResponse Pydantic Model

**Feature:** Regenerate last assistant message
**Status:** TODO

## Description

Add a `RegenerateResponse` Pydantic model to `backend/app/models/api.py` so the regenerate router endpoint has a typed response model. The model wraps a single `MessageModel` inside a `data` field whose key is `assistant_message`, matching the shape `{"data": {"assistant_message": {id, role, content}}}`.

## Scope

What IS included:
- New `RegenerateData` model with a single `assistant_message: MessageModel` field
- New `RegenerateResponse` model with a single `data: RegenerateData` field
- Both added to `backend/app/models/api.py` in a new `# Regenerate` section

What is NOT included (deferred):
- Router endpoint that uses this model (task 066)
- Any service or repository changes

## Deliverable

Two new Pydantic classes in `backend/app/models/api.py`:

```
backend/app/models/api.py
```

```python
class RegenerateData(BaseModel):
    assistant_message: MessageModel

class RegenerateResponse(BaseModel):
    data: RegenerateData
```

## Acceptance Criteria

- [ ] `RegenerateData` and `RegenerateResponse` exist in `app/models/api.py`
- [ ] `RegenerateResponse(data={"assistant_message": {"id": 1, "role": "assistant", "content": "x"}})` validates without error
- [ ] `MessageModel` is reused (no duplication of message field definitions)
- [ ] All existing backend tests still pass (`pytest backend/tests/`)

## Test Notes

Manual: import and instantiate in a Python REPL or a quick `pytest` invocation — no dedicated test file required for a pure model addition. Existing model tests in `backend/tests/` cover the pattern.

## Dependencies

none
