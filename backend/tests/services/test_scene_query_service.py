from __future__ import annotations

from unittest.mock import AsyncMock

import pytest

from app.exceptions import NotFoundError
from app.models.domain import Message
from app.services.scene_query_service import SceneQueryService
from tests.factories import make_scene_metadata


STORY_ID = "story-123"
SCENE_ID = 1


@pytest.mark.asyncio
async def test_get_scene_returns_metadata_and_messages():
    metadata = make_scene_metadata(story_id=STORY_ID, scene_id=SCENE_ID)
    messages = [Message(id=1, role="user", content="Hello")]

    story_repo = AsyncMock()
    scene_repo = AsyncMock()
    scene_repo.get_metadata.return_value = metadata
    scene_repo.get_messages.return_value = messages

    service = SceneQueryService(story_repo, scene_repo)
    result_meta, result_messages = await service.get_scene(STORY_ID, SCENE_ID)

    assert result_meta is metadata
    assert result_messages is messages
    story_repo.get_story.assert_awaited_once_with(STORY_ID)
    scene_repo.get_metadata.assert_awaited_once_with(STORY_ID, SCENE_ID)
    scene_repo.get_messages.assert_awaited_once_with(STORY_ID, SCENE_ID)


@pytest.mark.asyncio
async def test_get_scene_raises_when_story_not_found():
    story_repo = AsyncMock()
    story_repo.get_story.side_effect = NotFoundError(STORY_ID)
    scene_repo = AsyncMock()

    service = SceneQueryService(story_repo, scene_repo)

    with pytest.raises(NotFoundError):
        await service.get_scene(STORY_ID, SCENE_ID)

    scene_repo.get_metadata.assert_not_awaited()


@pytest.mark.asyncio
async def test_get_scene_raises_when_scene_not_found():
    story_repo = AsyncMock()
    scene_repo = AsyncMock()
    scene_repo.get_metadata.side_effect = NotFoundError(SCENE_ID)

    service = SceneQueryService(story_repo, scene_repo)

    with pytest.raises(NotFoundError):
        await service.get_scene(STORY_ID, SCENE_ID)
