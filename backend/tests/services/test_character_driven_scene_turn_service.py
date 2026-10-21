from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from app.exceptions import (
    CharacterNotInSceneError,
    InvalidModelError,
    LLMError,
    NotFoundError,
    SceneFinishedError,
)
from app.llm.models import LLMCompletion
from app.models.api import (
    CharacterDrivenCharacterActor,
    CharacterDrivenCharacterTurnRequest,
    CharacterDrivenPlayerActor,
    CharacterDrivenPlayerTurnRequest,
)
from app.models.domain import (
    CharacterCard,
    CharacterDrivenInput,
    CharacterDrivenLLMData,
    CharacterDrivenMessage,
    ModelMetadata,
    ModelRegistry,
    SceneDescription,
    SceneMetadata,
    StoryMeta,
    TokenUsage,
)
from app.services.character_driven_scene_turn_service import (
    CharacterDrivenSceneTurnService,
)
from app.services.model_registry_service import ModelRegistryService

STORY_ID = "story-abc"
SCENE_ID = 1

_OPENING = CharacterDrivenMessage(
    id=1,
    narration="A bell rings.",
    llm_data=CharacterDrivenLLMData(
        character_model_id="model-a", narrator_model_id="model-b"
    ),
)


def make_metadata(
    user_character_id: str | None = "hero", finished: bool = False
) -> SceneMetadata:
    return SceneMetadata(
        id=SCENE_ID,
        story_id=STORY_ID,
        character_ids=["villain"],
        user_character_id=user_character_id,
        finished=finished,
        scene_description=SceneDescription(
            general_scene_guide="Build tension.", writing_style="Cinematic."
        ),
        context=["Previously..."],
    )


def make_completion(content: str = "The hero steps forward.") -> LLMCompletion:
    return LLMCompletion(
        content=content,
        model_id="provider-b",
        provider_model_id="provider-b",
        provider_created=1,
        usage=TokenUsage(prompt_tokens=1, completion_tokens=2, total_tokens=3),
        duration_ms=10,
        result="The hero steps forward.",
    )


def make_request(action: str = "I step forward.") -> CharacterDrivenPlayerTurnRequest:
    return CharacterDrivenPlayerTurnRequest(
        actor=CharacterDrivenPlayerActor(type="player"),
        action=action,
        character_model_id="model-a",
        narrator_model_id="model-b",
    )


def make_character_request(
    character_id: str = "villain", guidance: str | None = ""
) -> CharacterDrivenCharacterTurnRequest:
    return CharacterDrivenCharacterTurnRequest(
        actor=CharacterDrivenCharacterActor(
            type="character", character_id=character_id
        ),
        guidance=guidance,
        character_model_id="model-a",
        narrator_model_id="model-b",
    )


def make_service(
    metadata: SceneMetadata | None = None,
    narrator_error: Exception | None = None,
    character_error: Exception | None = None,
):
    story_repo = AsyncMock()
    story_repo.get_story.return_value = StoryMeta(
        id=STORY_ID,
        title="T",
        scenes=[],
        active_scene_id=None,
        type="character_driven",
    )
    scene_repo = AsyncMock()
    scene_repo.get_metadata.return_value = metadata or make_metadata()
    cd_repo = AsyncMock()
    cd_repo.get_messages.return_value = [_OPENING]
    cd_repo.append_message.side_effect = lambda s, sc, inp, narration, llm_data: (
        CharacterDrivenMessage(
            id=2, input=inp, narration=narration, llm_data=llm_data
        )
    )
    character_repo = AsyncMock()
    character_repo.get_character.side_effect = lambda story_id, character_id: (
        CharacterCard(id=character_id, name=character_id.title())
    )
    registry_repo = AsyncMock()
    registry_repo.get_registry.return_value = ModelRegistry(
        models={
            "model-a": ModelMetadata(id="model-a", name="A", provider_model_id="pa"),
            "model-b": ModelMetadata(id="model-b", name="B", provider_model_id="pb"),
        },
        default_model_id="model-a",
    )
    usage_repo = AsyncMock()
    narrator = MagicMock()
    narrator.invoke = (
        AsyncMock(side_effect=narrator_error)
        if narrator_error is not None
        else AsyncMock(return_value=make_completion())
    )
    factory = MagicMock(return_value=narrator)
    character_agent = MagicMock()
    character_agent.invoke = (
        AsyncMock(side_effect=character_error)
        if character_error is not None
        else AsyncMock(
            return_value=make_completion(
                "INTERNAL: The path is clear. ACTION: The villain raises a lantern."
            )
        )
    )
    character_agent_factory = MagicMock(return_value=character_agent)
    service = CharacterDrivenSceneTurnService(
        story_repo,
        scene_repo,
        cd_repo,
        character_repo,
        ModelRegistryService(registry_repo),
        usage_repo,
        factory,
        character_agent_factory,
    )
    return (
        service,
        cd_repo,
        usage_repo,
        narrator,
        factory,
        character_agent,
        character_agent_factory,
        character_repo,
    )


