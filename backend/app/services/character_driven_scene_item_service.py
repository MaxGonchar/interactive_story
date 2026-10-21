from __future__ import annotations

from app.exceptions import (
    NotFoundError,
    NotLastItemError,
    OpeningItemNotDeletableError,
    SceneFinishedError,
)
from app.models.domain import CharacterDrivenMessage, SceneMetadata
from app.repositories.character_driven_scene_repository import (
    CharacterDrivenSceneRepository,
)
from app.repositories.scene_repository import SceneRepository
from app.repositories.story_repository import StoryRepository


class CharacterDrivenSceneItemService:
    def __init__(
        self,
        story_repo: StoryRepository,
        scene_repo: SceneRepository,
        character_driven_scene_repo: CharacterDrivenSceneRepository,
    ) -> None:
        self._story_repo = story_repo
        self._scene_repo = scene_repo
        self._character_driven_scene_repo = character_driven_scene_repo

    async def edit_item(
        self, story_id: str, scene_id: int, item_id: int, narration: str
    ) -> tuple[SceneMetadata, CharacterDrivenMessage]:
        metadata = await self._get_active_scene(story_id, scene_id)
        message = await self._character_driven_scene_repo.update_narration(
            story_id, scene_id, item_id, narration
        )
        return metadata, message

    async def delete_item(self, story_id: str, scene_id: int, item_id: int) -> None:
        await self._get_active_scene(story_id, scene_id)
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
        if item_index == 0:
            raise OpeningItemNotDeletableError()

        await self._character_driven_scene_repo.delete_last_message(story_id, scene_id)

    async def _get_active_scene(self, story_id: str, scene_id: int) -> SceneMetadata:
        await self._story_repo.get_story(story_id)
        metadata = await self._scene_repo.get_metadata(story_id, scene_id)
        if metadata.finished:
            raise SceneFinishedError()
        return metadata
