from __future__ import annotations

import asyncio
import logging

from app.exceptions import SceneFinishedError
from app.llm.summarize_llm_client import SummarizeLLMClient
from app.repositories.character_driven_scene_repository import (
    CharacterDrivenSceneRepository,
)
from app.repositories.llm_usage_repository import LLMUsageRepository
from app.repositories.scene_repository import SceneRepository
from app.repositories.story_repository import StoryRepository
from app.services.llm_usage_service import record_usage

_MAX_CONTEXT_ITEMS = 50

logger = logging.getLogger(__name__)


class CharacterDrivenSceneSummaryService:
    def __init__(
        self,
        story_repo: StoryRepository,
        scene_repo: SceneRepository,
        character_driven_scene_repo: CharacterDrivenSceneRepository,
        llm_client: SummarizeLLMClient,
        usage_repository: LLMUsageRepository,
    ) -> None:
        self._story_repo = story_repo
        self._scene_repo = scene_repo
        self._character_driven_scene_repo = character_driven_scene_repo
        self._llm_client = llm_client
        self._usage_repository = usage_repository

    async def draft(self, story_id: str, scene_id: int) -> list[str]:
        logger.info(f"Drafting scene summary story_id={story_id} scene_id={scene_id}")
        await self._story_repo.get_story(story_id)
        metadata, messages = await asyncio.gather(
            self._scene_repo.get_metadata(story_id, scene_id),
            self._character_driven_scene_repo.get_messages(story_id, scene_id),
        )
        if metadata.finished:
            raise SceneFinishedError()

        previous_summary = (metadata.context or [])[-_MAX_CONTEXT_ITEMS:]
        scene_content = "\n\n".join(message.narration for message in messages)

        completion = await self._llm_client.invoke(previous_summary, scene_content)
        await record_usage(
            self._usage_repository,
            story_id,
            "scene_summary",
            completion,
            scene_id=scene_id,
        )
        return completion.result
