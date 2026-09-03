from __future__ import annotations

import logging

from app.exceptions import SceneFinishedError
from app.models.domain import SceneMetadata
from app.repositories.scene_repository import SceneRepository

logger = logging.getLogger(__name__)


class SceneLifecycleService:
    def __init__(self, scene_repo: SceneRepository) -> None:
        self._scene_repo = scene_repo

    async def finish_scene(
        self, story_id: str, scene_id: int, summary: list[str]
    ) -> SceneMetadata:
        logger.info(f"Finishing scene story_id={story_id} scene_id={scene_id}")
        metadata = await self._scene_repo.get_metadata(story_id, scene_id)

        if metadata.finished:
            raise SceneFinishedError()

        updated = metadata.model_copy(
            update={"finished": True, "scene_summary": summary}
        )

        await self._scene_repo.save_metadata(story_id, scene_id, updated)

        return updated
