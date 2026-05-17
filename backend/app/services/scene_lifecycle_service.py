from __future__ import annotations

from app.models.domain import SceneMetadata
from app.repositories.scene_repository import SceneRepository


class SceneLifecycleService:
    def __init__(self, scene_repo: SceneRepository) -> None:
        self._scene_repo = scene_repo

    async def finish_scene(
        self, story_id: str, scene_id: int, summary: str
    ) -> SceneMetadata:
        metadata = await self._scene_repo.get_metadata(story_id, scene_id)

        if metadata.finished:
            raise ValueError("scene_finished")

        updated = metadata.model_copy(
            update={"finished": True, "scene_summary": [summary]}
        )

        await self._scene_repo.save_metadata(story_id, scene_id, updated)

        return updated
