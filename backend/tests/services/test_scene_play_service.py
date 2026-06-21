import pytest
from unittest.mock import AsyncMock, MagicMock
from app.models.domain import Message, SceneDescription, SceneMetadata, SceneRef, StoryMeta
from app.services.scene_play_service import ScenePlayService

def _make_story_meta_with_finished_scenes():
    return StoryMeta(
        id="story-1",
        title="Test Story",
        user_character_id="max",
        character_ids=["c1"],
        scenes=[
            SceneRef(id=0, finished=True, summary=["Scene zero happened.", "More context."]),
            SceneRef(id=1, finished=True, summary=["Scene one happened."]),
            SceneRef(id=2, finished=False, summary=None),  # current scene
            SceneRef(id=3, finished=True, summary=["Should not be included."]),
        ],
        active_scene_id=2,
    )

@pytest.mark.asyncio
async def test_play_populates_context_data_from_prior_finished_scenes():
    story_meta = _make_story_meta_with_finished_scenes()
    service, _, _, llm_client, _ = make_service(story_meta=story_meta)
    # Patch llm_client to capture context
    captured_context = {}
    async def fake_invoke(context, *_):
        captured_context['context_data'] = context.context_data
        return "LLM reply"
    llm_client.invoke.side_effect = fake_invoke
    await service.play(story_meta.id, 2, "Hello")
    # Should include summaries from scenes 0 and 1 only
    assert captured_context['context_data'] == ["Scene zero happened.", "More context.", "Scene one happened."]

@pytest.mark.asyncio
async def test_play_context_data_empty_when_no_prior_finished():
    from app.models.domain import SceneRef, StoryMeta
    story_meta = StoryMeta(
        id="story-2",
        title="Test Story",
        user_character_id="max",
        character_ids=["c1"],
        scenes=[
            SceneRef(id=0, finished=False, summary=None),
            SceneRef(id=1, finished=False, summary=None),  # current scene
        ],
        active_scene_id=1,
    )
    service, _, _, llm_client, _ = make_service(story_meta=story_meta)
    captured_context = {}
    async def fake_invoke(context, *_):
        captured_context['context_data'] = context.context_data
        return "LLM reply"
    llm_client.invoke.side_effect = fake_invoke
    await service.play(story_meta.id, 1, "Hello")
    assert captured_context['context_data'] == []

@pytest.mark.asyncio
async def test_play_excludes_finished_scenes_after_current():
    from app.models.domain import SceneRef, StoryMeta
    story_meta = StoryMeta(
        id="story-3",
        title="Test Story",
        user_character_id="max",
        character_ids=["c1"],
        scenes=[
            SceneRef(id=0, finished=True, summary=["Scene zero happened."]),
            SceneRef(id=1, finished=False, summary=None),  # current scene
            SceneRef(id=2, finished=True, summary=["Should not be included."]),
        ],
        active_scene_id=1,
    )
    service, _, _, llm_client, _ = make_service(story_meta=story_meta)
    captured_context = {}
    async def fake_invoke(context, *_):
        captured_context['context_data'] = context.context_data
        return "LLM reply"
    llm_client.invoke.side_effect = fake_invoke
    await service.play(story_meta.id, 1, "Hello")
    # Only scene 0 summary should be included
    assert captured_context['context_data'] == ["Scene zero happened."]


STORY_ID = "story-123"
SCENE_ID = 1


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


from app.models.domain import SceneRef, StoryMeta
from unittest.mock import AsyncMock, MagicMock

def make_service(
    metadata: SceneMetadata | None = None,
    messages: list[Message] | None = None,
    llm_reply: str = "Assistant reply",
    llm_side_effect: Exception | None = None,
    story_meta: StoryMeta | None = None,
) -> tuple[ScenePlayService, AsyncMock, AsyncMock, MagicMock, AsyncMock]:
    scene_repo = AsyncMock()
    scene_repo.get_metadata.return_value = metadata or make_scene_metadata()
    scene_repo.get_messages.return_value = messages if messages is not None else []

    character_repo = AsyncMock()
    character_repo.get_characters.return_value = []
    from app.models.domain import CharacterCard
    character_repo.get_character.return_value = CharacterCard(
        id="user-char", story_id=STORY_ID, name="Hero"
    )

    llm_client = AsyncMock()
    if llm_side_effect is not None:
        llm_client.invoke.side_effect = llm_side_effect
    else:
        llm_client.invoke.return_value = llm_reply

    story_repo = AsyncMock()
    if story_meta is None:
        # Default: one unfinished scene
        story_meta = StoryMeta(
            id=STORY_ID,
            title="Test Story",
            user_character_id="max",
            character_ids=["c1"],
            scenes=[SceneRef(id=SCENE_ID, finished=False, summary=None)],
            active_scene_id=SCENE_ID,
        )
    story_repo.get_story.return_value = story_meta

    service = ScenePlayService(scene_repo, character_repo, llm_client, story_repo)
    return service, scene_repo, character_repo, llm_client, story_repo


