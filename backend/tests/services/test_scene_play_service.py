from unittest.mock import AsyncMock, MagicMock

import pytest

from app.models.domain import Message, SceneDescription, SceneMetadata
from app.services.scene_play_service import ScenePlayService


STORY_ID = "story-123"
SCENE_ID = 1


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
    messages: list[Message] | None = None,
    llm_reply: str = "Assistant reply",
    llm_side_effect: Exception | None = None,
) -> tuple[ScenePlayService, AsyncMock, AsyncMock, MagicMock]:
    scene_repo = AsyncMock()
    scene_repo.get_metadata.return_value = metadata or make_scene_metadata()
    scene_repo.get_messages.return_value = messages if messages is not None else []

    character_repo = AsyncMock()
    character_repo.get_characters.return_value = []

    llm_client = AsyncMock()
    if llm_side_effect is not None:
        llm_client.invoke.side_effect = llm_side_effect
    else:
        llm_client.invoke.return_value = llm_reply

    service = ScenePlayService(scene_repo, character_repo, llm_client)
    return service, scene_repo, character_repo, llm_client


@pytest.mark.asyncio
async def test_play_returns_both_messages():
    service, scene_repo, _, _ = make_service(llm_reply="Hello back!")

    user_msg, assistant_msg = await service.play(STORY_ID, SCENE_ID, "Hello")

    assert user_msg.role == "user"
    assert user_msg.content == "Hello"
    assert assistant_msg.role == "assistant"
    assert assistant_msg.content == "Hello back!"
    scene_repo.add_message.assert_awaited()
    assert scene_repo.add_message.await_count == 2


@pytest.mark.asyncio
async def test_play_raises_when_scene_finished():
    service, scene_repo, _, _ = make_service(metadata=make_scene_metadata(finished=True))

    with pytest.raises(ValueError, match="scene_finished"):
        await service.play(STORY_ID, SCENE_ID, "Hello")

    scene_repo.add_message.assert_not_awaited()


@pytest.mark.asyncio
async def test_play_does_not_persist_on_llm_failure():
    service, scene_repo, _, _ = make_service(llm_side_effect=RuntimeError("LLM down"))

    with pytest.raises(RuntimeError, match="LLM down"):
        await service.play(STORY_ID, SCENE_ID, "Hello")

    scene_repo.add_message.assert_not_awaited()


@pytest.mark.asyncio
async def test_play_assigns_correct_message_ids():
    existing = [
        Message(id=3, role="user", content="msg3"),
        Message(id=5, role="assistant", content="msg5"),
    ]
    service, _, _, _ = make_service(messages=existing)

    user_msg, assistant_msg = await service.play(STORY_ID, SCENE_ID, "New input")

    assert user_msg.id == 6
    assert assistant_msg.id == 7
