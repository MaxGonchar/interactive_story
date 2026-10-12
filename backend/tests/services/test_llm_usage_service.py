from __future__ import annotations

from unittest.mock import AsyncMock

import pytest

from app.llm.models import LLMCompletion
from app.models.domain import TokenUsage
from app.services.llm_usage_service import record_usage


@pytest.mark.asyncio
async def test_record_usage_passes_character_id_to_repository():
    repository = AsyncMock()
    completion = LLMCompletion(
        content="The navigator warns the captain.",
        model_id="character-model",
        provider_model_id="provider-character-model",
        provider_created=1739928524,
        usage=TokenUsage(prompt_tokens=10, completion_tokens=20, total_tokens=30),
        duration_ms=1243,
    )

    await record_usage(
        repository,
        "story-1",
        "character_action",
        completion,
        scene_id=1,
        message_id=2,
        character_id="navigator",
    )

    repository.append.assert_awaited_once()
    story_id, usage = repository.append.call_args.args
    assert story_id == "story-1"
    assert usage.character_id == "navigator"