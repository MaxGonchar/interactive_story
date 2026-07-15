from unittest.mock import AsyncMock

import pytest

from app.exceptions import ActiveSceneExistsError, NotFoundError
from app.models.domain import SceneDescription, SceneMetadata, SceneRef, StoryMeta
from app.services.scene_creation_service import SceneCreationService


STORY_ID = "story-abc"
FIRST_MESSAGE = "You enter a dark corridor."

_BASE_KWARGS = dict(
    story_id=STORY_ID,
    user_character_id="hero",
    character_ids=["villain"],
    context=["Previously..."],
    general_scene_guide="Build tension.",
    writing_style="Cinematic.",
    first_message=FIRST_MESSAGE,
)


def make_story_meta(scenes: list[SceneRef]) -> StoryMeta:
    return StoryMeta(id=STORY_ID, title="Test Story", scenes=scenes, active_scene_id=None)


def make_service(
    story_meta: StoryMeta | None = None,
    story_side_effect: Exception | None = None,
) -> tuple[SceneCreationService, AsyncMock, AsyncMock]:
    story_repo = AsyncMock()
    scene_repo = AsyncMock()

    if story_side_effect is not None:
        story_repo.get_story = AsyncMock(side_effect=story_side_effect)
    else:
        story_repo.get_story = AsyncMock(return_value=story_meta or make_story_meta([]))

    service = SceneCreationService(story_repo, scene_repo)
    return service, story_repo, scene_repo


# ---------------------------------------------------------------------------
# Happy path
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_create_returns_scene_ref_with_next_id():
    existing = [SceneRef(id=1, finished=True), SceneRef(id=2, finished=True)]
    service, _, _ = make_service(story_meta=make_story_meta(existing))

    result = await service.create(**_BASE_KWARGS)

    assert result.id == 3
    assert result.finished is False


@pytest.mark.asyncio
async def test_create_returns_id_1_when_no_scenes_exist():
    service, _, _ = make_service(story_meta=make_story_meta([]))

    result = await service.create(**_BASE_KWARGS)

    assert result.id == 1


@pytest.mark.asyncio
async def test_create_calls_scene_repo_create_scene():
    existing = [SceneRef(id=1, finished=True)]
    service, _, scene_repo = make_service(story_meta=make_story_meta(existing))

    result = await service.create(**_BASE_KWARGS)

    scene_repo.create_scene.assert_awaited_once()
    call_args = scene_repo.create_scene.call_args
    assert call_args.args[0] == STORY_ID      # story_id
    assert call_args.args[1] == 2             # next scene_id
    metadata: SceneMetadata = call_args.args[2]
    assert metadata.finished is False
    assert metadata.user_character_id == "hero"
    assert metadata.character_ids == ["villain"]
    assert metadata.context == ["Previously..."]
    assert metadata.scene_description.general_scene_guide == "Build tension."
    first_msg = call_args.args[3]
    assert first_msg.id == 1
    assert first_msg.role == "assistant"
    assert first_msg.content == FIRST_MESSAGE


# ---------------------------------------------------------------------------
# Error cases
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_create_raises_not_found_when_story_missing():
    service, _, _ = make_service(story_side_effect=NotFoundError("Story 'x' not found"))

    with pytest.raises(NotFoundError):
        await service.create(**_BASE_KWARGS)


@pytest.mark.asyncio
async def test_create_raises_active_scene_exists_when_unfinished_scene_present():
    existing = [SceneRef(id=1, finished=True), SceneRef(id=2, finished=False)]
    service, _, scene_repo = make_service(story_meta=make_story_meta(existing))

    with pytest.raises(ActiveSceneExistsError):
        await service.create(**_BASE_KWARGS)

    scene_repo.create_scene.assert_not_awaited()
