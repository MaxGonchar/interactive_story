from __future__ import annotations

from app.llm.models import SceneContext
from app.llm.scene_llm_client import SceneLLMClient
from app.models.domain import Message
from app.repositories.character_repository import CharacterRepository
from app.repositories.scene_repository import SceneRepository
from app.repositories.story_repository import StoryRepository


class ScenePlayService:
    def __init__(
        self,
        scene_repo: SceneRepository,
        character_repo: CharacterRepository,
        llm_client: SceneLLMClient,
        story_repo: StoryRepository,
    ) -> None:
        self._scene_repo = scene_repo
        self._character_repo = character_repo
        self._llm_client = llm_client
        self._story_repo = story_repo

    async def play(
        self, story_id: str, scene_id: int, user_content: str
    ) -> tuple[Message, Message]:
        metadata = await self._scene_repo.get_metadata(story_id, scene_id)

        if metadata.finished:
            raise ValueError("scene_finished")

        characters, messages = (
            await self._character_repo.get_characters(
                story_id, metadata.characters_ids
            ),
            await self._scene_repo.get_messages(story_id, scene_id),
        )

        user_id = max((m.id for m in messages), default=0) + 1
        assistant_id = user_id + 1

        # Fetch story meta and build context_data from finished scenes before current
        story_meta = await self._story_repo.get_story(story_id)
        current_index = next(
            (i for i, s in enumerate(story_meta.scenes) if s.id == scene_id), None
        )
        context_data = [
            line
            for i, s in enumerate(story_meta.scenes)
            if s.finished and (current_index is None or i < current_index) and s.summary
            for line in s.summary
        ]

        context = SceneContext(
            scene_description=metadata.scene_description,
            characters=characters,
            messages=messages,
            context_data=context_data,
        )

        reply = await self._llm_client.invoke(context, user_content)

        user_msg = Message(id=user_id, role="user", content=user_content)
        assistant_msg = Message(id=assistant_id, role="assistant", content=reply)

        await self._scene_repo.add_message(story_id, scene_id, user_msg)
        await self._scene_repo.add_message(story_id, scene_id, assistant_msg)

        return user_msg, assistant_msg

    async def regenerate(self, story_id: str, scene_id: int) -> Message:
        metadata = await self._scene_repo.get_metadata(story_id, scene_id)
        if metadata.finished:
            raise ValueError("scene_finished")

        messages = await self._scene_repo.get_messages(story_id, scene_id)
        if not messages or messages[-1].role != "assistant":
            raise ValueError("no_assistant_message")

        # Exclude the last assistant message
        context_messages = messages[:-1]

        # Determine user content for LLM
        if context_messages and context_messages[-1].role == "user":
            user_content = context_messages[-1].content
        else:
            raise ValueError("no_user_message")

        characters = await self._character_repo.get_characters(story_id, metadata.characters_ids)
        context = SceneContext(
            scene_description=metadata.scene_description,
            characters=characters,
            messages=context_messages,
        )

        reply = await self._llm_client.invoke(context, user_content)

        last_assistant_msg = messages[-1]
        updated_msg = await self._scene_repo.update_message(
            story_id, scene_id, last_assistant_msg.id, reply
        )
        return updated_msg