@pytest.mark.asyncio
async def test_submit_player_turn_persists_item_and_records_usage():
    service, cd_repo, usage_repo, narrator, factory, _, _, _ = make_service()

    metadata, message = await service.submit_turn(STORY_ID, SCENE_ID, make_request())

    assert metadata == make_metadata()
    assert message == CharacterDrivenMessage(
        id=2,
        input=CharacterDrivenInput(author="hero", action="I step forward."),
        narration="The hero steps forward.",
        llm_data=CharacterDrivenLLMData(
            character_model_id=None, narrator_model_id="model-b"
        ),
    )
    factory.assert_called_once_with("pb")
    narrator.invoke.assert_awaited_once_with(
        story_context=["Previously..."],
        general_scene_guide="Build tension.",
        writing_style="Cinematic.",
        scene_narrations=["A bell rings."],
        actor_name="Hero",
        current_turn="I step forward.",
    )
    usage_repo.append.assert_awaited_once()
    story_id, usage = usage_repo.append.await_args.args
    assert story_id == STORY_ID
    assert (usage.operation, usage.model_id, usage.scene_id, usage.message_id) == (
        "narration",
        "model-b",
        SCENE_ID,
        2,
    )


@pytest.mark.asyncio
async def test_submit_player_turn_without_user_character_uses_player_name():
    service, cd_repo, _, narrator, _, _, _, _ = make_service(
        metadata=make_metadata(user_character_id=None)
    )

    await service.submit_turn(STORY_ID, SCENE_ID, make_request())

    assert narrator.invoke.await_args.kwargs["actor_name"] == "Player"
    cd_repo.append_message.assert_awaited_once_with(
        STORY_ID,
        SCENE_ID,
        CharacterDrivenInput(author=None, action="I step forward."),
        "The hero steps forward.",
        CharacterDrivenLLMData(character_model_id=None, narrator_model_id="model-b"),
    )


@pytest.mark.asyncio
async def test_submit_turn_narrator_failure_persists_nothing(caplog):
    service, cd_repo, usage_repo, _, _, _, _, _ = make_service(
        narrator_error=LLMError("boom")
    )

    with caplog.at_level("ERROR"), pytest.raises(LLMError):
        await service.submit_turn(STORY_ID, SCENE_ID, make_request())

    cd_repo.append_message.assert_not_awaited()
    usage_repo.append.assert_not_awaited()
    assert "stage=narration" in caplog.text


@pytest.mark.asyncio
async def test_submit_character_turn_persists_action_and_records_both_usages():
    (
        service,
        cd_repo,
        usage_repo,
        narrator,
        narrator_factory,
        character_agent,
        character_agent_factory,
        _,
    ) = make_service()

    metadata, message = await service.submit_turn(
        STORY_ID, SCENE_ID, make_character_request()
    )

    raw_action = "INTERNAL: The path is clear. ACTION: The villain raises a lantern."
    assert metadata == make_metadata()
    assert message == CharacterDrivenMessage(
        id=2,
        input=CharacterDrivenInput(
            author="villain", action=raw_action, guidance=""
        ),
        narration="The hero steps forward.",
        llm_data=CharacterDrivenLLMData(
            character_model_id="model-a", narrator_model_id="model-b"
        ),
    )
    character_agent_factory.assert_called_once_with("pa")
    character_agent.invoke.assert_awaited_once_with(
        character=CharacterCard(id="villain", name="Villain"),
        scene_narrations=["A bell rings."],
        player_guidance="",
    )
    narrator_factory.assert_called_once_with("pb")
    narrator.invoke.assert_awaited_once_with(
        story_context=["Previously..."],
        general_scene_guide="Build tension.",
        writing_style="Cinematic.",
        scene_narrations=["A bell rings."],
        actor_name="Villain",
        current_turn=raw_action,
    )
    cd_repo.append_message.assert_awaited_once_with(
        STORY_ID,
        SCENE_ID,
        CharacterDrivenInput(author="villain", action=raw_action, guidance=""),
        "The hero steps forward.",
        CharacterDrivenLLMData(
            character_model_id="model-a", narrator_model_id="model-b"
        ),
    )
    assert len(usage_repo.append.await_args_list) == 2
    usages = [call.args[1] for call in usage_repo.append.await_args_list]
    assert [
        (
            usage.operation,
            usage.model_id,
            usage.scene_id,
            usage.message_id,
            usage.character_id,
        )
        for usage in usages
    ] == [
        ("character_action", "model-a", SCENE_ID, message.id, "villain"),
        ("narration", "model-b", SCENE_ID, message.id, None),
    ]


