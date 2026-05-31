# Task 077: Test ScenePlayService Populates context_data from Scene Summaries

**Feature:** System prompt correction — test coverage
**Status:** TODO

## Description

After task 074 adds `StoryRepository` to `ScenePlayService` and populates `context_data`, tests are needed to verify (a) `SceneContext` is constructed with summaries from all finished scenes that precede the current scene, and (b) `context_data` is empty when no prior finished scenes exist. These tests belong in `test_scene_play_service.py` and require updating any existing test fixtures that construct `ScenePlayService` without a `story_repo` argument.

## Scope

What IS included:
- `backend/tests/services/test_scene_play_service.py`:
  - Update all existing `ScenePlayService(...)` construction calls to include a mock `StoryRepository`
  - Add test: `context_data` is populated from finished prior scenes
  - Add test: `context_data` is empty when no prior finished scenes exist
  - Add test: finished scenes *after* the current scene's index are excluded from `context_data`

What is NOT included (deferred):
- Changes to production code (covered by tasks 074, 075)
- Tests for `SceneLLMClient` (covered by task 076)

## Deliverable

Updated `backend/tests/services/test_scene_play_service.py` with:

```python
# Example fixture / helper for a story with prior finished scenes
def _make_story_meta_with_finished_scenes():
    return StoryMeta(
        id="story-1",
        title="Test Story",
        scenes=[
            SceneRef(id="scene-0", finished=True, summary=["Scene zero happened.", "More context."]),
            SceneRef(id="scene-1", finished=False, summary=None),  # current scene
        ],
    )

@pytest.mark.asyncio
async def test_play_populates_context_data_from_prior_finished_scenes(...):
    """context_data contains summary lines from finished scenes before current scene."""
    ...
    # assert SceneContext constructed with context_data == ["Scene zero happened.", "More context."]

@pytest.mark.asyncio
async def test_play_context_data_empty_when_no_prior_finished_scenes(...):
    """context_data is empty list when no finished scenes precede current scene."""
    ...
    # assert SceneContext constructed with context_data == []

@pytest.mark.asyncio
async def test_play_excludes_summaries_of_later_scenes(...):
    """Finished scenes after current scene index do not appear in context_data."""
    ...
```

```
backend/tests/services/test_scene_play_service.py
```

## Acceptance Criteria

- [ ] All existing tests in `test_scene_play_service.py` still pass after updating `ScenePlayService` construction to include mock `StoryRepository`
- [ ] New test verifies `context_data` equals the flattened summary lines of finished prior scenes
- [ ] New test verifies `context_data == []` when there are no finished scenes before the current scene
- [ ] New test verifies finished scenes whose index is >= current scene's index are excluded
- [ ] Full test suite passes: `pytest backend/ -v`

## Test Notes

```
pytest backend/tests/services/test_scene_play_service.py -v
pytest backend/ -v
```

## Dependencies

074, 075
