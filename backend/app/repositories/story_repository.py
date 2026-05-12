from __future__ import annotations

from app.models.domain import SceneRef, StoryIndexItem, StoryMeta
from app.models.storage import StoriesIndex, StoryYaml
from app.utils import file_paths, yaml_storage


class StoryRepository:
    async def list_stories(self) -> list[StoryIndexItem]:
        data = await yaml_storage.read_yaml(file_paths.stories_index())
        index = StoriesIndex(**data)
        sorted_entries = sorted(index.stories, key=lambda e: e.created_at, reverse=True)
        return [
            StoryIndexItem(id=e.id, title=e.title, created_at=e.created_at)
            for e in sorted_entries
        ]

    async def get_story(self, story_id: str) -> StoryMeta:
        try:
            data = await yaml_storage.read_yaml(file_paths.story_file(story_id))
        except FileNotFoundError:
            raise KeyError(story_id)

        story = StoryYaml(**data)

        active_scene_id: int | None = None
        for scene in story.scenes:
            if not scene.finished:
                active_scene_id = scene.id
                break

        return StoryMeta(
            id=story.id,
            title=story.title,
            character_ids=story.character_ids,
            scenes=[
                SceneRef(id=s.id, finished=s.finished, summary=s.summary)
                for s in story.scenes
            ],
            active_scene_id=active_scene_id,
        )
