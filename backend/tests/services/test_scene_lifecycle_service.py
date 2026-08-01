from __future__ import annotations

from unittest.mock import AsyncMock

import pytest

from app.exceptions import SceneFinishedError
from app.services.scene_lifecycle_service import SceneLifecycleService
from tests.factories import make_scene_metadata


STORY_ID = "story-123"
SCENE_ID = 1
SUMMARY = ["The hero escaped the dungeon."]


def make_service(
    metadata: SceneMetadata | None = None,
) -> tuple[SceneLifecycleService, AsyncMock]:
    scene_repo = AsyncMock()
    scene_repo.get_metadata.return_value = metadata or make_scene_metadata(story_id=STORY_ID, scene_id=SCENE_ID)
    service = SceneLifecycleService(scene_repo)
    return service, scene_repo


@pytest.mark.asyncio
async def test_finish_scene_returns_updated_metadata():
    service, _ = make_service(metadata=make_scene_metadata(finished=False))

    result = await service.finish_scene(STORY_ID, SCENE_ID, SUMMARY)

    assert result.finished is True
    assert result.scene_summary == SUMMARY


@pytest.mark.asyncio
async def test_finish_scene_calls_save_metadata():
    service, scene_repo = make_service(metadata=make_scene_metadata(finished=False))

    result = await service.finish_scene(STORY_ID, SCENE_ID, SUMMARY)

    scene_repo.save_metadata.assert_awaited_once_with(STORY_ID, SCENE_ID, result)


@pytest.mark.asyncio
async def test_finish_scene_raises_when_already_finished():
    service, scene_repo = make_service(metadata=make_scene_metadata(finished=True))

    with pytest.raises(SceneFinishedError):
        await service.finish_scene(STORY_ID, SCENE_ID, SUMMARY)

    scene_repo.save_metadata.assert_not_awaited()
