from __future__ import annotations

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
            raise ValueError("scene_finished")

        characters, messages = (
            await self._character_repo.get_characters(
                story_id, metadata.characters_ids
            ),
            await self._scene_repo.get_messages(story_id, scene_id),
        )

        user_id = max((m.id for m in messages), default=0) + 1
        assistant_id = user_id + 1

        context = SceneContext(
            scene_description=metadata.scene_description,
            characters=characters,
            messages=messages,
        )

        reply = await self._llm_client.invoke(context, user_content)

        user_msg = Message(id=user_id, role="user", content=user_content)
        assistant_msg = Message(id=assistant_id, role="assistant", content=reply)

        await self._scene_repo.add_message(story_id, scene_id, user_msg)
        await self._scene_repo.add_message(story_id, scene_id, assistant_msg)

        return user_msg, assistant_msg
