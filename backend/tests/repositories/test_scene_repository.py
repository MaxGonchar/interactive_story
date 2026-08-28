from __future__ import annotations

import shutil
from pathlib import Path

import pytest
import yaml

from app.exceptions import NarratorModeNotSupportedError, NotFoundError
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
# add_messages
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_add_messages_appends_to_existing(writable_data_root):
    repo = SceneRepository()
    original = await repo.get_messages(FIXTURE_STORY_ID, FIXTURE_SCENE_ID)
    new_msgs = [
        Message(id=len(original) + 1, role="user", content="A new message."),
        Message(id=len(original) + 2, role="assistant", content="A reply."),
    ]

    await repo.add_messages(FIXTURE_STORY_ID, FIXTURE_SCENE_ID, new_msgs)
    result = await repo.get_messages(FIXTURE_STORY_ID, FIXTURE_SCENE_ID)

    assert len(result) == len(original) + 2
    assert result[-2].content == "A new message."
    assert result[-1].content == "A reply."


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


@pytest.mark.asyncio
async def test_save_metadata_does_not_write_id_or_story_id(writable_data_root):
    repo = SceneRepository()
    original = await repo.get_metadata(FIXTURE_STORY_ID, FIXTURE_SCENE_ID)

    await repo.save_metadata(FIXTURE_STORY_ID, FIXTURE_SCENE_ID, original)

    meta_path = (
        writable_data_root
        / "stories"
        / FIXTURE_STORY_ID
        / "scenes"
        / str(FIXTURE_SCENE_ID)
        / "meta.yaml"
    )
    raw = yaml.safe_load(meta_path.read_text())
    assert "id" not in raw
    assert "story_id" not in raw


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


# ---------------------------------------------------------------------------
# create_scene
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_create_scene_writes_metadata(writable_data_root):
    repo = SceneRepository()
    new_scene_id = 99
    metadata = SceneMetadata(
        id=new_scene_id,
        story_id=FIXTURE_STORY_ID,
        character_ids=["mila"],
        user_character_id="max",
        finished=False,
        scene_description=SceneDescription(
            general_scene_guide="A new guide.",
            writing_style="Terse.",
        ),
        context=["Context line one."],
    )
    first_msg = Message(id=1, role="assistant", content="Welcome to the new scene.")

    await repo.create_scene(FIXTURE_STORY_ID, new_scene_id, metadata, first_msg)

    result = await repo.get_metadata(FIXTURE_STORY_ID, new_scene_id)
    assert result.id == new_scene_id
    assert result.finished is False
    assert result.character_ids == ["mila"]
    assert result.user_character_id == "max"
    assert result.scene_description.general_scene_guide == "A new guide."
    assert result.context == ["Context line one."]


@pytest.mark.asyncio
async def test_create_scene_writes_first_message_with_id_1(writable_data_root):
    repo = SceneRepository()
    new_scene_id = 98
    metadata = SceneMetadata(
        id=new_scene_id,
        story_id=FIXTURE_STORY_ID,
        character_ids=[],
        user_character_id="max",
        finished=False,
        scene_description=SceneDescription(
            general_scene_guide="Guide.",
            writing_style="Style.",
        ),
        context=["ctx"],
    )
    first_msg = Message(id=1, role="assistant", content="First message content.")

    await repo.create_scene(FIXTURE_STORY_ID, new_scene_id, metadata, first_msg)

    messages = await repo.get_messages(FIXTURE_STORY_ID, new_scene_id)
    assert len(messages) == 1
    assert messages[0].id == 1
    assert messages[0].role == "assistant"
    assert messages[0].content == "First message content."


@pytest.mark.asyncio
async def test_create_scene_creates_directory(writable_data_root):
    repo = SceneRepository()
    new_scene_id = 97
    metadata = SceneMetadata(
        id=new_scene_id,
        story_id=FIXTURE_STORY_ID,
        character_ids=[],
        user_character_id="max",
        finished=False,
        scene_description=SceneDescription(
            general_scene_guide="Guide.",
            writing_style="Style.",
        ),
        context=["ctx"],
    )
    first_msg = Message(id=1, role="assistant", content="Hello.")

    scene_dir = writable_data_root / "stories" / FIXTURE_STORY_ID / "scenes" / str(new_scene_id)
    assert not scene_dir.exists()

    await repo.create_scene(FIXTURE_STORY_ID, new_scene_id, metadata, first_msg)

    assert scene_dir.exists()
    assert (scene_dir / "meta.yaml").exists()
    assert (scene_dir / "messages.yaml").exists()


@pytest.mark.asyncio
async def test_create_scene_persists_null_user_character_for_scene_story(writable_data_root):
    repo = SceneRepository()
    metadata = SceneMetadata(
        id=96,
        story_id=FIXTURE_STORY_ID,
        character_ids=["mila"],
        user_character_id=None,
        finished=False,
        scene_description=SceneDescription(general_scene_guide="Guide.", writing_style="Style."),
    )

    await repo.create_scene(
        FIXTURE_STORY_ID,
        96,
        metadata,
        Message(id=1, role="assistant", content="Hello."),
    )

    result = await repo.get_metadata(FIXTURE_STORY_ID, 96)
    assert result.user_character_id is None


@pytest.mark.asyncio
async def test_create_scene_rejects_missing_character_reference(writable_data_root):
    repo = SceneRepository()
    metadata = SceneMetadata(
        id=95,
        story_id=FIXTURE_STORY_ID,
        character_ids=["missing"],
        user_character_id="max",
        finished=False,
        scene_description=SceneDescription(general_scene_guide="Guide.", writing_style="Style."),
    )

    with pytest.raises(NotFoundError, match="Character 'missing' not found"):
        await repo.create_scene(
            FIXTURE_STORY_ID,
            95,
            metadata,
            Message(id=1, role="assistant", content="Hello."),
        )


@pytest.mark.asyncio
async def test_create_scene_rejects_narrator_for_choice_driven_story(writable_data_root):
    story_path = writable_data_root / "stories" / FIXTURE_STORY_ID / "story.yaml"
    story_data = yaml.safe_load(story_path.read_text())
    story_data["type"] = "choice_driven"
    story_path.write_text(yaml.safe_dump(story_data))
    repo = SceneRepository()
    metadata = SceneMetadata(
        id=94,
        story_id=FIXTURE_STORY_ID,
        character_ids=["mila"],
        user_character_id=None,
        finished=False,
        scene_description=SceneDescription(general_scene_guide="Guide.", writing_style="Style."),
    )

    with pytest.raises(NarratorModeNotSupportedError):
        await repo.create_scene(
            FIXTURE_STORY_ID,
            94,
            metadata,
            Message(id=1, role="assistant", content="Hello."),
        )
