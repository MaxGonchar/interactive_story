from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from app.exceptions import InvalidMessageAuthorError, NotFoundError
from app.models.domain import (
    CharacterDrivenInput,
    CharacterDrivenLLMData,
    CharacterDrivenMessage,
    SceneDescription,
    SceneMetadata,
)
from app.repositories.character_driven_scene_repository import (
    CharacterDrivenSceneRepository,
)

STORY_ID = "story-1"
SCENE_ID = 1


@pytest.fixture()
def data_root(monkeypatch, tmp_path) -> Path:
    monkeypatch.setenv("DATA_ROOT", str(tmp_path))
    characters = tmp_path / "stories" / STORY_ID / "characters"
    characters.mkdir(parents=True)
    for character_id in ("captain", "navigator"):
        (characters / f"{character_id}.yaml").write_text(
            yaml.safe_dump({"name": character_id.title(), "features": {}, "memory": []})
        )
    return tmp_path


def _scene_dir(root: Path) -> Path:
    return root / "stories" / STORY_ID / "scenes" / str(SCENE_ID)


def _read_yaml(path: Path) -> dict:
    return yaml.safe_load(path.read_text())


def _make_metadata(user_character_id: str | None = "captain") -> SceneMetadata:
    return SceneMetadata(
        id=SCENE_ID,
        story_id=STORY_ID,
        character_ids=["navigator"],
        user_character_id=user_character_id,
        finished=False,
        scene_description=SceneDescription(
            general_scene_guide="Guide.", writing_style="Style."
        ),
        scene_summary=None,
        context=["Context."],
    )


def _llm_data(character_model_id: str | None = None) -> CharacterDrivenLLMData:
    return CharacterDrivenLLMData(
        narrator_model_id="narrator", character_model_id=character_model_id
    )


def _opening() -> CharacterDrivenMessage:
    return CharacterDrivenMessage(
        id=1, input=None, narration="Opening.", llm_data=_llm_data("character")
    )


def _player_input(author: str | None = "captain") -> CharacterDrivenInput:
    return CharacterDrivenInput(author=author, action="I look around.")


async def _create(user_character_id: str | None = "captain") -> CharacterDrivenSceneRepository:
    repo = CharacterDrivenSceneRepository()
    await repo.create_scene(
        STORY_ID, SCENE_ID, _make_metadata(user_character_id), _opening()
    )
    return repo


# --- create_scene ---


@pytest.mark.asyncio
async def test_create_scene_writes_metadata_and_opening_message(data_root):
    await _create()

    assert _read_yaml(_scene_dir(data_root) / "meta.yaml") == {
        "finished": False,
        "character_ids": ["navigator"],
        "user_character_id": "captain",
        "scene_description": {
            "general_scene_guide": "Guide.",
            "writing_style": "Style.",
        },
        "scene_summary": None,
        "context": ["Context."],
    }
    assert _read_yaml(_scene_dir(data_root) / "messages.yaml") == {
        "messages": [
            {
                "id": 1,
                "input": None,
                "narration": "Opening.",
                "llm_data": {
                    "narrator_model_id": "narrator",
                    "character_model_id": "character",
                },
            }
        ]
    }


@pytest.mark.asyncio
async def test_create_scene_allows_null_user_character(data_root):
    repo = await _create(user_character_id=None)

    result = await repo.get_messages(STORY_ID, SCENE_ID)

    assert result == [_opening()]


@pytest.mark.asyncio
async def test_create_scene_missing_character_file_raises_not_found(data_root):
    repo = CharacterDrivenSceneRepository()
    metadata = _make_metadata().model_copy(update={"character_ids": ["ghost"]})

    with pytest.raises(NotFoundError):
        await repo.create_scene(STORY_ID, SCENE_ID, metadata, _opening())


@pytest.mark.asyncio
async def test_create_scene_missing_user_character_file_raises_not_found(data_root):
    repo = CharacterDrivenSceneRepository()

    with pytest.raises(NotFoundError):
        await repo.create_scene(STORY_ID, SCENE_ID, _make_metadata("ghost"), _opening())

    assert not (_scene_dir(data_root) / "meta.yaml").exists()


# --- get_messages ---


@pytest.mark.asyncio
async def test_get_messages_missing_file_returns_empty_list(data_root):
    repo = CharacterDrivenSceneRepository()

    assert await repo.get_messages(STORY_ID, SCENE_ID) == []


@pytest.mark.asyncio
async def test_get_messages_returns_sorted_by_id(data_root):
    await _create()
    path = _scene_dir(data_root) / "messages.yaml"
    data = _read_yaml(path)
    data["messages"].insert(0, {**data["messages"][0], "id": 5, "narration": "Later."})
    path.write_text(yaml.safe_dump(data))

    result = await CharacterDrivenSceneRepository().get_messages(STORY_ID, SCENE_ID)

    assert [m.id for m in result] == [1, 5]


# --- append_message ---


@pytest.mark.asyncio
async def test_append_message_assigns_max_id_plus_one(data_root):
    repo = await _create()

    result = await repo.append_message(
        STORY_ID, SCENE_ID, _player_input(), "Turn.", _llm_data()
    )

    assert result == CharacterDrivenMessage(
        id=2, input=_player_input(), narration="Turn.", llm_data=_llm_data()
    )
    assert await repo.get_messages(STORY_ID, SCENE_ID) == [_opening(), result]


