from __future__ import annotations

from app.exceptions import NotFoundError
from app.models.domain import SceneRef, StoryIndexItem, StoryMeta
from app.models.storage import StoriesIndex, StoryYaml
from app.utils import file_paths, yaml_storage
from app.utils.atomic_write import atomic_write


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

        active_scene_id: int | None = None
        for scene in story.scenes:
            if not scene.finished:
                active_scene_id = scene.id
                break

        return StoryMeta(
            id=story.id,
            title=story.title,
            scenes=[
                SceneRef(id=s.id, finished=s.finished)
                for s in story.scenes
            ],
            active_scene_id=active_scene_id,
        )

    async def update_scene_finished(
        self, story_id: str, scene_id: int, summary: str
    ) -> None:
        try:
            data = await yaml_storage.read_yaml(file_paths.story_file(story_id))
        except FileNotFoundError:
            raise NotFoundError(f"Story '{story_id}' not found")

        story = StoryYaml(**data)

        scene = next((s for s in story.scenes if s.id == scene_id), None)
        if scene is None:
            raise NotFoundError(f"Scene '{scene_id}' not found")

        scene.finished = True

        await atomic_write(
            file_paths.story_file(story_id),
            yaml_storage.dump_yaml(story.model_dump()),
        )
