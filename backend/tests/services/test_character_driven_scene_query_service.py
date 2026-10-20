from __future__ import annotations

from unittest.mock import AsyncMock

import pytest

from app.exceptions import NotFoundError
from app.models.domain import CharacterDrivenMessage
from app.services.character_driven_scene_query_service import (
    CharacterDrivenSceneQueryService,
)
from tests.factories import make_scene_metadata


STORY_ID = "story-123"
SCENE_ID = 1


# --- get_scene ---


@pytest.mark.asyncio
async def test_get_scene_returns_metadata_and_messages():
    metadata = make_scene_metadata(story_id=STORY_ID, scene_id=SCENE_ID)
    messages = [
        CharacterDrivenMessage(
            id=1,
            input=None,
            narration="The harbor bell rings.",
            llm_data={"character_model_id": "character", "narrator_model_id": "narrator"},
        )
    ]
    story_repo = AsyncMock()
    scene_repo = AsyncMock()
    scene_repo.get_metadata.return_value = metadata
    character_driven_scene_repo = AsyncMock()
    character_driven_scene_repo.get_messages.return_value = messages

    service = CharacterDrivenSceneQueryService(
        story_repo, scene_repo, character_driven_scene_repo
    )
    result_metadata, result_messages = await service.get_scene(STORY_ID, SCENE_ID)

    assert result_metadata is metadata
    assert result_messages is messages
    story_repo.get_story.assert_awaited_once_with(STORY_ID)
    scene_repo.get_metadata.assert_awaited_once_with(STORY_ID, SCENE_ID)
    character_driven_scene_repo.get_messages.assert_awaited_once_with(
        STORY_ID, SCENE_ID
    )


@pytest.mark.asyncio
async def test_get_scene_raises_when_story_not_found():
    story_repo = AsyncMock()
    story_repo.get_story.side_effect = NotFoundError("Story not found")
    scene_repo = AsyncMock()
    character_driven_scene_repo = AsyncMock()
    service = CharacterDrivenSceneQueryService(
        story_repo, scene_repo, character_driven_scene_repo
    )

    with pytest.raises(NotFoundError):
        await service.get_scene(STORY_ID, SCENE_ID)

    scene_repo.get_metadata.assert_not_awaited()
    character_driven_scene_repo.get_messages.assert_not_awaited()


@pytest.mark.asyncio
async def test_get_scene_raises_when_scene_not_found():
    story_repo = AsyncMock()
    scene_repo = AsyncMock()
    scene_repo.get_metadata.side_effect = NotFoundError("Scene not found")
    character_driven_scene_repo = AsyncMock()
    service = CharacterDrivenSceneQueryService(
        story_repo, scene_repo, character_driven_scene_repo
    )

    with pytest.raises(NotFoundError):
        await service.get_scene(STORY_ID, SCENE_ID)