@pytest.mark.asyncio
async def test_append_message_reuses_id_after_delete_last(data_root):
    repo = await _create()
    await repo.append_message(STORY_ID, SCENE_ID, _player_input(), "A.", _llm_data())
    await repo.delete_last_message(STORY_ID, SCENE_ID)

    result = await repo.append_message(
        STORY_ID, SCENE_ID, _player_input(), "B.", _llm_data()
    )

    assert result.id == 2


@pytest.mark.asyncio
async def test_append_message_npc_author_in_character_ids_is_valid(data_root):
    repo = await _create()
    npc_input = CharacterDrivenInput(
        author="navigator", action="Warns.", guidance="Warn."
    )

    result = await repo.append_message(
        STORY_ID, SCENE_ID, npc_input, "Turn.", _llm_data("character")
    )

    assert result.input == npc_input


@pytest.mark.asyncio
async def test_append_message_null_author_valid_without_user_character(data_root):
    repo = await _create(user_character_id=None)

    result = await repo.append_message(
        STORY_ID, SCENE_ID, _player_input(None), "Turn.", _llm_data()
    )

    assert result.id == 2


@pytest.mark.asyncio
async def test_append_message_null_author_with_user_character_raises(data_root):
    repo = await _create()

    with pytest.raises(InvalidMessageAuthorError):
        await repo.append_message(
            STORY_ID, SCENE_ID, _player_input(None), "Turn.", _llm_data()
        )

    assert await repo.get_messages(STORY_ID, SCENE_ID) == [_opening()]


@pytest.mark.asyncio
async def test_append_message_unknown_npc_author_raises(data_root):
    repo = await _create()

    with pytest.raises(InvalidMessageAuthorError):
        await repo.append_message(
            STORY_ID, SCENE_ID, _player_input("stranger"), "Turn.", _llm_data()
        )


# --- update_narration ---


@pytest.mark.asyncio
async def test_update_narration_changes_only_narration(data_root):
    repo = await _create()
    await repo.append_message(STORY_ID, SCENE_ID, _player_input(), "Old.", _llm_data())

    result = await repo.update_narration(STORY_ID, SCENE_ID, 2, "New.")

    expected = CharacterDrivenMessage(
        id=2, input=_player_input(), narration="New.", llm_data=_llm_data()
    )
    assert result == expected
    assert await repo.get_messages(STORY_ID, SCENE_ID) == [_opening(), expected]


@pytest.mark.asyncio
async def test_update_narration_unknown_id_raises_not_found(data_root):
    repo = await _create()

    with pytest.raises(NotFoundError):
        await repo.update_narration(STORY_ID, SCENE_ID, 99, "New.")


# --- replace_message ---


@pytest.mark.asyncio
async def test_replace_message_overwrites_item_with_same_id(data_root):
    repo = await _create()
    await repo.append_message(STORY_ID, SCENE_ID, _player_input(), "Old.", _llm_data())
    npc_input = CharacterDrivenInput(author="navigator", action="Acts.", guidance=None)

    result = await repo.replace_message(
        STORY_ID, SCENE_ID, 2, npc_input, "Replaced.", _llm_data("character")
    )

    expected = CharacterDrivenMessage(
        id=2, input=npc_input, narration="Replaced.", llm_data=_llm_data("character")
    )
    assert result == expected
    assert await repo.get_messages(STORY_ID, SCENE_ID) == [_opening(), expected]


@pytest.mark.asyncio
async def test_replace_message_unknown_id_raises_not_found(data_root):
    repo = await _create()

    with pytest.raises(NotFoundError):
        await repo.replace_message(
            STORY_ID, SCENE_ID, 99, _player_input(), "X.", _llm_data()
        )


@pytest.mark.asyncio
async def test_replace_message_invalid_author_raises_and_keeps_item(data_root):
    repo = await _create()
    original = await repo.append_message(
        STORY_ID, SCENE_ID, _player_input(), "Old.", _llm_data()
    )

    with pytest.raises(InvalidMessageAuthorError):
        await repo.replace_message(
            STORY_ID, SCENE_ID, 2, _player_input("stranger"), "X.", _llm_data()
        )

    assert await repo.get_messages(STORY_ID, SCENE_ID) == [_opening(), original]


# --- delete_last_message ---


@pytest.mark.asyncio
async def test_delete_last_message_removes_only_last_item(data_root):
    repo = await _create()
    await repo.append_message(STORY_ID, SCENE_ID, _player_input(), "A.", _llm_data())
    await repo.append_message(STORY_ID, SCENE_ID, _player_input(), "B.", _llm_data())

    await repo.delete_last_message(STORY_ID, SCENE_ID)

    result = await repo.get_messages(STORY_ID, SCENE_ID)
    assert [m.id for m in result] == [1, 2]
    assert result[1].narration == "A."


@pytest.mark.asyncio
async def test_delete_last_message_without_messages_raises_not_found(data_root):
    repo = CharacterDrivenSceneRepository()

    with pytest.raises(NotFoundError):
        await repo.delete_last_message(STORY_ID, SCENE_ID)
