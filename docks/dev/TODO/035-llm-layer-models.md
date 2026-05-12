# Task 035: LLM Layer Models

**Feature:** M5 — LLM Adapter
**Status:** TODO

## Description

Define the input/output Pydantic models used by the LLM layer (`PromptBuilder` and `SceneLLMClient`). `SceneContext` is the single input type that carries everything needed to construct a prompt.

## Scope

What IS included:
- `SceneContext` — Pydantic model with:
  - `scene_description: SceneDescription`
  - `characters: list[CharacterCard]`
  - `messages: list[Message]`
- All types imported from `app.models.domain`; no new domain models introduced

What is NOT included (deferred):
- LLM request/response envelope types (not needed — `SceneLLMClient` returns a plain `str`)
- Any I/O or LLM logic

## Deliverable

`backend/app/llm/models.py` — a finished module with `SceneContext`.

```
backend/app/llm/models.py
```

## Acceptance Criteria

- [ ] `SceneContext` is a Pydantic `BaseModel`
- [ ] `SceneContext(scene_description=..., characters=[...], messages=[...])` constructs without error given valid domain objects
- [ ] `from app.llm.models import SceneContext` succeeds in the backend package

## Test Notes

Unit test: construct a `SceneContext` with minimal fixture data and assert field access works. No I/O required.

## Dependencies

030, 031
