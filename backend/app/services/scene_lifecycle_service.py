from __future__ import annotations

from app.exceptions import SceneFinishedError
from app.models.domain import SceneMetadata
from app.repositories.scene_repository import SceneRepository
from app.repositories.story_repository import StoryRepository


class SceneLifecycleService:
    def __init__(self, scene_repo: SceneRepository, story_repo: StoryRepository) -> None:
        self._scene_repo = scene_repo
        self._story_repo = story_repo

    async def finish_scene(
        self, story_id: str, scene_id: int, summary: list[str]
    ) -> SceneMetadata:
        metadata = await self._scene_repo.get_metadata(story_id, scene_id)

        if metadata.finished:
            raise SceneFinishedError()

        updated = metadata.model_copy(
            update={"finished": True, "scene_summary": summary}
        )

        await self._story_repo.update_scene_finished(story_id, scene_id, summary)
        await self._scene_repo.save_metadata(story_id, scene_id, updated)

        return updated
