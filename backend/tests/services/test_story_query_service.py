from __future__ import annotations

from unittest.mock import AsyncMock

import pytest

from app.exceptions import NotFoundError
from app.models.domain import SceneRef, StoryIndexItem, StoryMeta
from app.services.story_query_service import StoryQueryService


@pytest.mark.asyncio
async def test_list_stories_returns_repository_result():
    expected = [
        StoryIndexItem(id="abc", title="Story A", created_at="2024-01-01T00:00:00Z", type="scene"),
        StoryIndexItem(id="def", title="Story B", created_at="2023-12-01T00:00:00Z", type="scene"),
    ]
    repo = AsyncMock()
    repo.list_stories.return_value = expected

    service = StoryQueryService(repo)
    result = await service.list_stories()

    assert result is expected
    repo.list_stories.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_story_returns_story_meta():
    expected = StoryMeta(
        id="abc",
        title="Story A",
        scenes=[SceneRef(id=1, finished=False)],
        active_scene_id=1,
    )
    repo = AsyncMock()
    repo.get_story.return_value = expected

    service = StoryQueryService(repo)
    result = await service.get_story("abc")

    assert result is expected
    repo.get_story.assert_awaited_once_with("abc")


@pytest.mark.asyncio
async def test_get_story_raises_key_error_when_not_found():
    repo = AsyncMock()
    repo.get_story.side_effect = NotFoundError("nonexistent")

    service = StoryQueryService(repo)

    with pytest.raises(NotFoundError):
        await service.get_story("nonexistent")
