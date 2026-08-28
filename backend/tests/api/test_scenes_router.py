from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.api.dependencies import (
    get_scene_creation_service,
    get_scene_lifecycle_service,
    get_scene_message_service,
    get_scene_play_service,
    get_scene_query_service,
    get_scene_summarize_service,
)
from app.exceptions import ActiveSceneExistsError, LLMError, NoAssistantMessageError, NoUserMessageError, NotFoundError, SceneFinishedError
from app.main import app
from app.models.domain import SceneDescription, SceneMetadata
from tests.factories import (
    make_creation_service,
    make_lifecycle_service,
    make_message_service,
    make_play_service,
    make_query_service,
    make_summarize_service,
)

_STORY_ID = "8fa93a9e-8dad-4fcb-b9cf-8e39f1707ec8"
_SCENE_ID = 1

_VALID_CREATE_PAYLOAD = {
    "user_character_id": "hero",
    "character_ids": ["villain"],
    "context": ["Previously in the story..."],
    "general_scene_guide": "Build tension.",
    "writing_style": "Cinematic.",
    "first_message": "You enter a dark corridor.",
}

_SCENE_METADATA = SceneMetadata(
    id=_SCENE_ID,
    story_id=_STORY_ID,
    character_ids=["villain"],
    user_character_id="hero",
    finished=False,
    scene_description=SceneDescription(
        general_scene_guide="Keep tension rising.",
        writing_style="Cinematic.",
    ),
    scene_summary=None,
    context=["Previously...", "And then..."],
)


# ---------------------------------------------------------------------------
# POST /api/stories/{story_id}/scenes/{scene_id}/play
# ---------------------------------------------------------------------------


def test_play_success():
    svc = make_play_service()
    app.dependency_overrides[get_scene_play_service] = lambda: svc

    client = TestClient(app)
    resp = client.post(
        f"/api/stories/{_STORY_ID}/scenes/{_SCENE_ID}/play",
        json={"content": "Hello"},
    )

    assert resp.status_code == 200
    assert resp.json() == {
        "data": {
            "user_message": {"id": 1, "role": "user", "content": "Hello"},
            "assistant_message": {"id": 2, "role": "assistant", "content": "Hi there!"},
        }
    }


@pytest.mark.parametrize("exc,status,code", [
    (SceneFinishedError(), 409, "scene_finished"),
    (NotFoundError("scene"), 404, "not_found"),
    (LLMError("boom"), 502, "llm_error"),
])
def test_play_error(exc, status, code):
    svc = make_play_service(play_side_effect=exc)
    app.dependency_overrides[get_scene_play_service] = lambda: svc

    client = TestClient(app)
    resp = client.post(
        f"/api/stories/{_STORY_ID}/scenes/{_SCENE_ID}/play",
        json={"content": "Hello"},
    )

    assert resp.status_code == status
    assert resp.json()["error"]["code"] == code


# ---------------------------------------------------------------------------
# PUT /api/stories/{story_id}/scenes/{scene_id}/messages/{message_id}
# ---------------------------------------------------------------------------


def test_edit_message_success():
    svc = make_message_service()
    app.dependency_overrides[get_scene_message_service] = lambda: svc

    client = TestClient(app)
    resp = client.put(
        f"/api/stories/{_STORY_ID}/scenes/{_SCENE_ID}/messages/1",
        json={"content": "Updated"},
    )

    assert resp.status_code == 200
    assert resp.json() == {"data": {"id": 1, "role": "user", "content": "Hello"}}


def test_edit_message_scene_finished():
    svc = make_message_service(edit_side_effect=SceneFinishedError())
    app.dependency_overrides[get_scene_message_service] = lambda: svc

    client = TestClient(app)
    resp = client.put(
        f"/api/stories/{_STORY_ID}/scenes/{_SCENE_ID}/messages/1",
        json={"content": "Updated"},
    )

    assert resp.status_code == 409
    assert resp.json()["error"]["code"] == "scene_finished"


# ---------------------------------------------------------------------------
# DELETE /api/stories/{story_id}/scenes/{scene_id}/messages/{message_id}
# ---------------------------------------------------------------------------


def test_delete_message_success():
    svc = make_message_service()
    app.dependency_overrides[get_scene_message_service] = lambda: svc

    client = TestClient(app)
    resp = client.delete(f"/api/stories/{_STORY_ID}/scenes/{_SCENE_ID}/messages/1")

    assert resp.status_code == 200
    assert resp.json() == {"success": True}


