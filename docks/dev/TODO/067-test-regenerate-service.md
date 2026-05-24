# Task 067: Unit Tests for ScenePlayService.regenerate

**Feature:** Regenerate last assistant message
**Status:** TODO

## Description

Add unit tests for `ScenePlayService.regenerate` to `backend/tests/services/test_scene_play_service.py`. Tests use the existing `make_service` / `make_scene_metadata` helpers already in that file and cover the success path, both `ValueError` branches, and the LLM-failure atomicity guarantee.

## Scope

What IS included:
- `test_regenerate_replaces_last_assistant_message` — happy path: LLM returns new reply, `update_message` is called with the last assistant message ID and the new content, returned `Message` has correct fields
- `test_regenerate_raises_when_scene_finished` — `metadata.finished=True` raises `ValueError("scene_finished")`; `update_message` not called
- `test_regenerate_raises_when_no_messages` — empty message list raises `ValueError("no_assistant_message")`; `update_message` not called
- `test_regenerate_raises_when_last_message_is_user` — last message has `role="user"`, raises `ValueError("no_assistant_message")`; `update_message` not called
- `test_regenerate_does_not_persist_on_llm_failure` — LLM raises `RuntimeError`; exception propagates; `update_message` not called

What is NOT included (deferred):
- Router-level integration tests
- Tests for entry-point edge case (no preceding user message) — covered by the service implementation implicitly; can be added as a follow-up

## Deliverable

Additional `@pytest.mark.asyncio` test functions in the existing test file:

```
backend/tests/services/test_scene_play_service.py
```

## Acceptance Criteria

- [ ] All 5 new tests exist and are collected by pytest
- [ ] All 5 new tests pass
- [ ] No existing tests are modified or broken
- [ ] `scene_repo.update_message` is asserted **not called** in all error/LLM-failure tests
- [ ] `scene_repo.update_message` is asserted **called once** with correct args in the happy-path test

## Test Notes

Run: `pytest backend/tests/services/test_scene_play_service.py -v`

All 5 new tests plus the 3 existing `play` tests should pass.

## Dependencies

- 065 (ScenePlayService.regenerate implementation)
