from __future__ import annotations

from uuid import UUID

from app.models.domain import LLMUsage, TokenUsage
from app.models.storage import LLMUsageDocumentYaml, LLMUsageYaml
from app.utils import file_paths, yaml_storage
from app.utils.atomic_write import atomic_write


class LLMUsageRepository:
    async def get_calls(self, story_id: str) -> list[LLMUsage]:
        try:
            data = await yaml_storage.read_yaml(file_paths.llm_usage_file(story_id))
        except FileNotFoundError:
            return []

        document = LLMUsageDocumentYaml(**data)
        return [self._to_domain(call) for call in document.calls]

    async def append(self, story_id: str, usage: LLMUsage) -> None:
        calls = await self.get_calls(story_id)
        calls.append(usage)
        data = {"calls": [self._to_storage(call).model_dump(mode="json") for call in calls]}
        await atomic_write(
            file_paths.llm_usage_file(story_id),
            yaml_storage.dump_yaml(data),
        )

    @staticmethod
    def _to_domain(raw: LLMUsageYaml) -> LLMUsage:
        return LLMUsage(
            id=raw.id,
            operation=raw.operation,
            model_id=raw.model_id,
            provider_model_id=raw.provider_model_id,
            provider_created=raw.provider_created,
            duration_ms=raw.duration_ms,
            usage=TokenUsage(
                prompt_tokens=raw.usage.prompt_tokens,
                completion_tokens=raw.usage.completion_tokens,
                total_tokens=raw.usage.total_tokens,
            ),
            cost_usd=raw.cost_usd,
            scene_id=raw.scene_id,
            message_id=raw.message_id,
            step_id=raw.step_id,
        )

    @staticmethod
    def _to_storage(usage: LLMUsage) -> LLMUsageYaml:
        return LLMUsageYaml(
            id=UUID(str(usage.id)),
            operation=usage.operation,
            model_id=usage.model_id,
            provider_model_id=usage.provider_model_id,
            provider_created=usage.provider_created,
            duration_ms=usage.duration_ms,
            usage={
                "prompt_tokens": usage.usage.prompt_tokens,
                "completion_tokens": usage.usage.completion_tokens,
                "total_tokens": usage.usage.total_tokens,
            },
            cost_usd=usage.cost_usd,
            scene_id=usage.scene_id,
            message_id=usage.message_id,
            step_id=usage.step_id,
        )