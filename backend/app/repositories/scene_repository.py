from __future__ import annotations

from app.exceptions import NarratorModeNotSupportedError, NotFoundError
from app.models.domain import Message, SceneDescription, SceneMetadata
from app.models.storage import MessagesYaml, SceneMetadataYaml, StoryYaml
from app.utils import file_paths, yaml_storage
from app.utils.atomic_write import atomic_write


class SceneRepository:
    async def get_metadata(self, story_id: str, scene_id: int) -> SceneMetadata:
        try:
            data = await yaml_storage.read_yaml(
                file_paths.scene_metadata_file(story_id, scene_id)
            )
        except FileNotFoundError:
            raise NotFoundError(f"Scene '{scene_id}' not found")

        raw = SceneMetadataYaml(**data)
        return SceneMetadata(
            id=scene_id,
            story_id=story_id,
            character_ids=raw.character_ids,
            user_character_id=raw.user_character_id,
            finished=raw.finished,
            scene_description=SceneDescription(
                general_scene_guide=raw.scene_description.general_scene_guide,
                writing_style=raw.scene_description.writing_style,
            ),
            scene_summary=raw.scene_summary,
            context=raw.context,
        )

    async def save_metadata(
        self, story_id: str, scene_id: int, metadata: SceneMetadata
    ) -> None:
        data = metadata.model_dump(exclude={"id", "story_id"})
        await atomic_write(
            file_paths.scene_metadata_file(story_id, scene_id),
            yaml_storage.dump_yaml(data),
        )

    async def get_messages(self, story_id: str, scene_id: int) -> list[Message]:
        try:
            data = await yaml_storage.read_yaml(
                file_paths.scene_messages_file(story_id, scene_id)
            )
        except FileNotFoundError:
            return []

        parsed = MessagesYaml(**data)
        return sorted(
            [Message(id=m.id, role=m.role, content=m.content) for m in parsed.messages],
            key=lambda m: m.id,
        )

    async def add_messages(
        self, story_id: str, scene_id: int, new_messages: list[Message]
    ) -> None:
        messages = await self.get_messages(story_id, scene_id)
        messages.extend(new_messages)
        await self._save_messages(story_id, scene_id, messages)

    async def update_message(
        self, story_id: str, scene_id: int, message_id: int, new_content: str
    ) -> Message:
        messages = await self.get_messages(story_id, scene_id)
        index = next((i for i, m in enumerate(messages) if m.id == message_id), None)
        if index is None:
            raise NotFoundError(f"Message '{message_id}' not found")

        updated = Message(id=messages[index].id, role=messages[index].role, content=new_content)
        messages[index] = updated
        await self._save_messages(story_id, scene_id, messages)
        return updated

    async def delete_message(
        self, story_id: str, scene_id: int, message_id: int
    ) -> None:
        messages = await self.get_messages(story_id, scene_id)
        if not any(m.id == message_id for m in messages):
            raise NotFoundError(f"Message '{message_id}' not found")

        await self._save_messages(
            story_id, scene_id, [m for m in messages if m.id != message_id]
        )

    async def create_scene(
        self, story_id: str, scene_id: int, metadata: SceneMetadata, first_message: Message
    ) -> None:
        await self._validate_scene_references(story_id, metadata)
        await self.save_metadata(story_id, scene_id, metadata)
        await self._save_messages(story_id, scene_id, [first_message])

    async def _validate_scene_references(
        self, story_id: str, metadata: SceneMetadata
    ) -> None:
        try:
            story_data = await yaml_storage.read_yaml(file_paths.story_file(story_id))
        except FileNotFoundError:
            raise NotFoundError(f"Story '{story_id}' not found")

        story = StoryYaml(**story_data)
        if story.type != "scene" and metadata.user_character_id is None:
            raise NarratorModeNotSupportedError()

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
        self, story_id: str, scene_id: int, messages: list[Message]
    ) -> None:
        data = {"messages": [m.model_dump() for m in messages]}
        await atomic_write(
            file_paths.scene_messages_file(story_id, scene_id),
            yaml_storage.dump_yaml(data),
        )
