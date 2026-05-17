from __future__ import annotations

import asyncio

from app.models.domain import Message, SceneMetadata
from app.repositories.scene_repository import SceneRepository
from app.repositories.story_repository import StoryRepository


class SceneQueryService:
    def __init__(self, story_repo: StoryRepository, scene_repo: SceneRepository) -> None:
        self._story_repo = story_repo
        self._scene_repo = scene_repo

    async def get_scene(
        self, story_id: str, scene_id: int
    ) -> tuple[SceneMetadata, list[Message]]:
        await self._story_repo.get_story(story_id)
        metadata, messages = await asyncio.gather(
            self._scene_repo.get_metadata(story_id, scene_id),
            self._scene_repo.get_messages(story_id, scene_id),
        )
        return metadata, messages
