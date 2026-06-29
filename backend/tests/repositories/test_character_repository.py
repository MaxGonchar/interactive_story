from pathlib import Path

import pytest

from app.exceptions import NotFoundError
from app.repositories.character_repository import CharacterRepository

FIXTURE_STORY_ID = "8fa93a9e-8dad-4fcb-b9cf-8e39f1707ec8"
FIXTURE_DATA_ROOT = Path(__file__).parents[3] / "data-test"


@pytest.fixture()
def data_root(monkeypatch):
    monkeypatch.setenv("DATA_ROOT", str(FIXTURE_DATA_ROOT))


@pytest.mark.asyncio
async def test_get_character_returns_character_card(data_root):
    repo = CharacterRepository()
    result = await repo.get_character(FIXTURE_STORY_ID, "mila")

    assert result.id == "mila"
    assert result.story_id == FIXTURE_STORY_ID
    assert result.name == "Mila"


@pytest.mark.asyncio
async def test_get_character_returns_all_fields(data_root):
    repo = CharacterRepository()
    result = await repo.get_character(FIXTURE_STORY_ID, "mila")

    assert isinstance(result.features, dict)
    assert len(result.features) > 0
    assert isinstance(result.memory, list)
    assert len(result.memory) > 0
    assert isinstance(result.memory[0], str)


@pytest.mark.asyncio
async def test_get_character_nonexistent_raises_key_error(data_root):
    repo = CharacterRepository()

    with pytest.raises(NotFoundError):
        await repo.get_character(FIXTURE_STORY_ID, "nonexistent-character")


@pytest.mark.asyncio
async def test_get_characters_returns_list(data_root):
    repo = CharacterRepository()
    result = await repo.get_characters(FIXTURE_STORY_ID, ["mila", "bun"])

    assert len(result) == 2
    assert result[0].id == "mila"
    assert result[1].id == "bun"


@pytest.mark.asyncio
async def test_get_characters_preserves_order(data_root):
    repo = CharacterRepository()
    result = await repo.get_characters(FIXTURE_STORY_ID, ["bun", "mila"])

    assert result[0].id == "bun"
    assert result[1].id == "mila"


@pytest.mark.asyncio
async def test_get_characters_missing_id_raises_key_error(data_root):
    repo = CharacterRepository()

    with pytest.raises(NotFoundError):
        await repo.get_characters(FIXTURE_STORY_ID, ["mila", "nonexistent-character"])
