from __future__ import annotations

import asyncio

from app.exceptions import NoAssistantMessageError, NoUserMessageError, SceneFinishedError
from app.llm.models import SceneContext
from app.llm.scene_llm_client import SceneLLMClient
from app.models.domain import Message
from app.repositories.character_repository import CharacterRepository
from app.repositories.scene_repository import SceneRepository


class ScenePlayService:
    def __init__(
        self,
        scene_repo: SceneRepository,
        character_repo: CharacterRepository,
        llm_client: SceneLLMClient,
    ) -> None:
        self._scene_repo = scene_repo
        self._character_repo = character_repo
        self._llm_client = llm_client

    async def play(
        self, story_id: str, scene_id: int, user_content: str
    ) -> tuple[Message, Message]:
        metadata = await self._scene_repo.get_metadata(story_id, scene_id)

        if metadata.finished:
            raise SceneFinishedError()

        characters, messages = await asyncio.gather(
            self._character_repo.get_characters(story_id, metadata.character_ids),
            self._scene_repo.get_messages(story_id, scene_id),
        )

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

        reply = await self._llm_client.invoke(context, user_content)

        user_msg = Message(id=user_id, role="user", content=user_content)
        assistant_msg = Message(id=assistant_id, role="assistant", content=reply)

        await self._scene_repo.add_messages(story_id, scene_id, [user_msg, assistant_msg])

        return user_msg, assistant_msg

    async def regenerate(self, story_id: str, scene_id: int) -> Message:
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

        reply = await self._llm_client.invoke(context, user_content)

        last_assistant_msg = messages[-1]
        updated_msg = await self._scene_repo.update_message(
            story_id, scene_id, last_assistant_msg.id, reply
        )
        return updated_msg
