import shutil
from pathlib import Path

import pytest

from app.exceptions import NotFoundError
from app.models.domain import Message, SceneDescription, SceneMetadata
from app.repositories.scene_repository import SceneRepository

FIXTURE_STORY_ID = "8fa93a9e-8dad-4fcb-b9cf-8e39f1707ec8"
FIXTURE_SCENE_ID = 2
FIXTURE_DATA_ROOT = Path(__file__).parents[3] / "data-test"


@pytest.fixture()
def data_root(monkeypatch):
    monkeypatch.setenv("DATA_ROOT", str(FIXTURE_DATA_ROOT))


@pytest.fixture()
def writable_data_root(monkeypatch, tmp_path):
    copy = tmp_path / "data-test"
    shutil.copytree(FIXTURE_DATA_ROOT, copy)
    monkeypatch.setenv("DATA_ROOT", str(copy))
    return copy


# ---------------------------------------------------------------------------
# get_metadata
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_get_metadata_returns_scene_metadata(data_root):
    repo = SceneRepository()
    result = await repo.get_metadata(FIXTURE_STORY_ID, FIXTURE_SCENE_ID)

    assert result.id == FIXTURE_SCENE_ID
    assert result.story_id == FIXTURE_STORY_ID
    assert result.user_character_id == "max"
    assert isinstance(result.character_ids, list)
    assert isinstance(result.scene_description, SceneDescription)


@pytest.mark.asyncio
async def test_get_metadata_nonexistent_raises_key_error(data_root):
    repo = SceneRepository()

    with pytest.raises(NotFoundError):
        await repo.get_metadata(FIXTURE_STORY_ID, 999)


# ---------------------------------------------------------------------------
# get_messages
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_get_messages_returns_message_list(data_root):
    repo = SceneRepository()
    result = await repo.get_messages(FIXTURE_STORY_ID, FIXTURE_SCENE_ID)

    assert len(result) == 2
    assert all(isinstance(m, Message) for m in result)


@pytest.mark.asyncio
async def test_get_messages_sorted_by_id(data_root):
    repo = SceneRepository()
    result = await repo.get_messages(FIXTURE_STORY_ID, FIXTURE_SCENE_ID)

    ids = [m.id for m in result]
    assert ids == sorted(ids)


@pytest.mark.asyncio
async def test_get_messages_returns_empty_list_when_file_missing(data_root):
    repo = SceneRepository()
    result = await repo.get_messages(FIXTURE_STORY_ID, 999)

    assert result == []


# ---------------------------------------------------------------------------
# add_message
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_add_message_appends_to_existing(writable_data_root):
    repo = SceneRepository()
    original = await repo.get_messages(FIXTURE_STORY_ID, FIXTURE_SCENE_ID)
    new_msg = Message(id=len(original) + 1, role="user", content="A new message.")

    await repo.add_message(FIXTURE_STORY_ID, FIXTURE_SCENE_ID, new_msg)
    result = await repo.get_messages(FIXTURE_STORY_ID, FIXTURE_SCENE_ID)

    assert len(result) == len(original) + 1
    assert result[-1].content == "A new message."


# ---------------------------------------------------------------------------
# save_metadata / round-trip
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_save_metadata_round_trip(writable_data_root):
    repo = SceneRepository()
    original = await repo.get_metadata(FIXTURE_STORY_ID, FIXTURE_SCENE_ID)
    updated = SceneMetadata(
        id=original.id,
        story_id=original.story_id,
        character_ids=original.character_ids,
        user_character_id=original.user_character_id,
        finished=True,
        scene_description=original.scene_description,
        scene_summary=["A summary line."],
    )

    await repo.save_metadata(FIXTURE_STORY_ID, FIXTURE_SCENE_ID, updated)
    result = await repo.get_metadata(FIXTURE_STORY_ID, FIXTURE_SCENE_ID)

    assert result.finished is True
    assert result.scene_summary == ["A summary line."]


# ---------------------------------------------------------------------------
# update_message
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_update_message_changes_only_target(writable_data_root):
    repo = SceneRepository()
    original = await repo.get_messages(FIXTURE_STORY_ID, FIXTURE_SCENE_ID)

    updated = await repo.update_message(
        FIXTURE_STORY_ID, FIXTURE_SCENE_ID, message_id=1, new_content="Updated content."
    )

    assert updated.id == 1
    assert updated.content == "Updated content."

    after = await repo.get_messages(FIXTURE_STORY_ID, FIXTURE_SCENE_ID)
    assert len(after) == len(original)
    unchanged = next(m for m in after if m.id == 2)
    assert unchanged.content == original[1].content


@pytest.mark.asyncio
async def test_update_message_nonexistent_raises_key_error(writable_data_root):
    repo = SceneRepository()

    with pytest.raises(NotFoundError):
        await repo.update_message(FIXTURE_STORY_ID, FIXTURE_SCENE_ID, message_id=999, new_content="x")


# ---------------------------------------------------------------------------
# delete_message
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_delete_message_removes_only_target(writable_data_root):
    repo = SceneRepository()
    original = await repo.get_messages(FIXTURE_STORY_ID, FIXTURE_SCENE_ID)

    await repo.delete_message(FIXTURE_STORY_ID, FIXTURE_SCENE_ID, message_id=1)

    after = await repo.get_messages(FIXTURE_STORY_ID, FIXTURE_SCENE_ID)
    assert len(after) == len(original) - 1
    assert all(m.id != 1 for m in after)


@pytest.mark.asyncio
async def test_delete_message_nonexistent_raises_key_error(writable_data_root):
    repo = SceneRepository()

    with pytest.raises(NotFoundError):
        await repo.delete_message(FIXTURE_STORY_ID, FIXTURE_SCENE_ID, message_id=999)
