import pytest
from pydantic import ValidationError
from app.models.api import RegenerateData, RegenerateResponse, MessageModel, StoryDetail, SceneListItem, StoryListItem


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


def test_story_detail_includes_user_character_id():
    detail = StoryDetail(
        id="8fa93a9e-8dad-4fcb-b9cf-8e39f1707ec8",
        title="Mila and Bun",
        user_character_id="max",
        scenes=[SceneListItem(id=1, finished=True)],
        active_scene_id=1,
    )
    assert detail.user_character_id == "max"


def test_story_detail_missing_user_character_id_raises():
    with pytest.raises(ValidationError):
        StoryDetail(
            id="abc",
            title="Test",
            scenes=[],
            active_scene_id=1,
        )