@pytest.mark.asyncio
async def test_submit_character_turn_agent_failure_persists_nothing(caplog):
    (
        service,
        cd_repo,
        usage_repo,
        narrator,
        _,
        character_agent,
        _,
        _,
    ) = make_service(character_error=LLMError("boom"))

    with caplog.at_level("ERROR"), pytest.raises(LLMError):
        await service.submit_turn(STORY_ID, SCENE_ID, make_character_request())

    character_agent.invoke.assert_awaited_once()
    narrator.invoke.assert_not_awaited()
    cd_repo.append_message.assert_not_awaited()
    usage_repo.append.assert_not_awaited()
    assert "stage=character_action" in caplog.text


@pytest.mark.asyncio
async def test_submit_character_turn_narrator_failure_persists_nothing(caplog):
    (
        service,
        cd_repo,
        usage_repo,
        narrator,
        _,
        character_agent,
        _,
        _,
    ) = make_service(narrator_error=LLMError("boom"))

    with caplog.at_level("ERROR"), pytest.raises(LLMError):
        await service.submit_turn(STORY_ID, SCENE_ID, make_character_request())

    character_agent.invoke.assert_awaited_once()
    narrator.invoke.assert_awaited_once()
    cd_repo.append_message.assert_not_awaited()
    usage_repo.append.assert_not_awaited()
    assert "stage=narration" in caplog.text


@pytest.mark.asyncio
async def test_submit_character_turn_rejects_character_not_in_scene():
    service, cd_repo, usage_repo, narrator, _, agent, _, character_repo = (
        make_service()
    )

    with pytest.raises(CharacterNotInSceneError):
        await service.submit_turn(
            STORY_ID, SCENE_ID, make_character_request(character_id="outsider")
        )

    character_repo.get_character.assert_not_awaited()
    agent.invoke.assert_not_awaited()
    narrator.invoke.assert_not_awaited()
    cd_repo.append_message.assert_not_awaited()
    usage_repo.append.assert_not_awaited()


@pytest.mark.asyncio
async def test_submit_character_turn_missing_character_propagates_not_found():
    service, cd_repo, usage_repo, narrator, _, agent, _, character_repo = (
        make_service()
    )
    character_repo.get_character.side_effect = NotFoundError("missing character")

    with pytest.raises(NotFoundError, match="missing character"):
        await service.submit_turn(STORY_ID, SCENE_ID, make_character_request())

    agent.invoke.assert_not_awaited()
    narrator.invoke.assert_not_awaited()
    cd_repo.append_message.assert_not_awaited()
    usage_repo.append.assert_not_awaited()


@pytest.mark.asyncio
async def test_submit_turn_rejects_finished_scene():
    service, cd_repo, usage_repo, narrator, _, _, _, _ = make_service(
        metadata=make_metadata(finished=True)
    )

    with pytest.raises(SceneFinishedError):
        await service.submit_turn(STORY_ID, SCENE_ID, make_request())

    narrator.invoke.assert_not_awaited()
    cd_repo.append_message.assert_not_awaited()
    usage_repo.append.assert_not_awaited()


@pytest.mark.asyncio
@pytest.mark.parametrize("field", ["character_model_id", "narrator_model_id"])
async def test_submit_turn_rejects_unknown_model(field):
    service, cd_repo, usage_repo, narrator, _, _, _, _ = make_service()
    request = make_request().model_copy(update={field: "unknown"})

    with pytest.raises(InvalidModelError):
        await service.submit_turn(STORY_ID, SCENE_ID, request)

    narrator.invoke.assert_not_awaited()
    cd_repo.append_message.assert_not_awaited()
    usage_repo.append.assert_not_awaited()


@pytest.mark.asyncio
async def test_submit_turn_missing_scene_propagates_not_found():
    service, cd_repo, _, _, _, _, _, _ = make_service()
    service._scene_repo.get_metadata.side_effect = NotFoundError("missing")

    with pytest.raises(NotFoundError):
        await service.submit_turn(STORY_ID, SCENE_ID, make_request())

    cd_repo.append_message.assert_not_awaited()
