from __future__ import annotations

import logging

from app.exceptions import SceneFinishedError
from app.models.domain import Message
from app.repositories.scene_repository import SceneRepository

logger = logging.getLogger(__name__)


class SceneMessageService:
    def __init__(self, scene_repo: SceneRepository) -> None:
        self._scene_repo = scene_repo

    async def edit_message(
        self, story_id: str, scene_id: int, message_id: int, new_content: str
    ) -> Message:
        logger.info(f"Editing message story_id={story_id} scene_id={scene_id} message_id={message_id}")
        metadata = await self._scene_repo.get_metadata(story_id, scene_id)

        if metadata.finished:
            raise SceneFinishedError()

        return await self._scene_repo.update_message(
            story_id, scene_id, message_id, new_content
        )

    async def delete_message(
        self, story_id: str, scene_id: int, message_id: int
    ) -> None:
        logger.info(f"Deleting message story_id={story_id} scene_id={scene_id} message_id={message_id}")
        metadata = await self._scene_repo.get_metadata(story_id, scene_id)

        if metadata.finished:
            raise SceneFinishedError()

        await self._scene_repo.delete_message(story_id, scene_id, message_id)
