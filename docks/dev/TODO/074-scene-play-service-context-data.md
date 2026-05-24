# Task 074: Populate context_data with Finished-Scene Summaries in ScenePlayService

**Feature:** System prompt correction — scene summaries in context
**Status:** TODO

## Description

`ScenePlayService.play()` constructs `SceneContext` without populating `context_data`, so `# Context Data` in the system prompt always renders as `(no context)`. This task adds `StoryRepository` as a constructor dependency and uses it to fetch summaries of all previously-finished scenes, populating `context_data` before the LLM call.

Scene ordering is determined by position in `story_meta.scenes` list (not by ID comparison) to handle non-sequential IDs correctly.

## Scope

What IS included:
- `backend/app/services/scene_play_service.py`:
  - Add `story_repo: StoryRepository` parameter to `__init__`
  - In `play()`, call `self._story_repo.get_story(story_id)` to fetch `StoryMeta`
  - Collect summaries of all finished scenes whose index in `story_meta.scenes` is less than the index of the current scene
  - Pass collected summary lines as `context_data` to `SceneContext`

What is NOT included (deferred):
- Changes to `dependencies.py` DI wiring (covered by task 075)
- Changes to `SceneLLMClient` (covered by task 073)
- Test additions (covered by task 077)

## Deliverable

Updated `backend/app/services/scene_play_service.py`:

```python
# __init__ signature change:
def __init__(
    self,
    scene_repo: SceneRepository,
    character_repo: CharacterRepository,
    llm_client: SceneLLMClient,
    story_repo: StoryRepository,
) -> None:
    ...
    self._story_repo = story_repo

# inside play():
story_meta = await self._story_repo.get_story(story_id)
current_index = next(
    (i for i, s in enumerate(story_meta.scenes) if s.id == scene_id), None
)
context_data = [
    line
    for i, s in enumerate(story_meta.scenes)
    if s.finished and (current_index is None or i < current_index) and s.summary
    for line in s.summary
]
context = SceneContext(
    scene_description=metadata.scene_description,
    characters=characters,
    messages=messages,
    context_data=context_data,
)
```

```
backend/app/services/scene_play_service.py
```

## Acceptance Criteria

- [ ] `ScenePlayService.__init__` accepts `story_repo: StoryRepository` as a parameter and stores it
- [ ] `play()` calls `self._story_repo.get_story(story_id)` before constructing `SceneContext`
- [ ] `context_data` contains summary lines only from finished scenes that appear before the current scene in the `story_meta.scenes` list
- [ ] `context_data` is empty (not `None`) when no prior finished scenes exist
- [ ] Scenes after the current scene's index are excluded even if finished
- [ ] Scenes with `summary=None` or `summary=[]` are skipped without error
- [ ] Existing tests still pass (`pytest backend/tests/services/test_scene_play_service.py -v`)

## Test Notes

Run existing unit tests after changes. Because existing tests construct `ScenePlayService` directly without `story_repo`, they will break — update test construction to supply a mock `StoryRepository` as part of this task or accept that task 077 will fix them. Preferred: update test fixtures in this task to keep CI green.

```
pytest backend/tests/services/test_scene_play_service.py -v
```

## Dependencies

none
