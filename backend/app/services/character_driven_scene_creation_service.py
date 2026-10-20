from __future__ import annotations

import logging

from app.exceptions import ActiveSceneExistsError
from app.models.domain import (
    CharacterDrivenLLMData,
    CharacterDrivenMessage,
    SceneDescription,
    SceneMetadata,
    SceneRef,
)
from app.repositories.character_driven_scene_repository import (
    CharacterDrivenSceneRepository,
)
from app.repositories.story_repository import StoryRepository
from app.services.model_registry_service import ModelRegistryService

logger = logging.getLogger(__name__)


class CharacterDrivenSceneCreationService:
    def __init__(
        self,
        story_repo: StoryRepository,
        scene_repo: CharacterDrivenSceneRepository,
        model_registry_service: ModelRegistryService,
    ) -> None:
        self._story_repo = story_repo
        self._scene_repo = scene_repo
        self._model_registry_service = model_registry_service

    async def create(
        self,
        story_id: str,
        user_character_id: str | None,
        character_ids: list[str],
        context: list[str],
        general_scene_guide: str,
        writing_style: str,
        first_message: str,
        character_model_id: str,
        narrator_model_id: str,
    ) -> SceneRef:
        story = await self._story_repo.get_story(story_id)
        await self._model_registry_service.validate_model_ids(
            character_model_id, narrator_model_id
        )

        if any(not s.finished for s in story.scenes):
            raise ActiveSceneExistsError()

        next_id = max((s.id for s in story.scenes), default=0) + 1
        logger.info(
            f"Creating character-driven scene story_id={story_id} scene_id={next_id}"
        )

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
        opening = CharacterDrivenMessage(
            id=1,
            narration=first_message,
            llm_data=CharacterDrivenLLMData(
                character_model_id=character_model_id,
                narrator_model_id=narrator_model_id,
            ),
        )

        await self._scene_repo.create_scene(story_id, next_id, metadata, opening)

        return SceneRef(id=next_id, finished=False)
