from __future__ import annotations

import logging

from app.exceptions import (
    InvalidCharacterMemoryUpdatesError,
    SceneFinishedError,
)
from app.models.domain import SceneMetadata
from app.repositories.character_repository import CharacterRepository
from app.repositories.scene_repository import SceneRepository

logger = logging.getLogger(__name__)


class CharacterDrivenSceneFinishService:
    def __init__(
        self,
        scene_repo: SceneRepository,
        character_repo: CharacterRepository,
    ) -> None:
        self._scene_repo = scene_repo
        self._character_repo = character_repo

    async def finish(
        self,
        story_id: str,
        scene_id: int,
        scene_summary: list[str],
        character_memory_updates: dict[str, list[str]],
    ) -> SceneMetadata:
        logger.info(
            "Finishing character-driven scene story_id=%s scene_id=%s",
            story_id,
            scene_id,
        )
        metadata = await self._scene_repo.get_metadata(story_id, scene_id)
        if metadata.finished:
            raise SceneFinishedError()

        participant_ids = list(metadata.character_ids)
        if metadata.user_character_id is not None:
            participant_ids.append(metadata.user_character_id)
        if set(character_memory_updates) != set(participant_ids):
            raise InvalidCharacterMemoryUpdatesError()

        characters = await self._character_repo.get_characters(
            story_id, participant_ids
        )
        memory_snapshots = {
            character.id: list(character.memory) for character in characters
        }
        updated_metadata = metadata.model_copy(
            update={"finished": True, "scene_summary": scene_summary}
        )

        try:
            for character_id in participant_ids:
                await self._character_repo.append_memory(
                    story_id,
                    character_id,
                    character_memory_updates[character_id],
                )
            await self._scene_repo.save_metadata(
                story_id, scene_id, updated_metadata
            )
        except Exception:
            for character_id, memory in memory_snapshots.items():
                await self._character_repo.set_memory(story_id, character_id, memory)
            raise

        return updated_metadata
