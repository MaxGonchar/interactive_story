import pytest
from unittest.mock import AsyncMock

from app.exceptions import SceneFinishedError
from app.models.domain import Message, SceneDescription, SceneMetadata
from app.services.scene_summarize_service import SceneSummarizeService

STORY_ID = "story-abc"
SCENE_ID = 1


def make_metadata(
    finished: bool = False,
    context: list[str] | None = None,
) -> SceneMetadata:
    return SceneMetadata(
        id=SCENE_ID,
        story_id=STORY_ID,
        character_ids=["c1"],
        user_character_id="u1",
        finished=finished,
        scene_description=SceneDescription(
            general_scene_guide="Guide.",
            writing_style="Concise.",
        ),
        scene_summary=None,
        context=context,
    )


def make_messages(n: int = 2) -> list[Message]:
    msgs = []
    for i in range(n):
        role = "user" if i % 2 == 0 else "assistant"
        msgs.append(Message(id=i + 1, role=role, content=f"Message {i + 1}"))
    return msgs


def make_service(
    metadata: SceneMetadata | None = None,
    messages: list[Message] | None = None,
    llm_return: list[str] | None = None,
    llm_side_effect: Exception | None = None,
) -> tuple[SceneSummarizeService, AsyncMock, AsyncMock]:
    scene_repo = AsyncMock()
    scene_repo.get_metadata.return_value = metadata or make_metadata()
    scene_repo.get_messages.return_value = messages if messages is not None else make_messages()

    llm_client = AsyncMock()
    if llm_side_effect is not None:
        llm_client.invoke.side_effect = llm_side_effect
    else:
        llm_client.invoke.return_value = llm_return if llm_return is not None else ["summary line"]

    service = SceneSummarizeService(scene_repo, llm_client)
    return service, scene_repo, llm_client


@pytest.mark.asyncio
async def test_summarize_happy_path():
    messages = [
        Message(id=1, role="user", content="Hello"),
        Message(id=2, role="assistant", content="Hi there"),
    ]
    context = ["Previous point 1.", "Previous point 2."]
    service, _, llm_client = make_service(
        metadata=make_metadata(context=context),
        messages=messages,
        llm_return=["Summary A", "Summary B"],
    )

    result = await service.summarize(STORY_ID, SCENE_ID)

    assert result == ["Summary A", "Summary B"]
    llm_client.invoke.assert_awaited_once_with(
        context,
        "user:\nHello\n\nassistant:\nHi there",
    )


@pytest.mark.asyncio
async def test_summarize_previous_summary_capped_at_50():
    context = [f"item {i}" for i in range(60)]
    service, _, llm_client = make_service(metadata=make_metadata(context=context))

    await service.summarize(STORY_ID, SCENE_ID)

    called_previous = llm_client.invoke.call_args[0][0]
    assert len(called_previous) == 50
    assert called_previous == context[-50:]


@pytest.mark.asyncio
async def test_summarize_empty_context_passes_empty_list():
    service, _, llm_client = make_service(metadata=make_metadata(context=None))

    await service.summarize(STORY_ID, SCENE_ID)

    called_previous = llm_client.invoke.call_args[0][0]
    assert called_previous == []


@pytest.mark.asyncio
async def test_summarize_no_messages_passes_empty_scene_content():
    service, _, llm_client = make_service(messages=[])

    await service.summarize(STORY_ID, SCENE_ID)

    called_content = llm_client.invoke.call_args[0][1]
    assert called_content == ""


@pytest.mark.asyncio
async def test_summarize_raises_scene_finished_error():
    service, _, llm_client = make_service(metadata=make_metadata(finished=True))

    with pytest.raises(SceneFinishedError):
        await service.summarize(STORY_ID, SCENE_ID)

    llm_client.invoke.assert_not_awaited()


@pytest.mark.asyncio
async def test_summarize_propagates_llm_error():
    service, _, _ = make_service(llm_side_effect=RuntimeError("LLM failure"))

    with pytest.raises(RuntimeError, match="LLM failure"):
        await service.summarize(STORY_ID, SCENE_ID)


@pytest.mark.asyncio
async def test_summarize_scene_content_format():
    messages = [
        Message(id=1, role="user", content="Line one"),
        Message(id=2, role="assistant", content="Line two"),
        Message(id=3, role="user", content="Line three"),
    ]
    service, _, llm_client = make_service(messages=messages)

    await service.summarize(STORY_ID, SCENE_ID)

    called_content = llm_client.invoke.call_args[0][1]
    assert called_content == "user:\nLine one\n\nassistant:\nLine two\n\nuser:\nLine three"
