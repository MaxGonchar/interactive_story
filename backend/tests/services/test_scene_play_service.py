from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from app.exceptions import NoAssistantMessageError, NoUserMessageError, SceneFinishedError
from app.models.domain import CharacterCard, Message
from app.services.scene_play_service import ScenePlayService
from tests.factories import make_scene_metadata

STORY_ID = "story-123"
SCENE_ID = 1


def make_service(
    metadata=None,
    messages=None,
    llm_reply: str = "Assistant reply",
    llm_side_effect=None,
) -> tuple[ScenePlayService, AsyncMock, AsyncMock, MagicMock]:
    scene_repo = AsyncMock()
    scene_repo.get_metadata.return_value = metadata or make_scene_metadata(story_id=STORY_ID, scene_id=SCENE_ID)
    scene_repo.get_messages.return_value = messages if messages is not None else []

    character_repo = AsyncMock()
    character_repo.get_characters.return_value = []
    character_repo.get_character.return_value = CharacterCard(id="user-char", name="Hero")

    llm_client = AsyncMock()
    if llm_side_effect is not None:
        llm_client.invoke.side_effect = llm_side_effect
    else:
        llm_client.invoke.return_value = llm_reply

    service = ScenePlayService(scene_repo, character_repo, llm_client)
    return service, scene_repo, character_repo, llm_client


@pytest.mark.asyncio
async def test_play_context_data_uses_metadata_context():
    metadata = make_scene_metadata(story_id=STORY_ID, scene_id=SCENE_ID, context=["Context line one.", "Context line two."])
    service, _, _, llm_client = make_service(metadata=metadata)
    captured_context = {}

    async def fake_invoke(context, *_):
        captured_context["context_data"] = context.context_data
        return "LLM reply"

    llm_client.invoke.side_effect = fake_invoke
    await service.play(STORY_ID, SCENE_ID, "Hello")

    assert captured_context["context_data"] == ["Context line one.", "Context line two."]


@pytest.mark.asyncio
async def test_play_context_data_empty_when_metadata_context_none():
    service, _, _, llm_client = make_service()
    captured_context = {}

    async def fake_invoke(context, *_):
        captured_context["context_data"] = context.context_data
        return "LLM reply"

    llm_client.invoke.side_effect = fake_invoke
    await service.play(STORY_ID, SCENE_ID, "Hello")

    assert captured_context["context_data"] == []


@pytest.mark.asyncio
async def test_play_includes_user_character_in_context():
    service, _, character_repo, llm_client = make_service()
    captured = {}

    async def fake_invoke(context, *_):
        captured["user_character"] = context.user_character
        return "reply"

    llm_client.invoke.side_effect = fake_invoke
    await service.play(STORY_ID, SCENE_ID, "Hello")

    assert captured["user_character"].id == "user-char"
    character_repo.get_character.assert_awaited_once_with(STORY_ID, "max")


@pytest.mark.asyncio
async def test_play_uses_narrator_context_without_user_character_lookup():
    metadata = make_scene_metadata(story_id=STORY_ID, scene_id=SCENE_ID).model_copy(
        update={"user_character_id": None}
    )
    service, _, character_repo, llm_client = make_service(metadata=metadata)
    captured = {}

    async def fake_invoke(context, *_):
        captured["user_character"] = context.user_character
        return "reply"

    llm_client.invoke.side_effect = fake_invoke

    await service.play(STORY_ID, SCENE_ID, "Advance the scene.")

    assert captured["user_character"] is None
    character_repo.get_character.assert_not_awaited()


@pytest.mark.asyncio
async def test_regenerate_includes_user_character_in_context():
    user_msg = Message(id=1, role="user", content="Hi")
    assistant_msg = Message(id=2, role="assistant", content="Old reply")
    service, scene_repo, character_repo, llm_client = make_service(messages=[user_msg, assistant_msg])
    scene_repo.update_message.return_value = Message(id=2, role="assistant", content="New reply")
    captured = {}

    async def fake_invoke(context, *_):
        captured["user_character"] = context.user_character
        return "New reply"

    llm_client.invoke.side_effect = fake_invoke
    await service.regenerate(STORY_ID, SCENE_ID)

    assert captured["user_character"].id == "user-char"
    character_repo.get_character.assert_awaited_once_with(STORY_ID, "max")


@pytest.mark.asyncio
async def test_regenerate_uses_narrator_context_without_user_character_lookup():
    user_msg = Message(id=1, role="user", content="Advance the scene.")
    assistant_msg = Message(id=2, role="assistant", content="Old reply")
    metadata = make_scene_metadata(story_id=STORY_ID, scene_id=SCENE_ID).model_copy(
        update={"user_character_id": None}
    )
    service, scene_repo, character_repo, llm_client = make_service(
        metadata=metadata,
        messages=[user_msg, assistant_msg],
    )
    scene_repo.update_message.return_value = Message(id=2, role="assistant", content="New reply")
    captured = {}

    async def fake_invoke(context, *_):
        captured["user_character"] = context.user_character
        return "New reply"

    llm_client.invoke.side_effect = fake_invoke

    await service.regenerate(STORY_ID, SCENE_ID)

    assert captured["user_character"] is None
    character_repo.get_character.assert_not_awaited()


