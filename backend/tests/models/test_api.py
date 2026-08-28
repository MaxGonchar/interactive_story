from __future__ import annotations

import pytest
from pydantic import ValidationError
from app.models.api import (
    CreateSceneRequest,
    CreateSceneResponse,
    FinishSceneRequest,
    MessageModel,
    RegenerateData,
    RegenerateResponse,
    SceneListItem,
    StoryDetail,
    StoryListItem,
)


def test_story_list_item_has_type_field():
    item = StoryListItem(id="abc", title="Test", type="scene")
    assert item.type == "scene"


def test_story_list_item_type_choice_driven():
    item = StoryListItem(id="abc", title="Test", type="choice_driven")
    assert item.type == "choice_driven"


def test_regenerate_response_validates():
    msg = MessageModel(id=1, role="assistant", content="x")
    data = RegenerateData(assistant_message=msg)
    resp = RegenerateResponse(data=data)
    assert resp.data.assistant_message.id == 1
    assert resp.data.assistant_message.role == "assistant"
    assert resp.data.assistant_message.content == "x"


def test_story_detail_fields():
    detail = StoryDetail(
        id="8fa93a9e-8dad-4fcb-b9cf-8e39f1707ec8",
        title="Mila and Bun",
        scenes=[SceneListItem(id=1, finished=True)],
        active_scene_id=1,
    )
    assert detail.id == "8fa93a9e-8dad-4fcb-b9cf-8e39f1707ec8"
    assert detail.title == "Mila and Bun"


def test_story_detail_active_scene_id_none():
    detail = StoryDetail(
        id="8fa93a9e-8dad-4fcb-b9cf-8e39f1707ec8",
        title="Mila and Bun",
        scenes=[SceneListItem(id=1, finished=True)],
        active_scene_id=None,
    )
    assert detail.active_scene_id is None


# ---------------------------------------------------------------------------
# FinishSceneRequest
# ---------------------------------------------------------------------------


def test_finish_scene_request_valid_list():
    req = FinishSceneRequest(scene_summary=["The hero won.", "The map was found."])
    assert req.scene_summary == ["The hero won.", "The map was found."]


def test_finish_scene_request_single_item_valid():
    req = FinishSceneRequest(scene_summary=["The hero won."])
    assert len(req.scene_summary) == 1


def test_finish_scene_request_empty_list_rejected():
    with pytest.raises(ValidationError):
        FinishSceneRequest(scene_summary=[])


def test_finish_scene_request_list_over_100_rejected():
    with pytest.raises(ValidationError):
        FinishSceneRequest(scene_summary=["item"] * 101)


def test_finish_scene_request_plain_string_rejected():
    with pytest.raises(ValidationError):
        FinishSceneRequest(scene_summary="The hero won.")


def test_finish_scene_request_empty_string_item_rejected():
    with pytest.raises(ValidationError):
        FinishSceneRequest(scene_summary=[""])


# ---------------------------------------------------------------------------
# CreateSceneRequest
# ---------------------------------------------------------------------------

VALID_CREATE_SCENE = dict(
    user_character_id="char-1",
    character_ids=["char-2", "char-3"],
    context=["It was a dark night."],
    general_scene_guide="A tense encounter",
    writing_style="noir",
    first_message="Hello, stranger.",
)


def test_create_scene_request_valid():
    req = CreateSceneRequest(**VALID_CREATE_SCENE)
    assert req.user_character_id == "char-1"
    assert req.character_ids == ["char-2", "char-3"]
    assert req.context == ["It was a dark night."]


def test_create_scene_request_accepts_null_user_character_id():
    req = CreateSceneRequest(**{**VALID_CREATE_SCENE, "user_character_id": None})

    assert req.user_character_id is None


def test_create_scene_request_character_ids_defaults_to_empty():
    req = CreateSceneRequest(
        user_character_id="char-1",
        context=["Context."],
        general_scene_guide="Guide",
        writing_style="style",
        first_message="Hello",
    )
    assert req.character_ids == []


def test_create_scene_request_user_character_id_in_character_ids_rejected():
    with pytest.raises(ValidationError):
        CreateSceneRequest(
            user_character_id="char-1",
            character_ids=["char-1", "char-2"],
            context=["Context."],
            general_scene_guide="Guide",
            writing_style="style",
            first_message="Hello",
        )


def test_create_scene_request_null_user_character_id_skips_membership_validation():
    req = CreateSceneRequest(
        user_character_id=None,
        character_ids=["char-1", "char-2"],
        context=["Context."],
        general_scene_guide="Guide",
        writing_style="style",
        first_message="Hello",
    )

    assert req.character_ids == ["char-1", "char-2"]


def test_create_scene_request_missing_user_character_id_rejected():
    with pytest.raises(ValidationError):
        CreateSceneRequest(
            context=["Context."],
            general_scene_guide="Guide",
            writing_style="style",
            first_message="Hello",
        )


def test_create_scene_request_missing_context_rejected():
    with pytest.raises(ValidationError):
        CreateSceneRequest(
            user_character_id="char-1",
            general_scene_guide="Guide",
            writing_style="style",
            first_message="Hello",
        )


def test_create_scene_request_empty_context_rejected():
    with pytest.raises(ValidationError):
        CreateSceneRequest(
            user_character_id="char-1",
            context=[],
            general_scene_guide="Guide",
            writing_style="style",
            first_message="Hello",
        )


def test_create_scene_request_missing_general_scene_guide_rejected():
    with pytest.raises(ValidationError):
        CreateSceneRequest(
            user_character_id="char-1",
            context=["Context."],
            writing_style="style",
            first_message="Hello",
        )


def test_create_scene_request_missing_writing_style_rejected():
    with pytest.raises(ValidationError):
        CreateSceneRequest(
            user_character_id="char-1",
            context=["Context."],
            general_scene_guide="Guide",
            first_message="Hello",
        )


def test_create_scene_request_missing_first_message_rejected():
    with pytest.raises(ValidationError):
        CreateSceneRequest(
            user_character_id="char-1",
            context=["Context."],
            general_scene_guide="Guide",
            writing_style="style",
        )


def test_create_scene_response_wraps_scene_list_item():
    resp = CreateSceneResponse(data=SceneListItem(id=1, finished=False))
    assert resp.data.id == 1
    assert resp.data.finished is False