def test_delete_message_scene_finished():
    svc = make_message_service(delete_side_effect=SceneFinishedError())
    app.dependency_overrides[get_scene_message_service] = lambda: svc

    client = TestClient(app)
    resp = client.delete(f"/api/stories/{_STORY_ID}/scenes/{_SCENE_ID}/messages/1")

    assert resp.status_code == 409
    assert resp.json()["error"]["code"] == "scene_finished"


# ---------------------------------------------------------------------------
# POST /api/stories/{story_id}/scenes/{scene_id}/finish
# ---------------------------------------------------------------------------


def test_finish_scene_success():
    svc = make_lifecycle_service()
    app.dependency_overrides[get_scene_lifecycle_service] = lambda: svc

    client = TestClient(app)
    resp = client.post(
        f"/api/stories/{_STORY_ID}/scenes/{_SCENE_ID}/finish",
        json={"scene_summary": ["The hero won."]},
    )

    assert resp.status_code == 200
    assert resp.json() == {
        "data": {
            "id": _SCENE_ID,
            "finished": True,
            "scene_summary": ["The hero won."],
        }
    }


def test_finish_scene_scene_finished():
    svc = make_lifecycle_service(finish_side_effect=SceneFinishedError())
    app.dependency_overrides[get_scene_lifecycle_service] = lambda: svc

    client = TestClient(app)
    resp = client.post(
        f"/api/stories/{_STORY_ID}/scenes/{_SCENE_ID}/finish",
        json={"scene_summary": ["The hero won."]},
    )

    assert resp.status_code == 409
    assert resp.json()["error"]["code"] == "scene_finished"


def test_finish_scene_plain_string_summary_returns_422():
    svc = make_lifecycle_service()
    app.dependency_overrides[get_scene_lifecycle_service] = lambda: svc

    client = TestClient(app)
    resp = client.post(
        f"/api/stories/{_STORY_ID}/scenes/{_SCENE_ID}/finish",
        json={"scene_summary": "The hero won."},
    )

    assert resp.status_code == 422


def test_finish_scene_calls_service_with_summary_list():
    svc = make_lifecycle_service()
    app.dependency_overrides[get_scene_lifecycle_service] = lambda: svc

    client = TestClient(app)
    client.post(
        f"/api/stories/{_STORY_ID}/scenes/{_SCENE_ID}/finish",
        json={"scene_summary": ["The hero won."]},
    )

    svc.finish_scene.assert_awaited_once_with(_STORY_ID, _SCENE_ID, ["The hero won."])


# ---------------------------------------------------------------------------
# POST /api/stories/{story_id}/scenes/{scene_id}/regenerate
# ---------------------------------------------------------------------------


def test_regenerate_success():
    svc = make_play_service()
    app.dependency_overrides[get_scene_play_service] = lambda: svc

    client = TestClient(app)
    resp = client.post(f"/api/stories/{_STORY_ID}/scenes/{_SCENE_ID}/regenerate")

    assert resp.status_code == 200
    assert resp.json() == {
        "data": {"assistant_message": {"id": 2, "role": "assistant", "content": "Hi there!"}}
    }


@pytest.mark.parametrize("exc,status,code", [
    (SceneFinishedError(), 409, "scene_finished"),
    (NoAssistantMessageError(), 409, "no_assistant_message"),
    (NoUserMessageError(), 409, "no_user_message"),
    (LLMError("boom"), 502, "llm_error"),
])
def test_regenerate_error(exc, status, code):
    svc = make_play_service(regen_side_effect=exc)
    app.dependency_overrides[get_scene_play_service] = lambda: svc

    client = TestClient(app)
    resp = client.post(f"/api/stories/{_STORY_ID}/scenes/{_SCENE_ID}/regenerate")

    assert resp.status_code == status
    assert resp.json()["error"]["code"] == code


# ---------------------------------------------------------------------------
# GET /api/stories/{story_id}/scenes/{scene_id}/summarize
# ---------------------------------------------------------------------------


def test_summarize_scene_success():
    svc = make_summarize_service()
    app.dependency_overrides[get_scene_summarize_service] = lambda: svc

    client = TestClient(app)
    resp = client.get(f"/api/stories/{_STORY_ID}/scenes/{_SCENE_ID}/summarize")

    assert resp.status_code == 200
    assert resp.json() == {"data": {"summary": ["Item one", "Item two"]}}


