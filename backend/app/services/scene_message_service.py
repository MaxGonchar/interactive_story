from __future__ import annotations

from app.models.domain import Message
from app.repositories.scene_repository import SceneRepository


class SceneMessageService:
    def __init__(self, scene_repo: SceneRepository) -> None:
        self._scene_repo = scene_repo

    async def edit_message(
        self, story_id: str, scene_id: int, message_id: int, new_content: str
    ) -> Message:
        metadata = await self._scene_repo.get_metadata(story_id, scene_id)

        if metadata.finished:
            raise ValueError("scene_finished")

        return await self._scene_repo.update_message(
            story_id, scene_id, message_id, new_content
        )

    async def delete_message(
        self, story_id: str, scene_id: int, message_id: int
    ) -> None:
        metadata = await self._scene_repo.get_metadata(story_id, scene_id)

        if metadata.finished:
            raise ValueError("scene_finished")

        await self._scene_repo.delete_message(story_id, scene_id, message_id)
