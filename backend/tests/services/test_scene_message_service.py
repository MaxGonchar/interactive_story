from unittest.mock import AsyncMock

import pytest

from app.models.domain import Message, SceneDescription, SceneMetadata
from app.services.scene_message_service import SceneMessageService


STORY_ID = "story-123"
SCENE_ID = 1
MESSAGE_ID = 42


def make_scene_metadata(finished: bool = False) -> SceneMetadata:
    return SceneMetadata(
        id=SCENE_ID,
        story_id=STORY_ID,
        characters_ids=["c1"],
        finished=finished,
        scene_description=SceneDescription(
            general_scene_guide="Guide text.",
            writing_style="Descriptive.",
        ),
        scene_summary=None,
    )


def make_service(
    finished: bool = False,
    update_return: Message | None = None,
    update_side_effect: Exception | None = None,
    delete_side_effect: Exception | None = None,
) -> tuple[SceneMessageService, AsyncMock]:
    scene_repo = AsyncMock()
    scene_repo.get_metadata.return_value = make_scene_metadata(finished=finished)

    if update_side_effect is not None:
        scene_repo.update_message.side_effect = update_side_effect
    elif update_return is not None:
        scene_repo.update_message.return_value = update_return

    if delete_side_effect is not None:
        scene_repo.delete_message.side_effect = delete_side_effect

    service = SceneMessageService(scene_repo)
    return service, scene_repo


@pytest.mark.asyncio
async def test_edit_message_returns_updated_message():
    expected = Message(id=MESSAGE_ID, role="user", content="updated text")
    service, scene_repo = make_service(update_return=expected)

    result = await service.edit_message(STORY_ID, SCENE_ID, MESSAGE_ID, "updated text")

    assert result == expected
    scene_repo.update_message.assert_awaited_once_with(
        STORY_ID, SCENE_ID, MESSAGE_ID, "updated text"
    )


@pytest.mark.asyncio
async def test_edit_message_raises_when_scene_finished():
    service, scene_repo = make_service(finished=True)

    with pytest.raises(ValueError, match="scene_finished"):
        await service.edit_message(STORY_ID, SCENE_ID, MESSAGE_ID, "new text")

    scene_repo.update_message.assert_not_awaited()


@pytest.mark.asyncio
async def test_edit_message_raises_when_message_not_found():
    service, scene_repo = make_service(update_side_effect=KeyError(MESSAGE_ID))

    with pytest.raises(KeyError):
        await service.edit_message(STORY_ID, SCENE_ID, MESSAGE_ID, "new text")


@pytest.mark.asyncio
async def test_delete_message_succeeds():
    service, scene_repo = make_service()

    result = await service.delete_message(STORY_ID, SCENE_ID, MESSAGE_ID)

    assert result is None
    scene_repo.delete_message.assert_awaited_once_with(STORY_ID, SCENE_ID, MESSAGE_ID)


@pytest.mark.asyncio
async def test_delete_message_raises_when_scene_finished():
    service, scene_repo = make_service(finished=True)

    with pytest.raises(ValueError, match="scene_finished"):
        await service.delete_message(STORY_ID, SCENE_ID, MESSAGE_ID)

    scene_repo.delete_message.assert_not_awaited()


@pytest.mark.asyncio
async def test_delete_message_raises_when_message_not_found():
    service, scene_repo = make_service(delete_side_effect=KeyError(MESSAGE_ID))

    with pytest.raises(KeyError):
        await service.delete_message(STORY_ID, SCENE_ID, MESSAGE_ID)
