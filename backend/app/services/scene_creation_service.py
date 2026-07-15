from __future__ import annotations

from app.exceptions import ActiveSceneExistsError
from app.models.domain import Message, SceneDescription, SceneMetadata, SceneRef
from app.repositories.scene_repository import SceneRepository
from app.repositories.story_repository import StoryRepository


class SceneCreationService:
    def __init__(self, story_repo: StoryRepository, scene_repo: SceneRepository) -> None:
        self._story_repo = story_repo
        self._scene_repo = scene_repo

    async def create(
        self,
        story_id: str,
        user_character_id: str,
        character_ids: list[str],
        context: list[str],
        general_scene_guide: str,
        writing_style: str,
        first_message: str,
    ) -> SceneRef:
        story = await self._story_repo.get_story(story_id)

        if any(not s.finished for s in story.scenes):
            raise ActiveSceneExistsError()

        next_id = max((s.id for s in story.scenes), default=0) + 1

        metadata = SceneMetadata(
            id=next_id,
            story_id=story_id,
            character_ids=character_ids,
            user_character_id=user_character_id,
            finished=False,
            scene_description=SceneDescription(
                general_scene_guide=general_scene_guide,
                writing_style=writing_style,
            ),
            context=context,
        )
        first_msg = Message(id=1, role="assistant", content=first_message)

        await self._scene_repo.create_scene(story_id, next_id, metadata, first_msg)

        return SceneRef(id=next_id, finished=False)