@pytest.mark.asyncio
async def test_play_includes_user_character_in_context():
    service, _, character_repo, llm_client, _ = make_service()
    captured = {}
    async def fake_invoke(context, *_):
        captured["user_character"] = context.user_character
        return "reply"
    llm_client.invoke.side_effect = fake_invoke

    await service.play(STORY_ID, SCENE_ID, "Hello")

    assert captured["user_character"].id == "user-char"
    character_repo.get_character.assert_awaited_once_with(STORY_ID, "max")


@pytest.mark.asyncio
async def test_regenerate_includes_user_character_in_context():
    user_msg = Message(id=1, role="user", content="Hi")
    assistant_msg = Message(id=2, role="assistant", content="Old reply")
    service, scene_repo, character_repo, llm_client, _ = make_service(
        messages=[user_msg, assistant_msg]
    )
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
async def test_play_returns_both_messages():
    service, scene_repo, _, _, _ = make_service(llm_reply="Hello back!")

    user_msg, assistant_msg = await service.play(STORY_ID, SCENE_ID, "Hello")

    assert user_msg.role == "user"
    assert user_msg.content == "Hello"
    assert assistant_msg.role == "assistant"
    assert assistant_msg.content == "Hello back!"
    scene_repo.add_message.assert_awaited()
    assert scene_repo.add_message.await_count == 2


@pytest.mark.asyncio
async def test_play_raises_when_scene_finished():
    service, scene_repo, _, _, _ = make_service(metadata=make_scene_metadata(finished=True))

    with pytest.raises(ValueError, match="scene_finished"):
        await service.play(STORY_ID, SCENE_ID, "Hello")

    scene_repo.add_message.assert_not_awaited()


@pytest.mark.asyncio
async def test_play_does_not_persist_on_llm_failure():
    service, scene_repo, _, _, _ = make_service(llm_side_effect=RuntimeError("LLM down"))

    with pytest.raises(RuntimeError, match="LLM down"):
        await service.play(STORY_ID, SCENE_ID, "Hello")

    scene_repo.add_message.assert_not_awaited()


@pytest.mark.asyncio
async def test_play_assigns_correct_message_ids():
    existing = [
        Message(id=3, role="user", content="msg3"),
        Message(id=5, role="assistant", content="msg5"),
    ]
    service, _, _, _, _ = make_service(messages=existing)

    user_msg, assistant_msg = await service.play(STORY_ID, SCENE_ID, "New input")

    assert user_msg.id == 6
    assert assistant_msg.id == 7


@pytest.mark.asyncio
async def test_regenerate_replaces_last_assistant_message():
    user_msg = Message(id=1, role="user", content="Hi")
    assistant_msg = Message(id=2, role="assistant", content="Old reply")
    service, scene_repo, _, _, _ = make_service(messages=[user_msg, assistant_msg], llm_reply="New reply")
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
    service, scene_repo, _, _, _ = make_service(metadata=make_scene_metadata(finished=True), messages=[user_msg, assistant_msg])

    with pytest.raises(ValueError, match="scene_finished"):
        await service.regenerate(STORY_ID, SCENE_ID)
    scene_repo.update_message.assert_not_awaited()


@pytest.mark.asyncio
async def test_regenerate_raises_when_no_messages():
    service, scene_repo, _, _, _ = make_service(messages=[])

    with pytest.raises(ValueError, match="no_assistant_message"):
        await service.regenerate(STORY_ID, SCENE_ID)
    scene_repo.update_message.assert_not_awaited()


@pytest.mark.asyncio
async def test_regenerate_raises_when_last_message_is_user():
    user_msg = Message(id=1, role="user", content="Hi")
    service, scene_repo, _, _, _ = make_service(messages=[user_msg])

    with pytest.raises(ValueError, match="no_assistant_message"):
        await service.regenerate(STORY_ID, SCENE_ID)
    scene_repo.update_message.assert_not_awaited()


@pytest.mark.asyncio
async def test_regenerate_does_not_persist_on_llm_failure():
    user_msg = Message(id=1, role="user", content="Hi")
    assistant_msg = Message(id=2, role="assistant", content="Old reply")
    service, scene_repo, _, _, _ = make_service(messages=[user_msg, assistant_msg], llm_side_effect=RuntimeError("LLM fail"))

    with pytest.raises(RuntimeError, match="LLM fail"):
        await service.regenerate(STORY_ID, SCENE_ID)
    scene_repo.update_message.assert_not_awaited()


@pytest.mark.asyncio
async def test_regenerate_raises_no_user_message_when_only_assistant():
    # Only the entry-point assistant message exists — no preceding user message
    assistant_msg = Message(id=1, role="assistant", content="Entry point text")
    service, scene_repo, _, _, _ = make_service(messages=[assistant_msg])

    with pytest.raises(ValueError, match="no_user_message"):
        await service.regenerate(STORY_ID, SCENE_ID)
    scene_repo.update_message.assert_not_awaited()
