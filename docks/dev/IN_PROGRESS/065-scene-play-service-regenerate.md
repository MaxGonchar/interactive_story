# Task 065: Add `regenerate` Method to ScenePlayService

**Feature:** Regenerate last assistant message
**Status:** TODO

## Description

Add an async `regenerate(story_id, scene_id)` method to `ScenePlayService` in `backend/app/services/scene_play_service.py`. The method invokes the LLM against the current history (minus the last assistant message) and replaces the last assistant message in storage with the new reply, returning the updated `Message`. It must never write to storage if the LLM call fails.

## Scope

What IS included:
- `async def regenerate(self, story_id: str, scene_id: int) -> Message` on `ScenePlayService`
- Raises `ValueError("scene_finished")` if scene metadata `finished` is `True`
- Raises `ValueError("no_assistant_message")` if messages list is empty or last message role is not `"assistant"`
- Builds `SceneContext` with messages up to but **not including** the last assistant message
- Uses the second-to-last message as the user content for the LLM call; if no preceding user message exists (entry-point case), passes `metadata.scene_description.entry_point` as the user content
- Calls `self._llm_client.invoke(context, user_content)`
- On success: calls `self._scene_repo.update_message(story_id, scene_id, last_assistant_msg.id, reply)` and returns the updated `Message`
- On LLM failure: propagates the exception without calling `update_message`

What is NOT included (deferred):
- Router endpoint wiring (task 066)
- Tests (task 067)
- Any changes to the `play` method

## Deliverable

Updated `ScenePlayService` class with the new `regenerate` method:

```
backend/app/services/scene_play_service.py
```

## Acceptance Criteria

- [ ] `ScenePlayService` has an `async def regenerate(self, story_id, scene_id)` method
- [ ] Returns the updated `Message` (id, role="assistant", content=new reply) on success
- [ ] Raises `ValueError("scene_finished")` when `metadata.finished` is `True`
- [ ] Raises `ValueError("no_assistant_message")` when messages list is empty or last message is not `role == "assistant"`
- [ ] `scene_repo.update_message` is **not** called if the LLM raises an exception
- [ ] All existing 116+ backend tests still pass

## Test Notes

Covered by task 067. Manual smoke: can be verified by calling the regenerate endpoint (task 066) once wired.

## Dependencies

none (SceneRepository.update_message already exists)
