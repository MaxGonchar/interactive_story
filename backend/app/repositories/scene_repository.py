from __future__ import annotations

from app.models.domain import Message, SceneDescription, SceneMetadata
from app.models.storage import MessagesYaml, SceneMetadataYaml
from app.utils import file_paths, yaml_storage
from app.utils.atomic_write import atomic_write


class SceneRepository:
    async def get_metadata(self, story_id: str, scene_id: int) -> SceneMetadata:
        try:
            data = await yaml_storage.read_yaml(
                file_paths.scene_metadata_file(story_id, scene_id)
            )
        except FileNotFoundError:
            raise KeyError(scene_id)

        raw = SceneMetadataYaml(**data)
        return SceneMetadata(
            id=raw.id,
            story_id=story_id,
            characters_ids=raw.characters_ids,
            finished=raw.finished,
            scene_description=SceneDescription(
                general_scene_guide=raw.scene_description.general_scene_guide,
                writing_style=raw.scene_description.writing_style,
            ),
            scene_summary=raw.scene_summary,
        )

    async def save_metadata(
        self, story_id: str, scene_id: int, metadata: SceneMetadata
    ) -> None:
        data = metadata.model_dump()
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

    async def add_message(
        self, story_id: str, scene_id: int, message: Message
    ) -> None:
        messages = await self.get_messages(story_id, scene_id)
        messages.append(message)
        await self._save_messages(story_id, scene_id, messages)

    async def update_message(
        self, story_id: str, scene_id: int, message_id: int, new_content: str
    ) -> Message:
        messages = await self.get_messages(story_id, scene_id)
        index = next((i for i, m in enumerate(messages) if m.id == message_id), None)
        if index is None:
            raise KeyError(message_id)

        updated = Message(id=messages[index].id, role=messages[index].role, content=new_content)
        messages[index] = updated
        await self._save_messages(story_id, scene_id, messages)
        return updated

    async def delete_message(
        self, story_id: str, scene_id: int, message_id: int
    ) -> None:
        messages = await self.get_messages(story_id, scene_id)
        if not any(m.id == message_id for m in messages):
            raise KeyError(message_id)

        await self._save_messages(
            story_id, scene_id, [m for m in messages if m.id != message_id]
        )

    async def _save_messages(
        self, story_id: str, scene_id: int, messages: list[Message]
    ) -> None:
        data = {"messages": [m.model_dump() for m in messages]}
        await atomic_write(
            file_paths.scene_messages_file(story_id, scene_id),
            yaml_storage.dump_yaml(data),
        )
