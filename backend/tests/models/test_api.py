import pytest
from pydantic import ValidationError
from app.models.api import FinishSceneRequest, RegenerateData, RegenerateResponse, MessageModel, StoryDetail, SceneListItem, StoryListItem


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
