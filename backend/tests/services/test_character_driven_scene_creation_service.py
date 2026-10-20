from __future__ import annotations

from unittest.mock import AsyncMock

import pytest

from app.exceptions import ActiveSceneExistsError, InvalidModelError, NotFoundError
from app.models.domain import (
    CharacterDrivenLLMData,
    CharacterDrivenMessage,
    ModelMetadata,
    ModelRegistry,
    SceneDescription,
    SceneMetadata,
    SceneRef,
    StoryMeta,
)
from app.services.character_driven_scene_creation_service import (
    CharacterDrivenSceneCreationService,
)
from app.services.model_registry_service import ModelRegistryService

STORY_ID = "story-abc"

_BASE_KWARGS = dict(
    story_id=STORY_ID,
    user_character_id="hero",
    character_ids=["villain"],
    context=["Previously..."],
    general_scene_guide="Build tension.",
    writing_style="Cinematic.",
    first_message="A bell rings.",
    character_model_id="model-a",
    narrator_model_id="model-b",
)


def make_story_meta(scenes: list[SceneRef]) -> StoryMeta:
    return StoryMeta(
        id=STORY_ID,
        title="Test Story",
        scenes=scenes,
        active_scene_id=None,
        type="character_driven",
    )


def make_service(
    scenes: list[SceneRef] | None = None,
) -> tuple[CharacterDrivenSceneCreationService, AsyncMock]:
    story_repo = AsyncMock()
    story_repo.get_story.return_value = make_story_meta(scenes or [])
    scene_repo = AsyncMock()
    registry_repo = AsyncMock()
    registry_repo.get_registry.return_value = ModelRegistry(
        models={
            "model-a": ModelMetadata(id="model-a", name="A", provider_model_id="pa"),
            "model-b": ModelMetadata(id="model-b", name="B", provider_model_id="pb"),
        },
        default_model_id="model-a",
    )
    service = CharacterDrivenSceneCreationService(
        story_repo, scene_repo, ModelRegistryService(registry_repo)
    )
    return service, scene_repo


@pytest.mark.asyncio
async def test_create_persists_scene_and_opening_item():
    service, scene_repo = make_service(
        [SceneRef(id=1, finished=True), SceneRef(id=2, finished=True)]
    )

    result = await service.create(**_BASE_KWARGS)

    assert result == SceneRef(id=3, finished=False)
    scene_repo.create_scene.assert_awaited_once_with(
        STORY_ID,
        3,
        SceneMetadata(
            id=3,
            story_id=STORY_ID,
            character_ids=["villain"],
            user_character_id="hero",
            finished=False,
            scene_description=SceneDescription(
                general_scene_guide="Build tension.", writing_style="Cinematic."
            ),
            context=["Previously..."],
        ),
        CharacterDrivenMessage(
            id=1,
            narration="A bell rings.",
            llm_data=CharacterDrivenLLMData(
                character_model_id="model-a", narrator_model_id="model-b"
            ),
        ),
    )


@pytest.mark.asyncio
async def test_create_accepts_null_user_character():
    service, scene_repo = make_service()

    result = await service.create(**{**_BASE_KWARGS, "user_character_id": None})

    assert result == SceneRef(id=1, finished=False)
    scene_repo.create_scene.assert_awaited_once()


@pytest.mark.asyncio
@pytest.mark.parametrize("field", ["character_model_id", "narrator_model_id"])
async def test_create_rejects_unknown_model(field):
    service, scene_repo = make_service()

    with pytest.raises(InvalidModelError):
        await service.create(**{**_BASE_KWARGS, field: "unknown"})

    scene_repo.create_scene.assert_not_awaited()


@pytest.mark.asyncio
async def test_create_rejects_when_active_scene_exists():
    service, scene_repo = make_service([SceneRef(id=1, finished=False)])

    with pytest.raises(ActiveSceneExistsError):
        await service.create(**_BASE_KWARGS)

    scene_repo.create_scene.assert_not_awaited()


@pytest.mark.asyncio
async def test_create_propagates_unknown_character():
    service, scene_repo = make_service()
    scene_repo.create_scene.side_effect = NotFoundError("Character 'x' not found")

    with pytest.raises(NotFoundError):
        await service.create(**_BASE_KWARGS)
