from __future__ import annotations

from pathlib import Path

import pytest

from app.exceptions import NotFoundError
from app.repositories.story_repository import StoryRepository

FIXTURE_STORY_ID = "8fa93a9e-8dad-4fcb-b9cf-8e39f1707ec8"
FIXTURE_DATA_ROOT = Path(__file__).parents[3] / "data-test"


@pytest.fixture()
def data_root(monkeypatch):
    monkeypatch.setenv("DATA_ROOT", str(FIXTURE_DATA_ROOT))


@pytest.mark.asyncio
async def test_list_stories_returns_story_index_items(data_root):
    repo = StoryRepository()
    result = await repo.list_stories()

    assert len(result) >= 1
    item = result[0]
    assert item.id == FIXTURE_STORY_ID
    assert item.title == "Mila and Bun"
    assert item.created_at == "2024-06-01T12:00:00Z"
    assert item.type == "scene"


@pytest.mark.asyncio
async def test_list_stories_sorted_by_created_at_desc(data_root):
    repo = StoryRepository()
    result = await repo.list_stories()

    dates = [item.created_at for item in result]
    assert dates == sorted(dates, reverse=True)


@pytest.mark.asyncio
async def test_get_story_returns_story_meta(data_root):
    repo = StoryRepository()
    result = await repo.get_story(FIXTURE_STORY_ID)

    assert result.id == FIXTURE_STORY_ID
    assert result.title == "Mila and Bun"
    assert len(result.scenes) == 2


@pytest.mark.asyncio
async def test_get_story_scenes_have_correct_data(data_root):
    repo = StoryRepository()
    result = await repo.get_story(FIXTURE_STORY_ID)

    scene1 = result.scenes[0]
    assert scene1.id == 1
    assert scene1.finished is True

    scene2 = result.scenes[1]
    assert scene2.id == 2
    assert scene2.finished is False


@pytest.mark.asyncio
async def test_get_story_active_scene_id_is_first_unfinished(data_root):
    repo = StoryRepository()
    result = await repo.get_story(FIXTURE_STORY_ID)

    assert result.active_scene_id == 2


@pytest.mark.asyncio
async def test_get_story_nonexistent_raises_key_error(data_root):
    repo = StoryRepository()

    with pytest.raises(NotFoundError):
        await repo.get_story("nonexistent-id")
