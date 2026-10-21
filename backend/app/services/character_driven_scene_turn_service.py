from __future__ import annotations

import logging
from collections.abc import Callable
from dataclasses import dataclass

from app.exceptions import LLMError, SceneFinishedError, TurnActorNotSupportedError
from app.llm.models import LLMCompletion
from app.llm.narrator_client import NarratorClient
from app.models.api import CharacterDrivenPlayerTurnRequest, CharacterDrivenTurnRequest
from app.models.domain import (
    CharacterDrivenInput,
    CharacterDrivenLLMData,
    CharacterDrivenMessage,
    ModelMetadata,
    SceneMetadata,
)
from app.repositories.character_driven_scene_repository import (
    CharacterDrivenSceneRepository,
)
from app.repositories.character_repository import CharacterRepository
from app.repositories.llm_usage_repository import LLMUsageRepository
from app.repositories.scene_repository import SceneRepository
from app.repositories.story_repository import StoryRepository
from app.services.llm_usage_service import record_usage, with_registry_model_id
from app.services.model_registry_service import ModelRegistryService

logger = logging.getLogger(__name__)

NarratorClientFactory = Callable[[str], NarratorClient]

DEFAULT_PLAYER_NAME = "Player"


@dataclass(frozen=True)
class GeneratedItem:
    input: CharacterDrivenInput
    narration: str
    llm_data: CharacterDrivenLLMData
    narration_completion: LLMCompletion


class CharacterDrivenSceneTurnService:
    def __init__(
        self,
        story_repo: StoryRepository,
        scene_repo: SceneRepository,
        character_driven_scene_repo: CharacterDrivenSceneRepository,
        character_repo: CharacterRepository,
        model_registry_service: ModelRegistryService,
        usage_repository: LLMUsageRepository,
        narrator_client_factory: NarratorClientFactory,
    ) -> None:
        self._story_repo = story_repo
        self._scene_repo = scene_repo
        self._character_driven_scene_repo = character_driven_scene_repo
        self._character_repo = character_repo
        self._model_registry_service = model_registry_service
        self._usage_repository = usage_repository
        self._narrator_client_factory = narrator_client_factory

    async def submit_turn(
        self, story_id: str, scene_id: int, request: CharacterDrivenTurnRequest
    ) -> tuple[SceneMetadata, CharacterDrivenMessage]:
        await self._story_repo.get_story(story_id)
        metadata = await self._scene_repo.get_metadata(story_id, scene_id)
        if metadata.finished:
            raise SceneFinishedError()

        if not isinstance(request, CharacterDrivenPlayerTurnRequest):
            raise TurnActorNotSupportedError()

        await self._model_registry_service.validate_model_ids(
            request.character_model_id, request.narrator_model_id
        )
        registry = await self._model_registry_service.get_registry()
        narrator_model = registry.models[request.narrator_model_id]

        history = await self._character_driven_scene_repo.get_messages(
            story_id, scene_id
        )
        player_name = await self._get_player_name(story_id, metadata)

        generated = await self.generate_player_turn(
            metadata, history, request, narrator_model, player_name
        )

        message = await self._character_driven_scene_repo.append_message(
            story_id,
            scene_id,
            generated.input,
            generated.narration,
            generated.llm_data,
        )
        await record_usage(
            self._usage_repository,
            story_id,
            "narration",
            with_registry_model_id(generated.narration_completion, narrator_model.id),
            scene_id=scene_id,
            message_id=message.id,
        )
        return metadata, message

    async def generate_player_turn(
        self,
        metadata: SceneMetadata,
        history: list[CharacterDrivenMessage],
        request: CharacterDrivenPlayerTurnRequest,
        narrator_model: ModelMetadata,
        player_name: str,
    ) -> GeneratedItem:
        narrator = self._narrator_client_factory(narrator_model.provider_model_id)
        try:
            completion = await narrator.invoke(
                story_context=metadata.context or [],
                general_scene_guide=metadata.scene_description.general_scene_guide,
                writing_style=metadata.scene_description.writing_style,
                scene_narrations=[message.narration for message in history],
                actor_name=player_name,
                current_turn=request.action,
            )
        except LLMError:
            logger.error(
                "Turn generation failed story_id=%s scene_id=%s stage=narration",
                metadata.story_id,
                metadata.id,
            )
            raise

        return GeneratedItem(
            input=CharacterDrivenInput(
                author=metadata.user_character_id, action=request.action
            ),
            narration=completion.content,
            llm_data=CharacterDrivenLLMData(
                character_model_id=None,
                narrator_model_id=request.narrator_model_id,
            ),
            narration_completion=completion,
        )

    async def _get_player_name(self, story_id: str, metadata: SceneMetadata) -> str:
        if metadata.user_character_id is None:
            return DEFAULT_PLAYER_NAME
        character = await self._character_repo.get_character(
            story_id, metadata.user_character_id
        )
        return character.name
