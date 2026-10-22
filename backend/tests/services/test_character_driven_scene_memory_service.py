from __future__ import annotations

from unittest.mock import AsyncMock

import pytest

from app.exceptions import (
    CharacterNotParticipantError,
    LLMError,
    NotFoundError,
    SceneFinishedError,
)
from app.llm.models import LLMCompletion
from app.models.domain import CharacterCard, CharacterDrivenMessage, TokenUsage
from app.services.character_driven_scene_memory_service import (
    CharacterDrivenSceneMemoryService,
)
from tests.factories import make_scene_metadata

STORY_ID = "story-abc"
SCENE_ID = 1

CARDS = {
    "captain": CharacterCard(id="captain", name="Captain"),
    "navigator": CharacterCard(id="navigator", name="Navigator"),
    "hero": CharacterCard(id="hero", name="Hero"),
}


def make_messages() -> list[CharacterDrivenMessage]:
    return [
        CharacterDrivenMessage(
            id=1,
            input=None,
            narration="Fog rolls in.",
            llm_data={"character_model_id": "c", "narrator_model_id": "n"},
        )
    ]


def make_completion(result: list[str]) -> LLMCompletion:
    return LLMCompletion(
        content="{}",
        model_id="summary-model",
        provider_model_id="provider-summary",
        provider_created=1700000001,
        duration_ms=200,
        usage=TokenUsage(prompt_tokens=20, completion_tokens=6, total_tokens=26),
    ).model_copy(update={"result": result})


def make_service(
    metadata=None,
    llm_return: list[str] | None = None,
    llm_side_effect: Exception | None = None,
    characters_side_effect: Exception | None = None,
):
    story_repo = AsyncMock()
    scene_repo = AsyncMock()
    scene_repo.get_metadata.return_value = metadata or make_scene_metadata(
        story_id=STORY_ID,
        scene_id=SCENE_ID,
        character_ids=["captain", "navigator"],
        user_character_id="hero",
    )
    cd_repo = AsyncMock()
    cd_repo.get_messages.return_value = make_messages()
    character_repo = AsyncMock()
    if characters_side_effect is not None:
        character_repo.get_characters.side_effect = characters_side_effect
    else:
        character_repo.get_characters.side_effect = lambda _story_id, ids: [
            CARDS[cid] for cid in ids
        ]
    llm_client = AsyncMock()
    if llm_side_effect is not None:
        llm_client.invoke.side_effect = llm_side_effect
    else:
        llm_client.invoke.return_value = make_completion(
            ["Memory A"] if llm_return is None else llm_return
        )
    usage_repo = AsyncMock()
    service = CharacterDrivenSceneMemoryService(
        story_repo, scene_repo, cd_repo, character_repo, llm_client, usage_repo
    )
    return service, llm_client, usage_repo


# --- draft ---


@pytest.mark.asyncio
@pytest.mark.parametrize("character_id", ["navigator", "hero"])
async def test_draft_returns_items_for_npc_and_player_character(character_id):
    service, llm_client, _ = make_service(llm_return=["Memory A", "Memory B"])

    result = await service.draft(STORY_ID, SCENE_ID, character_id)

    assert result == ["Memory A", "Memory B"]
    llm_client.invoke.assert_awaited_once_with(
        CARDS[character_id],
        make_messages(),
        {"captain": "Captain", "navigator": "Navigator", "hero": "Hero"},
    )


@pytest.mark.asyncio
async def test_draft_allows_empty_result():
    service, _, _ = make_service(llm_return=[])

    result = await service.draft(STORY_ID, SCENE_ID, "captain")

    assert result == []


@pytest.mark.asyncio
async def test_draft_records_usage_with_character_id():
    service, _, usage_repo = make_service()

    await service.draft(STORY_ID, SCENE_ID, "navigator")

    usage_repo.append.assert_awaited_once()
    story_id, usage = usage_repo.append.await_args.args
    assert story_id == STORY_ID
    assert (usage.operation, usage.scene_id, usage.character_id) == (
        "character_memory_update",
        SCENE_ID,
        "navigator",
    )


@pytest.mark.asyncio
async def test_draft_raises_when_character_not_in_scene():
    service, llm_client, usage_repo = make_service()

    with pytest.raises(CharacterNotParticipantError):
        await service.draft(STORY_ID, SCENE_ID, "stranger")

    llm_client.invoke.assert_not_awaited()
    usage_repo.append.assert_not_awaited()


@pytest.mark.asyncio
async def test_draft_without_player_character_rejects_player_id():
    metadata = make_scene_metadata(
        story_id=STORY_ID,
        scene_id=SCENE_ID,
        character_ids=["captain"],
        user_character_id=None,
    )
    service, _, _ = make_service(metadata=metadata)

    with pytest.raises(CharacterNotParticipantError):
        await service.draft(STORY_ID, SCENE_ID, "hero")


@pytest.mark.asyncio
async def test_draft_raises_when_character_file_missing():
    service, llm_client, usage_repo = make_service(
        characters_side_effect=NotFoundError("Character 'navigator' not found")
    )

    with pytest.raises(NotFoundError):
        await service.draft(STORY_ID, SCENE_ID, "navigator")

    llm_client.invoke.assert_not_awaited()
    usage_repo.append.assert_not_awaited()


@pytest.mark.asyncio
async def test_draft_raises_when_scene_finished():
    metadata = make_scene_metadata(
        story_id=STORY_ID, scene_id=SCENE_ID, finished=True
    )
    service, llm_client, _ = make_service(metadata=metadata)

    with pytest.raises(SceneFinishedError):
        await service.draft(STORY_ID, SCENE_ID, "captain")

    llm_client.invoke.assert_not_awaited()


@pytest.mark.asyncio
async def test_draft_llm_error_propagates_and_records_nothing():
    service, _, usage_repo = make_service(llm_side_effect=LLMError("boom"))

    with pytest.raises(LLMError):
        await service.draft(STORY_ID, SCENE_ID, "captain")

    usage_repo.append.assert_not_awaited()
