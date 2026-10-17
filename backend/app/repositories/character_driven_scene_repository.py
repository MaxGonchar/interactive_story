from __future__ import annotations

from app.exceptions import InvalidMessageAuthorError, NotFoundError
from app.models.domain import (
    CharacterDrivenInput,
    CharacterDrivenLLMData,
    CharacterDrivenMessage,
    SceneMetadata,
)
from app.models.storage import CharacterDrivenMessagesYaml
from app.repositories.scene_repository import SceneRepository
from app.utils import file_paths, yaml_storage
from app.utils.atomic_write import atomic_write


class CharacterDrivenSceneRepository:
    def __init__(self, scene_repo: SceneRepository | None = None) -> None:
        self._scene_repo = scene_repo or SceneRepository()

    async def create_scene(
        self,
        story_id: str,
        scene_id: int,
        metadata: SceneMetadata,
        opening: CharacterDrivenMessage,
    ) -> None:
        await self._validate_characters_exist(story_id, metadata)
        await self._scene_repo.save_metadata(story_id, scene_id, metadata)
        await self._save_messages(story_id, scene_id, [opening])

    async def get_messages(
        self, story_id: str, scene_id: int
    ) -> list[CharacterDrivenMessage]:
        try:
            data = await yaml_storage.read_yaml(
                file_paths.scene_messages_file(story_id, scene_id)
            )
        except FileNotFoundError:
            return []

        parsed = CharacterDrivenMessagesYaml(**data)
        return sorted(
            (CharacterDrivenMessage(**m.model_dump()) for m in parsed.messages),
            key=lambda m: m.id,
        )

    async def append_message(
        self,
        story_id: str,
        scene_id: int,
        input: CharacterDrivenInput | None,
        narration: str,
        llm_data: CharacterDrivenLLMData,
    ) -> CharacterDrivenMessage:
        await self._validate_author(story_id, scene_id, input)
        messages = await self.get_messages(story_id, scene_id)
        new_id = max((m.id for m in messages), default=0) + 1
        message = CharacterDrivenMessage(
            id=new_id, input=input, narration=narration, llm_data=llm_data
        )
        await self._save_messages(story_id, scene_id, [*messages, message])
        return message

    async def update_narration(
        self, story_id: str, scene_id: int, message_id: int, narration: str
    ) -> CharacterDrivenMessage:
        messages = await self.get_messages(story_id, scene_id)
        index = self._index_of(messages, message_id)
        updated = messages[index].model_copy(update={"narration": narration})
        messages[index] = updated
        await self._save_messages(story_id, scene_id, messages)
        return updated

    async def replace_message(
        self,
        story_id: str,
        scene_id: int,
        message_id: int,
        input: CharacterDrivenInput | None,
        narration: str,
        llm_data: CharacterDrivenLLMData,
    ) -> CharacterDrivenMessage:
        messages = await self.get_messages(story_id, scene_id)
        index = self._index_of(messages, message_id)
        await self._validate_author(story_id, scene_id, input)
        replaced = CharacterDrivenMessage(
            id=message_id, input=input, narration=narration, llm_data=llm_data
        )
        messages[index] = replaced
        await self._save_messages(story_id, scene_id, messages)
        return replaced

    async def delete_last_message(self, story_id: str, scene_id: int) -> None:
        messages = await self.get_messages(story_id, scene_id)
        if not messages:
            raise NotFoundError("Scene has no messages")

        await self._save_messages(story_id, scene_id, messages[:-1])

    @staticmethod
    def _index_of(messages: list[CharacterDrivenMessage], message_id: int) -> int:
        for index, message in enumerate(messages):
            if message.id == message_id:
                return index
        raise NotFoundError(f"Message '{message_id}' not found")

    async def _validate_author(
        self, story_id: str, scene_id: int, input: CharacterDrivenInput | None
    ) -> None:
        if input is None:
            return

        metadata = await self._scene_repo.get_metadata(story_id, scene_id)
        author = input.author
        if author is None:
            if metadata.user_character_id is not None:
                raise InvalidMessageAuthorError(
                    "Author is required when the scene has a player character"
                )
            return

        if author != metadata.user_character_id and author not in metadata.character_ids:
            raise InvalidMessageAuthorError(
                f"Author '{author}' is not a participant of scene '{scene_id}'"
            )

    async def _validate_characters_exist(
        self, story_id: str, metadata: SceneMetadata
    ) -> None:
        character_ids = list(metadata.character_ids)
        if metadata.user_character_id is not None:
            character_ids.append(metadata.user_character_id)

        for character_id in character_ids:
            try:
                await yaml_storage.read_yaml(
                    file_paths.character_file(story_id, character_id)
                )
            except FileNotFoundError:
                raise NotFoundError(f"Character '{character_id}' not found")

    async def _save_messages(
        self, story_id: str, scene_id: int, messages: list[CharacterDrivenMessage]
    ) -> None:
        data = {"messages": [m.model_dump() for m in messages]}
        await atomic_write(
            file_paths.scene_messages_file(story_id, scene_id),
            yaml_storage.dump_yaml(data),
        )
