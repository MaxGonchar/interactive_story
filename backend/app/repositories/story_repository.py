from __future__ import annotations

import asyncio

from app.exceptions import NotFoundError
from app.models.domain import SceneRef, StoryIndexItem, StoryMeta
from app.models.storage import SceneMetadataYaml, StoriesIndex, StoryYaml
from app.utils import file_paths, yaml_storage


class StoryRepository:
    async def list_stories(self) -> list[StoryIndexItem]:
        data = await yaml_storage.read_yaml(file_paths.stories_index())
        index = StoriesIndex(**data)
        sorted_entries = sorted(index.stories, key=lambda e: e.created_at, reverse=True)
        return [
            StoryIndexItem(id=e.id, title=e.title, created_at=e.created_at, type=e.type)
            for e in sorted_entries
        ]

    async def get_story(self, story_id: str) -> StoryMeta:
        try:
            data = await yaml_storage.read_yaml(file_paths.story_file(story_id))
        except FileNotFoundError:
            raise NotFoundError(f"Story '{story_id}' not found")

        story = StoryYaml(**data)

        def _scan_scene_ids() -> list[int]:
            d = file_paths.scenes_dir(story_id)
            return sorted(int(p.name) for p in d.iterdir() if p.is_dir() and p.name.isdigit())

        scene_ids = await asyncio.to_thread(_scan_scene_ids)

        async def _read_scene_ref(scene_id: int) -> SceneRef:
            meta_data = await yaml_storage.read_yaml(
                file_paths.scene_metadata_file(story_id, scene_id)
            )
            meta = SceneMetadataYaml(**meta_data)
            return SceneRef(id=scene_id, finished=meta.finished)

        scene_refs: list[SceneRef] = await asyncio.gather(
            *[_read_scene_ref(sid) for sid in scene_ids]
        )

        active_scene_id: int | None = None
        for scene in scene_refs:
            if not scene.finished:
                active_scene_id = scene.id
                break

        return StoryMeta(
            id=story_id,
            title=story.title,
            scenes=list(scene_refs),
            active_scene_id=active_scene_id,
        )
