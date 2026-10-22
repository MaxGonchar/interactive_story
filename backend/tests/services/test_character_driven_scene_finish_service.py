from __future__ import annotations

from unittest.mock import AsyncMock

import app.repositories.character_repository as character_repository_module
import app.repositories.scene_repository as scene_repository_module
import pytest

from app.exceptions import (
    InvalidCharacterMemoryUpdatesError,
    SceneFinishedError,
)
from app.models.domain import CharacterCard
from app.repositories.character_repository import CharacterRepository
from app.repositories.scene_repository import SceneRepository
from app.services.character_driven_scene_finish_service import (
    CharacterDrivenSceneFinishService,
)
from app.utils import file_paths, yaml_storage
from app.utils.atomic_write import atomic_write
from tests.factories import make_scene_metadata

STORY_ID = "finish-story"
SCENE_ID = 1
PARTICIPANT_IDS = ["captain", "navigator", "hero"]
SUMMARY = ["The crew uncovered a betrayal."]
MEMORY_UPDATES = {
    "captain": ["The harbor master cannot be trusted."],
    "navigator": [],
    "hero": ["The captain accepted my warning."],
}


def make_service(metadata=None):
    scene_repo = AsyncMock()
    scene_repo.get_metadata.return_value = metadata or make_scene_metadata(
        story_id=STORY_ID,
        scene_id=SCENE_ID,
        character_ids=["captain", "navigator"],
        user_character_id="hero",
    )
    character_repo = AsyncMock()
    character_repo.get_characters.return_value = [
        CharacterCard(
            id=character_id,
            name=character_id.title(),
            memory=[f"{character_id} memory"],
        )
        for character_id in PARTICIPANT_IDS
    ]
    service = CharacterDrivenSceneFinishService(scene_repo, character_repo)
    return service, scene_repo, character_repo


def seed_finish_files(tmp_path, monkeypatch):
    monkeypatch.setenv("DATA_ROOT", str(tmp_path))
    paths = {
        character_id: file_paths.character_file(STORY_ID, character_id)
        for character_id in PARTICIPANT_IDS
    }
    metadata_path = file_paths.scene_metadata_file(STORY_ID, SCENE_ID)

    for character_id, path in paths.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(
            yaml_storage.dump_yaml(
                {
                    "name": character_id.title(),
                    "features": {"traits": ["observant"]},
                    "memory": [f"{character_id} memory"],
                    "handwritten_note": "preserve this",
                }
            )
        )

    metadata_path.parent.mkdir(parents=True, exist_ok=True)
    metadata_path.write_bytes(
        yaml_storage.dump_yaml(
            {
                "finished": False,
                "character_ids": ["captain", "navigator"],
                "user_character_id": "hero",
                "scene_description": {
                    "general_scene_guide": "Keep tension rising.",
                    "writing_style": "Cinematic.",
                },
                "scene_summary": None,
                "context": ["The ship reached the harbor."],
            }
        )
    )
    return {**paths, "meta": metadata_path}


# --- finish validation ---


@pytest.mark.asyncio
async def test_finish_appends_memories_and_saves_metadata():
    service, scene_repo, character_repo = make_service()

    result = await service.finish(STORY_ID, SCENE_ID, SUMMARY, MEMORY_UPDATES)

    expected_metadata = make_scene_metadata(
        story_id=STORY_ID,
        scene_id=SCENE_ID,
        character_ids=["captain", "navigator"],
        user_character_id="hero",
    ).model_copy(update={"finished": True, "scene_summary": SUMMARY})
    assert result.model_dump() == expected_metadata.model_dump()
    character_repo.get_characters.assert_awaited_once_with(STORY_ID, PARTICIPANT_IDS)
    assert character_repo.append_memory.await_args_list == [
        ((STORY_ID, "captain", MEMORY_UPDATES["captain"]), {}),
        ((STORY_ID, "navigator", MEMORY_UPDATES["navigator"]), {}),
        ((STORY_ID, "hero", MEMORY_UPDATES["hero"]), {}),
    ]
    scene_repo.save_metadata.assert_awaited_once_with(STORY_ID, SCENE_ID, result)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "memory_updates",
    [
        {"captain": [], "navigator": []},
        {**MEMORY_UPDATES, "stranger": []},
    ],
)
async def test_finish_rejects_memory_updates_without_exact_participant_keys(
    memory_updates,
):
    service, scene_repo, character_repo = make_service()

    with pytest.raises(InvalidCharacterMemoryUpdatesError):
        await service.finish(STORY_ID, SCENE_ID, SUMMARY, memory_updates)

    character_repo.get_characters.assert_not_awaited()
    character_repo.append_memory.assert_not_awaited()
    scene_repo.save_metadata.assert_not_awaited()


