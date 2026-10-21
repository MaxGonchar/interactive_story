from __future__ import annotations

from unittest.mock import AsyncMock

import pytest

from app.exceptions import (
    NotFoundError,
    NotLastItemError,
    OpeningItemNotDeletableError,
    SceneFinishedError,
)
from app.models.domain import CharacterDrivenLLMData, CharacterDrivenMessage
from app.services.character_driven_scene_item_service import (
    CharacterDrivenSceneItemService,
)
from tests.factories import make_scene_metadata

STORY_ID = "story-abc"
SCENE_ID = 1


def _make_message(item_id: int) -> CharacterDrivenMessage:
    return CharacterDrivenMessage(
        id=item_id,
        input=None,
        narration=f"Item {item_id}.",
        llm_data=CharacterDrivenLLMData(
            character_model_id="character-model",
            narrator_model_id="narrator-model",
        ),
    )


def _make_service(
    messages: list[CharacterDrivenMessage] | None = None,
    finished: bool = False,
):
    story_repo = AsyncMock()
    scene_repo = AsyncMock()
    scene_repo.get_metadata.return_value = make_scene_metadata(
        finished=finished, story_id=STORY_ID, scene_id=SCENE_ID
    )
    item_repo = AsyncMock()
    item_repo.get_messages.return_value = (
        messages if messages is not None else [_make_message(1), _make_message(2)]
    )
    service = CharacterDrivenSceneItemService(story_repo, scene_repo, item_repo)
    return service, story_repo, scene_repo, item_repo


@pytest.mark.asyncio
async def test_edit_item_returns_updated_item_and_scene_metadata():
    updated = _make_message(1).model_copy(update={"narration": "Edited opening."})
    service, story_repo, scene_repo, item_repo = _make_service()
    item_repo.update_narration.return_value = updated

    metadata, result = await service.edit_item(
        STORY_ID, SCENE_ID, 1, "Edited opening."
    )

    assert (metadata, result) == (scene_repo.get_metadata.return_value, updated)
    story_repo.get_story.assert_awaited_once_with(STORY_ID)
    scene_repo.get_metadata.assert_awaited_once_with(STORY_ID, SCENE_ID)
    item_repo.update_narration.assert_awaited_once_with(
        STORY_ID, SCENE_ID, 1, "Edited opening."
    )


@pytest.mark.asyncio
async def test_edit_item_checks_story_before_scene_and_item():
    service, story_repo, scene_repo, item_repo = _make_service()
    story_repo.get_story.side_effect = NotFoundError("Story not found")

    with pytest.raises(NotFoundError, match="Story not found"):
        await service.edit_item(STORY_ID, SCENE_ID, 2, "Edited.")

    scene_repo.get_metadata.assert_not_awaited()
    item_repo.update_narration.assert_not_awaited()


@pytest.mark.asyncio
async def test_edit_item_checks_scene_before_item():
    service, _, scene_repo, item_repo = _make_service()
    scene_repo.get_metadata.side_effect = NotFoundError("Scene not found")

    with pytest.raises(NotFoundError, match="Scene not found"):
        await service.edit_item(STORY_ID, SCENE_ID, 2, "Edited.")

    item_repo.update_narration.assert_not_awaited()


@pytest.mark.asyncio
async def test_edit_item_rejects_finished_scene_before_item_lookup():
    service, _, _, item_repo = _make_service(finished=True)

    with pytest.raises(SceneFinishedError):
        await service.edit_item(STORY_ID, SCENE_ID, 999, "Edited.")

    item_repo.update_narration.assert_not_awaited()


@pytest.mark.asyncio
async def test_edit_item_propagates_missing_item_after_scene_checks():
    service, _, _, item_repo = _make_service()
    item_repo.update_narration.side_effect = NotFoundError("Item '9' not found")

    with pytest.raises(NotFoundError, match="Item '9' not found"):
        await service.edit_item(STORY_ID, SCENE_ID, 9, "Edited.")


@pytest.mark.asyncio
async def test_delete_item_rejects_finished_scene_before_item_lookup():
    service, _, _, item_repo = _make_service(finished=True)

    with pytest.raises(SceneFinishedError):
        await service.delete_item(STORY_ID, SCENE_ID, 999)

    item_repo.get_messages.assert_not_awaited()
    item_repo.delete_last_message.assert_not_awaited()


@pytest.mark.asyncio
async def test_delete_item_returns_not_found_for_missing_item():
    service, _, _, item_repo = _make_service()

    with pytest.raises(NotFoundError, match="Item '9' not found"):
        await service.delete_item(STORY_ID, SCENE_ID, 9)

    item_repo.delete_last_message.assert_not_awaited()


@pytest.mark.asyncio
async def test_delete_item_rejects_non_last_item():
    service, _, _, item_repo = _make_service()

    with pytest.raises(NotLastItemError):
        await service.delete_item(STORY_ID, SCENE_ID, 1)

    item_repo.delete_last_message.assert_not_awaited()


@pytest.mark.asyncio
async def test_delete_item_rejects_opening_item_when_it_is_last():
    service, _, _, item_repo = _make_service(messages=[_make_message(1)])

    with pytest.raises(OpeningItemNotDeletableError):
        await service.delete_item(STORY_ID, SCENE_ID, 1)

    item_repo.delete_last_message.assert_not_awaited()


@pytest.mark.asyncio
async def test_delete_item_deletes_last_item():
    service, _, _, item_repo = _make_service()

    result = await service.delete_item(STORY_ID, SCENE_ID, 2)

    assert result is None
    item_repo.delete_last_message.assert_awaited_once_with(STORY_ID, SCENE_ID)
