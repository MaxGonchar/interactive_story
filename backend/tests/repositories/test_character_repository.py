from __future__ import annotations

from pathlib import Path

import pytest

from app.exceptions import NotFoundError
from app.repositories.character_repository import CharacterRepository
from app.utils import file_paths, yaml_storage

FIXTURE_STORY_ID = "8fa93a9e-8dad-4fcb-b9cf-8e39f1707ec8"
FIXTURE_DATA_ROOT = Path(__file__).parents[3] / "data-test"


@pytest.fixture()
def data_root(monkeypatch):
    monkeypatch.setenv("DATA_ROOT", str(FIXTURE_DATA_ROOT))


@pytest.fixture()
def character_file(tmp_path, monkeypatch):
    monkeypatch.setenv("DATA_ROOT", str(tmp_path))
    path = file_paths.character_file(FIXTURE_STORY_ID, "mila")
    path.parent.mkdir(parents=True)
    path.write_bytes(
        yaml_storage.dump_yaml(
            {
                "name": "Mila",
                "features": {"traits": ["curious"]},
                "memory": ["existing memory"],
                "handwritten_note": {"detail": "preserve me"},
            }
        )
    )
    return path


@pytest.mark.asyncio
async def test_get_character_returns_character_card(data_root):
    repo = CharacterRepository()
    result = await repo.get_character(FIXTURE_STORY_ID, "mila")

    assert result.id == "mila"
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


@pytest.mark.asyncio
async def test_list_characters_returns_all_characters(data_root):
    repo = CharacterRepository()
    result = await repo.list_characters(FIXTURE_STORY_ID)

    ids = {c.id for c in result}
    assert ids == {"mila", "bun", "max"}


@pytest.mark.asyncio
async def test_list_characters_returns_character_cards(data_root):
    repo = CharacterRepository()
    result = await repo.list_characters(FIXTURE_STORY_ID)

    for card in result:
        assert card.id
        assert card.name


@pytest.mark.asyncio
async def test_list_characters_unknown_story_raises_not_found(data_root):
    repo = CharacterRepository()

    with pytest.raises(NotFoundError):
        await repo.list_characters("nonexistent-story-id")


@pytest.mark.asyncio
async def test_append_memory_adds_unique_entries_in_order_and_is_idempotent(character_file):
    repo = CharacterRepository()
    entries = ["new memory", "existing memory", "another memory", "new memory"]

    await repo.append_memory(FIXTURE_STORY_ID, "mila", entries)
    await repo.append_memory(FIXTURE_STORY_ID, "mila", entries)

    data = await yaml_storage.read_yaml(character_file)
    assert data["memory"] == [
        "existing memory",
        "new memory",
        "another memory",
    ]


@pytest.mark.asyncio
async def test_set_memory_replaces_list_exactly(character_file):
    repo = CharacterRepository()
    memory = ["replacement", "replacement", "last entry"]

    await repo.set_memory(FIXTURE_STORY_ID, "mila", memory)

    data = await yaml_storage.read_yaml(character_file)
    assert data["memory"] == memory


@pytest.mark.parametrize(
    ("method_name", "memory"),
    [("append_memory", ["new memory"]), ("set_memory", ["replacement"])],
)
@pytest.mark.asyncio
async def test_memory_methods_missing_character_raise_not_found(
    tmp_path, monkeypatch, method_name, memory
):
    monkeypatch.setenv("DATA_ROOT", str(tmp_path))
    repo = CharacterRepository()

    with pytest.raises(NotFoundError):
        await getattr(repo, method_name)(FIXTURE_STORY_ID, "missing", memory)


@pytest.mark.parametrize(
    ("method_name", "memory"),
    [
        ("append_memory", ["added memory"]),
        ("set_memory", ["replacement memory"]),
    ],
)
@pytest.mark.asyncio
async def test_memory_methods_preserve_unknown_yaml_keys(
    character_file, method_name, memory
):
    repo = CharacterRepository()

    await getattr(repo, method_name)(FIXTURE_STORY_ID, "mila", memory)

    data = await yaml_storage.read_yaml(character_file)
    assert data["handwritten_note"] == {"detail": "preserve me"}
