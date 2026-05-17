from unittest.mock import AsyncMock

import pytest

from app.models.domain import SceneDescription, SceneMetadata
from app.services.scene_lifecycle_service import SceneLifecycleService


STORY_ID = "story-123"
SCENE_ID = 1
SUMMARY = "The hero escaped the dungeon."


def make_scene_metadata(finished: bool = False) -> SceneMetadata:
    return SceneMetadata(
        id=SCENE_ID,
        story_id=STORY_ID,
        characters_ids=["c1"],
        finished=finished,
        scene_description=SceneDescription(
            entry_point="Start here.",
            general_scene_guide="Guide text.",
            writing_style="Descriptive.",
        ),
        scene_summary=None,
    )


def make_service(
    metadata: SceneMetadata | None = None,
) -> tuple[SceneLifecycleService, AsyncMock]:
    scene_repo = AsyncMock()
    scene_repo.get_metadata.return_value = metadata or make_scene_metadata()
    service = SceneLifecycleService(scene_repo)
    return service, scene_repo


@pytest.mark.asyncio
async def test_finish_scene_returns_updated_metadata():
    service, _ = make_service(metadata=make_scene_metadata(finished=False))

    result = await service.finish_scene(STORY_ID, SCENE_ID, SUMMARY)

    assert result.finished is True
    assert result.scene_summary == [SUMMARY]


@pytest.mark.asyncio
async def test_finish_scene_calls_save_metadata():
    service, scene_repo = make_service(metadata=make_scene_metadata(finished=False))

    result = await service.finish_scene(STORY_ID, SCENE_ID, SUMMARY)

    scene_repo.save_metadata.assert_awaited_once_with(STORY_ID, SCENE_ID, result)


@pytest.mark.asyncio
async def test_finish_scene_raises_when_already_finished():
    service, scene_repo = make_service(metadata=make_scene_metadata(finished=True))

    with pytest.raises(ValueError, match="scene_finished"):
        await service.finish_scene(STORY_ID, SCENE_ID, SUMMARY)

    scene_repo.save_metadata.assert_not_awaited()