@pytest.mark.asyncio
async def test_regenerate_context_data_uses_metadata_context():
    user_msg = Message(id=1, role="user", content="Hi")
    assistant_msg = Message(id=2, role="assistant", content="Old reply")
    metadata = make_scene_metadata(
        story_id=STORY_ID,
        scene_id=SCENE_ID,
        context=["Context line one.", "Context line two."],
    )
    service, scene_repo, _, llm_client = make_service(
        metadata=metadata,
        messages=[user_msg, assistant_msg],
    )
    scene_repo.update_message.return_value = Message(id=2, role="assistant", content="New reply")
    captured_context = {}

    async def fake_invoke(context, *_):
        captured_context["context_data"] = context.context_data
        return "New reply"

    llm_client.invoke.side_effect = fake_invoke

    await service.regenerate(STORY_ID, SCENE_ID)

    assert captured_context["context_data"] == ["Context line one.", "Context line two."]


@pytest.mark.asyncio
async def test_play_returns_both_messages():
    service, scene_repo, _, _ = make_service(llm_reply="Hello back!")

    user_msg, assistant_msg = await service.play(STORY_ID, SCENE_ID, "Hello")

    assert user_msg.role == "user"
    assert user_msg.content == "Hello"
    assert assistant_msg.role == "assistant"
    assert assistant_msg.content == "Hello back!"
    scene_repo.add_messages.assert_awaited_once_with(STORY_ID, SCENE_ID, [user_msg, assistant_msg])


@pytest.mark.asyncio
async def test_play_raises_when_scene_finished():
    service, scene_repo, _, _ = make_service(metadata=make_scene_metadata(story_id=STORY_ID, scene_id=SCENE_ID, finished=True))

    with pytest.raises(SceneFinishedError):
        await service.play(STORY_ID, SCENE_ID, "Hello")

    scene_repo.add_messages.assert_not_awaited()


@pytest.mark.asyncio
async def test_play_does_not_persist_on_llm_failure():
    service, scene_repo, _, _ = make_service(llm_side_effect=RuntimeError("LLM down"))

    with pytest.raises(RuntimeError, match="LLM down"):
        await service.play(STORY_ID, SCENE_ID, "Hello")

    scene_repo.add_messages.assert_not_awaited()


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


@pytest.mark.asyncio
async def test_regenerate_replaces_last_assistant_message():
    user_msg = Message(id=1, role="user", content="Hi")
    assistant_msg = Message(id=2, role="assistant", content="Old reply")
    service, scene_repo, _, _ = make_service(messages=[user_msg, assistant_msg], llm_reply="New reply")
    scene_repo.update_message.return_value = Message(id=2, role="assistant", content="New reply")

    result = await service.regenerate(STORY_ID, SCENE_ID)

    scene_repo.update_message.assert_awaited_once_with(STORY_ID, SCENE_ID, 2, "New reply")
    assert result.id == 2
    assert result.role == "assistant"
    assert result.content == "New reply"


@pytest.mark.asyncio
async def test_regenerate_raises_when_scene_finished():
    user_msg = Message(id=1, role="user", content="Hi")
    assistant_msg = Message(id=2, role="assistant", content="Old reply")
    service, scene_repo, _, _ = make_service(
        metadata=make_scene_metadata(story_id=STORY_ID, scene_id=SCENE_ID, finished=True),
        messages=[user_msg, assistant_msg],
    )

    with pytest.raises(SceneFinishedError):
        await service.regenerate(STORY_ID, SCENE_ID)

    scene_repo.update_message.assert_not_awaited()


@pytest.mark.asyncio
async def test_regenerate_raises_when_no_messages():
    service, scene_repo, _, _ = make_service(messages=[])

    with pytest.raises(NoAssistantMessageError):
        await service.regenerate(STORY_ID, SCENE_ID)

    scene_repo.update_message.assert_not_awaited()


@pytest.mark.asyncio
async def test_regenerate_raises_when_last_message_is_user():
    user_msg = Message(id=1, role="user", content="Hi")
    service, scene_repo, _, _ = make_service(messages=[user_msg])

    with pytest.raises(NoAssistantMessageError):
        await service.regenerate(STORY_ID, SCENE_ID)

    scene_repo.update_message.assert_not_awaited()


@pytest.mark.asyncio
async def test_regenerate_does_not_persist_on_llm_failure():
    user_msg = Message(id=1, role="user", content="Hi")
    assistant_msg = Message(id=2, role="assistant", content="Old reply")
    service, scene_repo, _, _ = make_service(messages=[user_msg, assistant_msg], llm_side_effect=RuntimeError("LLM fail"))

    with pytest.raises(RuntimeError, match="LLM fail"):
        await service.regenerate(STORY_ID, SCENE_ID)

    scene_repo.update_message.assert_not_awaited()


@pytest.mark.asyncio
async def test_regenerate_raises_no_user_message_when_only_assistant():
    # Only the entry-point assistant message exists — no preceding user message
    assistant_msg = Message(id=1, role="assistant", content="Entry point text")
    service, scene_repo, _, _ = make_service(messages=[assistant_msg])

    with pytest.raises(NoUserMessageError):
        await service.regenerate(STORY_ID, SCENE_ID)

    scene_repo.update_message.assert_not_awaited()
