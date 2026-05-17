# Task 042: ScenePlayService

**Feature:** M6 — Services and Full Integration
**Status:** TODO

## Description

Implement `ScenePlayService` in `app/services/scene_play_service.py`. This is the core gameplay service: it validates the scene is active, assembles the LLM context from characters and message history, calls `SceneLLMClient`, and persists both the user message and the assistant reply atomically (neither is written if the LLM call fails).

## Scope

What IS included:
- `ScenePlayService` class with one async method:
  - `play(story_id: str, scene_id: int, user_content: str) -> tuple[Message, Message]`
- Guard: raises `ValueError("scene_finished")` if `SceneMetadata.finished` is `True`
- Context assembly: loads scene metadata, characters (via `CharacterRepository`), and existing messages
- LLM call via `SceneLLMClient.invoke(context, user_content)`
- Atomic persist: both messages are appended in sequence; if LLM raises, nothing is written
- New message IDs: `max(existing_ids, default=0) + 1` for user message; `user_id + 1` for assistant
- Returns `(user_message, assistant_message)` as `Message` domain objects

What is NOT included (deferred):
- Scene or story existence validation (raises `KeyError` propagated from repositories)
- Router error mapping (task 047)
- LLM implementation (task 039, already done)

## Deliverable

A finished service class at `backend/app/services/scene_play_service.py`.

```
backend/app/services/scene_play_service.py
```

## Acceptance Criteria

- [ ] Returns `(user_message, assistant_message)` tuple on success
- [ ] Raises `ValueError("scene_finished")` when scene is already finished
- [ ] LLM failure (any exception) propagates without persisting any messages
- [ ] On success, both messages are written to storage via `SceneRepository.add_message()`
- [ ] `SceneContext` is assembled with correct scene description, characters, and prior messages
- [ ] Unit tests pass: `test_scene_play_service.py` covers success, finished-scene guard, and LLM failure

## Test Notes

Create `backend/tests/services/test_scene_play_service.py`.

Tests to write:
- `test_play_returns_both_messages` — mock repos and LLM client; assert two `Message` objects returned with correct roles and content
- `test_play_raises_when_scene_finished` — mock metadata with `finished=True`; assert `ValueError("scene_finished")`
- `test_play_does_not_persist_on_llm_failure` — mock LLM to raise; assert `add_message` was never called
- `test_play_assigns_correct_message_ids` — mock existing messages with known ids; assert new ids are `max+1` and `max+2`

## Dependencies

033 (SceneRepository), 034 (CharacterRepository), 039 (SceneLLMClient)
