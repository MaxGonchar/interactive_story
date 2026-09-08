from __future__ import annotations

import asyncio
import logging

from app.exceptions import (
    InvalidModelError,
    NoAssistantMessageError,
    NoUserMessageError,
    SceneFinishedError,
)
from app.llm.models import SceneContext
from app.llm.scene_llm_client import SceneLLMClientFactory
from app.models.domain import LLMData, Message, ModelMetadata, ModelRegistry
from app.repositories.character_repository import CharacterRepository
from app.repositories.scene_repository import SceneRepository
from app.services.model_registry_service import ModelRegistryService

logger = logging.getLogger(__name__)


class ScenePlayService:
    def __init__(
        self,
        scene_repo: SceneRepository,
        character_repo: CharacterRepository,
        llm_client_factory: SceneLLMClientFactory,
        model_registry_service: ModelRegistryService,
    ) -> None:
        self._scene_repo = scene_repo
        self._character_repo = character_repo
        self._llm_client_factory = llm_client_factory
        self._model_registry_service = model_registry_service

    async def play(
        self,
        story_id: str,
        scene_id: int,
        user_content: str,
        model_id: str | None = None,
    ) -> tuple[Message, Message]:
        logger.info(f"Playing scene story_id={story_id} scene_id={scene_id}")
        metadata = await self._scene_repo.get_metadata(story_id, scene_id)

        if metadata.finished:
            raise SceneFinishedError()

        characters, messages = await asyncio.gather(
            self._character_repo.get_characters(story_id, metadata.character_ids),
            self._scene_repo.get_messages(story_id, scene_id),
        )
        registry = await self._model_registry_service.get_registry()
        selected_model = self._resolve_model(registry, messages, model_id)

        user_id = max((m.id for m in messages), default=0) + 1
        assistant_id = user_id + 1

        context_data = metadata.context or []

        user_character = None
        if metadata.user_character_id is not None:
            user_character = await self._character_repo.get_character(
                story_id, metadata.user_character_id
            )

        context = SceneContext(
            scene_description=metadata.scene_description,
            characters=characters,
            user_character=user_character,
            messages=messages,
            context_data=context_data,
        )

        llm_client = self._llm_client_factory(selected_model.provider_model_id)
        reply = await llm_client.invoke(context, user_content)

        user_msg = Message(id=user_id, role="user", content=user_content)
        assistant_msg = Message(
            id=assistant_id,
            role="assistant",
            content=reply,
            llm_data=LLMData(model_id=selected_model.id),
        )

        await self._scene_repo.add_messages(story_id, scene_id, [user_msg, assistant_msg])

        return user_msg, assistant_msg

    async def regenerate(self, story_id: str, scene_id: int) -> Message:
        logger.info(f"Regenerating last assistant message story_id={story_id} scene_id={scene_id}")
        metadata = await self._scene_repo.get_metadata(story_id, scene_id)
        if metadata.finished:
            raise SceneFinishedError()

        messages = await self._scene_repo.get_messages(story_id, scene_id)
        if not messages or messages[-1].role != "assistant":
            raise NoAssistantMessageError()

        # Exclude the last assistant message
        context_messages = messages[:-1]

        # Determine user content for LLM
        if context_messages and context_messages[-1].role == "user":
            user_content = context_messages[-1].content
        else:
            raise NoUserMessageError()

        registry = await self._model_registry_service.get_registry()
        selected_model = self._resolve_model(registry, messages)

        context_data = metadata.context or []

        characters = await self._character_repo.get_characters(story_id, metadata.character_ids)
        user_character = None
        if metadata.user_character_id is not None:
            user_character = await self._character_repo.get_character(
                story_id, metadata.user_character_id
            )
        context = SceneContext(
            scene_description=metadata.scene_description,
            characters=characters,
            user_character=user_character,
            messages=context_messages,
            context_data=context_data,
        )

        llm_client = self._llm_client_factory(selected_model.provider_model_id)
        reply = await llm_client.invoke(context, user_content)

        last_assistant_msg = messages[-1]
        updated_msg = await self._scene_repo.update_message(
            story_id,
            scene_id,
            last_assistant_msg.id,
            reply,
            llm_data=LLMData(model_id=selected_model.id),
        )
        return updated_msg

    @staticmethod
    def _resolve_model(
        registry: ModelRegistry,
        messages: list[Message],
        requested_model_id: str | None = None,
    ) -> ModelMetadata:
        if requested_model_id is not None:
            try:
                return registry.models[requested_model_id]
            except KeyError as exc:
                raise InvalidModelError() from exc

        default_model = registry.models[registry.default_model_id]
        for message in reversed(messages):
            if message.role == "assistant" and message.llm_data is not None:
                return registry.models.get(message.llm_data.model_id, default_model)

        return default_model
