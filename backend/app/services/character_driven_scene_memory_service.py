from __future__ import annotations

import asyncio
import logging

from app.exceptions import CharacterNotParticipantError, SceneFinishedError
from app.llm.memory_agent_client import MemoryAgentClient
from app.repositories.character_driven_scene_repository import (
    CharacterDrivenSceneRepository,
)
from app.repositories.character_repository import CharacterRepository
from app.repositories.llm_usage_repository import LLMUsageRepository
from app.repositories.scene_repository import SceneRepository
from app.repositories.story_repository import StoryRepository
from app.services.llm_usage_service import record_usage

logger = logging.getLogger(__name__)


class CharacterDrivenSceneMemoryService:
    def __init__(
        self,
        story_repo: StoryRepository,
        scene_repo: SceneRepository,
        character_driven_scene_repo: CharacterDrivenSceneRepository,
        character_repo: CharacterRepository,
        llm_client: MemoryAgentClient,
        usage_repository: LLMUsageRepository,
    ) -> None:
        self._story_repo = story_repo
        self._scene_repo = scene_repo
        self._character_driven_scene_repo = character_driven_scene_repo
        self._character_repo = character_repo
        self._llm_client = llm_client
        self._usage_repository = usage_repository

    async def draft(
        self, story_id: str, scene_id: int, character_id: str
    ) -> list[str]:
        logger.info(
            f"Drafting character memory story_id={story_id} scene_id={scene_id} "
            f"character_id={character_id}"
        )
        await self._story_repo.get_story(story_id)
        metadata, messages = await asyncio.gather(
            self._scene_repo.get_metadata(story_id, scene_id),
            self._character_driven_scene_repo.get_messages(story_id, scene_id),
        )
        if metadata.finished:
            raise SceneFinishedError()

        participant_ids = list(metadata.character_ids)
        if metadata.user_character_id is not None:
            participant_ids.append(metadata.user_character_id)
        if character_id not in participant_ids:
            raise CharacterNotParticipantError()

        participants = await self._character_repo.get_characters(
            story_id, participant_ids
        )
        character = next(card for card in participants if card.id == character_id)
        character_names = {card.id: card.name for card in participants}

        completion = await self._llm_client.invoke(
            character, messages, character_names
        )
        await record_usage(
            self._usage_repository,
            story_id,
            "character_memory_update",
            completion,
            scene_id=scene_id,
            character_id=character_id,
        )
        return completion.result
