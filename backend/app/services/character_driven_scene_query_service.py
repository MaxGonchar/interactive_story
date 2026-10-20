from __future__ import annotations

import asyncio

from app.models.domain import CharacterDrivenMessage, SceneMetadata
from app.repositories.character_driven_scene_repository import (
    CharacterDrivenSceneRepository,
)
from app.repositories.scene_repository import SceneRepository
from app.repositories.story_repository import StoryRepository


class CharacterDrivenSceneQueryService:
    def __init__(
        self,
        story_repo: StoryRepository,
        scene_repo: SceneRepository,
        character_driven_scene_repo: CharacterDrivenSceneRepository,
    ) -> None:
        self._story_repo = story_repo
        self._scene_repo = scene_repo
        self._character_driven_scene_repo = character_driven_scene_repo

    async def get_scene(
        self, story_id: str, scene_id: int
    ) -> tuple[SceneMetadata, list[CharacterDrivenMessage]]:
        await self._story_repo.get_story(story_id)
        metadata, messages = await asyncio.gather(
            self._scene_repo.get_metadata(story_id, scene_id),
            self._character_driven_scene_repo.get_messages(story_id, scene_id),
        )
        return metadata, messages