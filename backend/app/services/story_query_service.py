from __future__ import annotations

from app.models.domain import StoryIndexItem, StoryMeta
from app.repositories.story_repository import StoryRepository


class StoryQueryService:
    def __init__(self, repo: StoryRepository) -> None:
        self._repo = repo

    async def list_stories(self) -> list[StoryIndexItem]:
        return await self._repo.list_stories()

    async def get_story(self, story_id: str) -> StoryMeta:
        return await self._repo.get_story(story_id)
