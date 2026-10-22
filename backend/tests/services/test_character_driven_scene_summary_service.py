from __future__ import annotations

from unittest.mock import AsyncMock

import pytest

from app.exceptions import LLMError, NotFoundError, SceneFinishedError
from app.llm.models import LLMCompletion
from app.models.domain import CharacterDrivenMessage, TokenUsage
from app.services.character_driven_scene_summary_service import (
    CharacterDrivenSceneSummaryService,
)
from tests.factories import make_scene_metadata

STORY_ID = "story-abc"
SCENE_ID = 1


def make_messages(narrations: list[str]) -> list[CharacterDrivenMessage]:
    return [
        CharacterDrivenMessage(
            id=index,
            input=None,
            narration=narration,
            llm_data={"character_model_id": "c", "narrator_model_id": "n"},
        )
        for index, narration in enumerate(narrations, start=1)
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
    narrations: list[str] | None = None,
    llm_return: list[str] | None = None,
    llm_side_effect: Exception | None = None,
):
    story_repo = AsyncMock()
    scene_repo = AsyncMock()
    scene_repo.get_metadata.return_value = metadata or make_scene_metadata(
        story_id=STORY_ID, scene_id=SCENE_ID
    )
    cd_repo = AsyncMock()
    cd_repo.get_messages.return_value = make_messages(narrations or ["One."])
    llm_client = AsyncMock()
    if llm_side_effect is not None:
        llm_client.invoke.side_effect = llm_side_effect
    else:
        llm_client.invoke.return_value = make_completion(llm_return or ["Draft"])
    usage_repo = AsyncMock()
    service = CharacterDrivenSceneSummaryService(
        story_repo, scene_repo, cd_repo, llm_client, usage_repo
    )
    return service, story_repo, llm_client, usage_repo


# --- draft ---


@pytest.mark.asyncio
async def test_draft_passes_context_and_joined_narrations_to_llm():
    metadata = make_scene_metadata(
        story_id=STORY_ID, scene_id=SCENE_ID, context=["Fact A.", "Fact B."]
    )
    service, story_repo, llm_client, _ = make_service(
        metadata=metadata,
        narrations=["First.", "Second."],
        llm_return=["Draft A", "Draft B"],
    )

    result = await service.draft(STORY_ID, SCENE_ID)

    assert result == ["Draft A", "Draft B"]
    story_repo.get_story.assert_awaited_once_with(STORY_ID)
    llm_client.invoke.assert_awaited_once_with(
        ["Fact A.", "Fact B."], "First.\n\nSecond."
    )


@pytest.mark.asyncio
async def test_draft_uses_only_last_50_context_items():
    context = [f"Fact {i}" for i in range(60)]
    metadata = make_scene_metadata(
        story_id=STORY_ID, scene_id=SCENE_ID, context=context
    )
    service, _, llm_client, _ = make_service(metadata=metadata)

    await service.draft(STORY_ID, SCENE_ID)

    llm_client.invoke.assert_awaited_once_with(context[-50:], "One.")


@pytest.mark.asyncio
async def test_draft_records_scene_summary_usage():
    service, _, _, usage_repo = make_service()

    await service.draft(STORY_ID, SCENE_ID)

    usage_repo.append.assert_awaited_once()
    story_id, usage = usage_repo.append.await_args.args
    assert story_id == STORY_ID
    assert (usage.operation, usage.scene_id, usage.message_id, usage.character_id) == (
        "scene_summary",
        SCENE_ID,
        None,
        None,
    )


@pytest.mark.asyncio
async def test_draft_raises_when_scene_finished():
    metadata = make_scene_metadata(
        story_id=STORY_ID, scene_id=SCENE_ID, finished=True
    )
    service, _, llm_client, usage_repo = make_service(metadata=metadata)

    with pytest.raises(SceneFinishedError):
        await service.draft(STORY_ID, SCENE_ID)

    llm_client.invoke.assert_not_awaited()
    usage_repo.append.assert_not_awaited()


@pytest.mark.asyncio
async def test_draft_raises_when_story_not_found():
    service, story_repo, llm_client, _ = make_service()
    story_repo.get_story.side_effect = NotFoundError("Story not found")

    with pytest.raises(NotFoundError):
        await service.draft(STORY_ID, SCENE_ID)

    llm_client.invoke.assert_not_awaited()


@pytest.mark.asyncio
async def test_draft_llm_error_propagates_and_records_nothing():
    service, _, _, usage_repo = make_service(llm_side_effect=LLMError("boom"))

    with pytest.raises(LLMError):
        await service.draft(STORY_ID, SCENE_ID)

    usage_repo.append.assert_not_awaited()