@pytest.mark.asyncio
async def test_finish_rejects_already_finished_scene():
    metadata = make_scene_metadata(
        story_id=STORY_ID,
        scene_id=SCENE_ID,
        finished=True,
    )
    service, scene_repo, character_repo = make_service(metadata=metadata)

    with pytest.raises(SceneFinishedError):
        await service.finish(STORY_ID, SCENE_ID, SUMMARY, MEMORY_UPDATES)

    character_repo.get_characters.assert_not_awaited()
    character_repo.append_memory.assert_not_awaited()
    scene_repo.save_metadata.assert_not_awaited()


# --- write rollback ---


@pytest.mark.asyncio
@pytest.mark.parametrize("failure_write", [1, 2, 3])
async def test_finish_write_failure_restores_all_yaml_files(
    tmp_path, monkeypatch, failure_write
):
    paths = seed_finish_files(tmp_path, monkeypatch)
    original_contents = {path: path.read_bytes() for path in paths.values()}
    write_count = 0

    async def fail_on_nth_write(path, data):
        nonlocal write_count
        write_count += 1
        if write_count == failure_write:
            raise OSError("simulated write failure")
        await atomic_write(path, data)

    monkeypatch.setattr(
        character_repository_module, "atomic_write", fail_on_nth_write
    )
    monkeypatch.setattr(scene_repository_module, "atomic_write", fail_on_nth_write)
    service = CharacterDrivenSceneFinishService(
        SceneRepository(), CharacterRepository()
    )

    with pytest.raises(OSError, match="simulated write failure"):
        await service.finish(STORY_ID, SCENE_ID, SUMMARY, MEMORY_UPDATES)

    assert {path: path.read_bytes() for path in paths.values()} == original_contents


@pytest.mark.asyncio
async def test_retry_after_interrupted_partial_finish_does_not_duplicate_memory(
    tmp_path, monkeypatch
):
    paths = seed_finish_files(tmp_path, monkeypatch)
    write_count = 0

    class SimulatedProcessCrash(BaseException):
        pass

    async def crash_on_second_write(path, data):
        nonlocal write_count
        write_count += 1
        if write_count == 2:
            raise SimulatedProcessCrash()
        await atomic_write(path, data)

    monkeypatch.setattr(
        character_repository_module, "atomic_write", crash_on_second_write
    )
    monkeypatch.setattr(scene_repository_module, "atomic_write", crash_on_second_write)
    service = CharacterDrivenSceneFinishService(
        SceneRepository(), CharacterRepository()
    )

    with pytest.raises(SimulatedProcessCrash):
        await service.finish(STORY_ID, SCENE_ID, SUMMARY, MEMORY_UPDATES)

    monkeypatch.setattr(character_repository_module, "atomic_write", atomic_write)
    monkeypatch.setattr(scene_repository_module, "atomic_write", atomic_write)
    result = await service.finish(STORY_ID, SCENE_ID, SUMMARY, MEMORY_UPDATES)

    captain = await yaml_storage.read_yaml(paths["captain"])
    navigator = await yaml_storage.read_yaml(paths["navigator"])
    hero = await yaml_storage.read_yaml(paths["hero"])
    metadata = await yaml_storage.read_yaml(paths["meta"])
    assert captain == {
        "name": "Captain",
        "features": {"traits": ["observant"]},
        "memory": ["captain memory", MEMORY_UPDATES["captain"][0]],
        "handwritten_note": "preserve this",
    }
    assert navigator == {
        "name": "Navigator",
        "features": {"traits": ["observant"]},
        "memory": ["navigator memory"],
        "handwritten_note": "preserve this",
    }
    assert hero == {
        "name": "Hero",
        "features": {"traits": ["observant"]},
        "memory": ["hero memory", MEMORY_UPDATES["hero"][0]],
        "handwritten_note": "preserve this",
    }
    assert metadata == {
        "finished": True,
        "character_ids": ["captain", "navigator"],
        "user_character_id": "hero",
        "scene_description": {
            "general_scene_guide": "Keep tension rising.",
            "writing_style": "Cinematic.",
        },
        "scene_summary": SUMMARY,
        "context": ["The ship reached the harbor."],
    }