@pytest.mark.parametrize("exc,status,code", [
    (NotFoundError("scene"), 404, "not_found"),
    (SceneFinishedError(), 409, "scene_finished"),
    (LLMError("boom"), 502, "llm_error"),
])
def test_summarize_scene_error(exc, status, code):
    svc = make_summarize_service(side_effect=exc)
    app.dependency_overrides[get_scene_summarize_service] = lambda: svc

    client = TestClient(app)
    resp = client.get(f"/api/stories/{_STORY_ID}/scenes/{_SCENE_ID}/summarize")

    assert resp.status_code == status
    assert resp.json()["error"]["code"] == code


# ---------------------------------------------------------------------------
# POST /api/stories/{story_id}/scenes
# ---------------------------------------------------------------------------


def test_create_scene_success():
    svc = make_creation_service()
    app.dependency_overrides[get_scene_creation_service] = lambda: svc

    client = TestClient(app)
    resp = client.post(f"/api/stories/{_STORY_ID}/scenes", json=_VALID_CREATE_PAYLOAD)

    assert resp.status_code == 201
    assert resp.json() == {"data": {"id": 3, "finished": False}}


def test_create_scene_accepts_null_user_character_id():
    svc = make_creation_service()
    app.dependency_overrides[get_scene_creation_service] = lambda: svc

    resp = TestClient(app).post(
        f"/api/stories/{_STORY_ID}/scenes",
        json={**_VALID_CREATE_PAYLOAD, "user_character_id": None},
    )

    assert resp.status_code == 201
    assert resp.json() == {"data": {"id": 3, "finished": False}}
    assert svc.create.await_args.kwargs["user_character_id"] is None


@pytest.mark.parametrize("exc,status,code", [
    (NotFoundError("Story not found"), 404, "not_found"),
    (ActiveSceneExistsError(), 409, "active_scene_exists"),
])
def test_create_scene_error(exc, status, code):
    svc = make_creation_service(side_effect=exc)
    app.dependency_overrides[get_scene_creation_service] = lambda: svc

    client = TestClient(app)
    resp = client.post(f"/api/stories/{_STORY_ID}/scenes", json=_VALID_CREATE_PAYLOAD)

    assert resp.status_code == status
    assert resp.json()["error"]["code"] == code


def test_create_scene_user_character_id_in_character_ids_returns_422():
    svc = make_creation_service()
    app.dependency_overrides[get_scene_creation_service] = lambda: svc

    client = TestClient(app)
    resp = client.post(
        f"/api/stories/{_STORY_ID}/scenes",
        json={**_VALID_CREATE_PAYLOAD, "character_ids": ["hero"]},
    )

    assert resp.status_code == 422
    assert resp.json()["error"]["code"] == "validation_error"


# ---------------------------------------------------------------------------
# GET /api/stories/{story_id}/scenes/{scene_id}
# ---------------------------------------------------------------------------


def test_get_scene_success():
    svc = make_query_service(metadata=_SCENE_METADATA)
    app.dependency_overrides[get_scene_query_service] = lambda: svc

    client = TestClient(app)
    resp = client.get(f"/api/stories/{_STORY_ID}/scenes/{_SCENE_ID}")

    assert resp.status_code == 200
    assert resp.json() == {
        "data": {
            "id": _SCENE_ID,
            "finished": False,
            "scene_description": {
                "general_scene_guide": "Keep tension rising.",
                "writing_style": "Cinematic.",
            },
            "scene_summary": None,
            "context": ["Previously...", "And then..."],
            "messages": [{"id": 2, "role": "assistant", "content": "Hi there!"}],
        }
    }


def test_get_scene_success_no_context():
    metadata = _SCENE_METADATA.model_copy(update={"context": None})
    svc = make_query_service(metadata=metadata)
    app.dependency_overrides[get_scene_query_service] = lambda: svc

    client = TestClient(app)
    resp = client.get(f"/api/stories/{_STORY_ID}/scenes/{_SCENE_ID}")

    assert resp.status_code == 200
    assert resp.json()["data"]["context"] is None


def test_get_scene_not_found():
    svc = make_query_service(side_effect=NotFoundError("scene"))
    app.dependency_overrides[get_scene_query_service] = lambda: svc

    client = TestClient(app)
    resp = client.get(f"/api/stories/{_STORY_ID}/scenes/{_SCENE_ID}")

    assert resp.status_code == 404
    assert resp.json()["error"]["code"] == "not_found"
