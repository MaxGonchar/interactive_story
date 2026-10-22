from __future__ import annotations

import logging
from collections.abc import Callable
from dataclasses import dataclass

from app.exceptions import (
    CharacterNotInSceneError,
    ItemNotReplaceableError,
    LLMError,
    NotFoundError,
    NotLastItemError,
    SceneFinishedError,
)
from app.llm.character_agent_client import CharacterAgentClient
from app.llm.models import LLMCompletion
from app.llm.narrator_client import NarratorClient
from app.models.api import (
    CharacterDrivenCharacterTurnRequest,
    CharacterDrivenPlayerTurnRequest,
    CharacterDrivenTurnRequest,
)
from app.models.domain import (
    CharacterCard,
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
CharacterAgentClientFactory = Callable[[str], CharacterAgentClient]

DEFAULT_PLAYER_NAME = "Player"


@dataclass(frozen=True)
class GeneratedItem:
    input: CharacterDrivenInput
    narration: str
    llm_data: CharacterDrivenLLMData
    narration_completion: LLMCompletion
    character_action_completion: LLMCompletion | None = None


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
        character_agent_client_factory: CharacterAgentClientFactory,
    ) -> None:
        self._story_repo = story_repo
        self._scene_repo = scene_repo
        self._character_driven_scene_repo = character_driven_scene_repo
        self._character_repo = character_repo
        self._model_registry_service = model_registry_service
        self._usage_repository = usage_repository
        self._narrator_client_factory = narrator_client_factory
        self._character_agent_client_factory = character_agent_client_factory

    async def submit_turn(
        self, story_id: str, scene_id: int, request: CharacterDrivenTurnRequest
    ) -> tuple[SceneMetadata, CharacterDrivenMessage]:
        metadata = await self._get_active_scene(story_id, scene_id)
        history = await self._character_driven_scene_repo.get_messages(
            story_id, scene_id
        )
        generated, character_model, narrator_model = await self._generate(
            story_id, metadata, history, request
        )

        message = await self._character_driven_scene_repo.append_message(
            story_id,
            scene_id,
            generated.input,
            generated.narration,
            generated.llm_data,
        )
        await self._record_generated_usage(
            story_id, scene_id, message.id, generated, character_model, narrator_model
        )
        return metadata, message

    async def replace_turn(
        self,
        story_id: str,
        scene_id: int,
        item_id: int,
        request: CharacterDrivenTurnRequest,
    ) -> tuple[SceneMetadata, CharacterDrivenMessage]:
        metadata = await self._get_active_scene(story_id, scene_id)
        messages = await self._character_driven_scene_repo.get_messages(
            story_id, scene_id
        )
        item_index = next(
            (index for index, message in enumerate(messages) if message.id == item_id),
            None,
        )
        if item_index is None:
            raise NotFoundError(f"Item '{item_id}' not found")
        if item_index != len(messages) - 1:
            raise NotLastItemError()
        if messages[item_index].input is None:
            raise ItemNotReplaceableError()

        generated, character_model, narrator_model = await self._generate(
            story_id, metadata, messages[:item_index], request
        )

        message = await self._character_driven_scene_repo.replace_message(
            story_id,
            scene_id,
            item_id,
            generated.input,
            generated.narration,
            generated.llm_data,
        )
        await self._record_generated_usage(
            story_id, scene_id, message.id, generated, character_model, narrator_model
        )
        return metadata, message

    async def _get_active_scene(self, story_id: str, scene_id: int) -> SceneMetadata:
        await self._story_repo.get_story(story_id)
        metadata = await self._scene_repo.get_metadata(story_id, scene_id)
        if metadata.finished:
            raise SceneFinishedError()
        return metadata

    async def _generate(
        self,
        story_id: str,
        metadata: SceneMetadata,
        history: list[CharacterDrivenMessage],
        request: CharacterDrivenTurnRequest,
    ) -> tuple[GeneratedItem, ModelMetadata, ModelMetadata]:
        await self._model_registry_service.validate_model_ids(
            request.character_model_id, request.narrator_model_id
        )
        registry = await self._model_registry_service.get_registry()
        character_model = registry.models[request.character_model_id]
        narrator_model = registry.models[request.narrator_model_id]

        if isinstance(request, CharacterDrivenPlayerTurnRequest):
            player_name = await self._get_player_name(story_id, metadata)
            generated = await self.generate_player_turn(
                metadata, history, request, narrator_model, player_name
            )
        else:
            character_id = request.actor.character_id
            if character_id not in metadata.character_ids:
                raise CharacterNotInSceneError()
            character = await self._character_repo.get_character(
                story_id, character_id
            )
            generated = await self.generate_character_turn(
                metadata,
                history,
                request,
                character,
                character_model,
                narrator_model,
            )
        return generated, character_model, narrator_model

    async def _record_generated_usage(
        self,
        story_id: str,
        scene_id: int,
        message_id: int,
        generated: GeneratedItem,
        character_model: ModelMetadata,
        narrator_model: ModelMetadata,
    ) -> None:
        if generated.character_action_completion is not None:
            await record_usage(
                self._usage_repository,
                story_id,
                "character_action",
                with_registry_model_id(
                    generated.character_action_completion, character_model.id
                ),
                scene_id=scene_id,
                message_id=message_id,
                character_id=generated.input.author,
            )
        await record_usage(
            self._usage_repository,
            story_id,
            "narration",
            with_registry_model_id(generated.narration_completion, narrator_model.id),
            scene_id=scene_id,
            message_id=message_id,
        )

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

    async def generate_character_turn(
        self,
        metadata: SceneMetadata,
        history: list[CharacterDrivenMessage],
        request: CharacterDrivenCharacterTurnRequest,
        character: CharacterCard,
        character_model: ModelMetadata,
        narrator_model: ModelMetadata,
    ) -> GeneratedItem:
        character_agent = self._character_agent_client_factory(
            character_model.provider_model_id
        )
        try:
            character_completion = await character_agent.invoke(
                character=character,
                scene_narrations=[message.narration for message in history],
                player_guidance=request.guidance,
            )
        except LLMError:
            logger.error(
                "Turn generation failed story_id=%s scene_id=%s stage=character_action",
                metadata.story_id,
                metadata.id,
            )
            raise

        narrator = self._narrator_client_factory(narrator_model.provider_model_id)
        try:
            narration_completion = await narrator.invoke(
                story_context=metadata.context or [],
                general_scene_guide=metadata.scene_description.general_scene_guide,
                writing_style=metadata.scene_description.writing_style,
                scene_narrations=[message.narration for message in history],
                actor_name=character.name,
                current_turn=character_completion.content,
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
                author=character.id,
                action=character_completion.content,
                guidance=request.guidance,
            ),
            narration=narration_completion.content,
            llm_data=CharacterDrivenLLMData(
                character_model_id=request.character_model_id,
                narrator_model_id=request.narrator_model_id,
            ),
            narration_completion=narration_completion,
            character_action_completion=character_completion,
        )

    async def _get_player_name(self, story_id: str, metadata: SceneMetadata) -> str:
        if metadata.user_character_id is None:
            return DEFAULT_PLAYER_NAME
        character = await self._character_repo.get_character(
            story_id, metadata.user_character_id
        )
        return character.name
