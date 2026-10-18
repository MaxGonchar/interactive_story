from __future__ import annotations

import logging
from uuid import uuid4

from app.llm.models import LLMCompletion
from app.models.domain import LLMUsage, LLMUsageOperation
from app.repositories.llm_usage_repository import LLMUsageRepository

logger = logging.getLogger(__name__)


def with_registry_model_id(completion: LLMCompletion, model_id: str) -> LLMCompletion:
    return completion.model_copy(update={"model_id": model_id})


async def record_usage(
    repository: LLMUsageRepository,
    story_id: str,
    operation: LLMUsageOperation,
    completion: LLMCompletion,
    *,
    scene_id: int | None = None,
    message_id: int | None = None,
    step_id: int | None = None,
    character_id: str | None = None,
) -> None:
    try:
        usage = LLMUsage(
            id=uuid4(),
            operation=operation,
            model_id=completion.model_id,
            provider_model_id=completion.provider_model_id,
            provider_created=completion.provider_created,
            duration_ms=completion.duration_ms,
            usage=completion.usage,
            cost_usd=completion.cost_usd,
            scene_id=scene_id,
            message_id=message_id,
            step_id=step_id,
            character_id=character_id,
        )
        await repository.append(story_id, usage)
    except Exception:
        logger.warning(
            "Failed to persist LLM usage",
            extra={
                "story_id": story_id,
                "operation": operation,
                "scene_id": scene_id,
                "message_id": message_id,
                "step_id": step_id,
                "character_id": character_id,
            },
            exc_info=True,
        )