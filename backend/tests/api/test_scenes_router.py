from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi.testclient import TestClient

from app.api.dependencies import (
    get_scene_creation_service,
    get_scene_lifecycle_service,
    get_scene_message_service,
    get_scene_play_service,
    get_scene_summarize_service,
)
from app.exceptions import ActiveSceneExistsError, NoAssistantMessageError, NoUserMessageError, NotFoundError, SceneFinishedError, LLMError
from app.main import app
from app.models.domain import Message, SceneRef

_STORY_ID = "8fa93a9e-8dad-4fcb-b9cf-8e39f1707ec8"
_SCENE_ID = 1

_USER_MSG = Message(id=1, role="user", content="Hello")
_ASSISTANT_MSG = Message(id=2, role="assistant", content="Hi there!")


def _make_play_service(
    play_side_effect: Exception | None = None,
    play_return: tuple | None = None,
    regen_side_effect: Exception | None = None,
    regen_return: Message | None = None,
) -> MagicMock:
    svc = MagicMock()
    if play_side_effect is not None:
        svc.play = AsyncMock(side_effect=play_side_effect)
    else:
        svc.play = AsyncMock(return_value=play_return or (_USER_MSG, _ASSISTANT_MSG))
    if regen_side_effect is not None:
        svc.regenerate = AsyncMock(side_effect=regen_side_effect)
    else:
        svc.regenerate = AsyncMock(return_value=regen_return or _ASSISTANT_MSG)
    return svc


def _make_message_service(
    edit_side_effect: Exception | None = None,
    delete_side_effect: Exception | None = None,
) -> MagicMock:
    svc = MagicMock()
    if edit_side_effect is not None:
        svc.edit_message = AsyncMock(side_effect=edit_side_effect)
    else:
        svc.edit_message = AsyncMock(return_value=_USER_MSG)
    if delete_side_effect is not None:
        svc.delete_message = AsyncMock(side_effect=delete_side_effect)
    else:
        svc.delete_message = AsyncMock(return_value=None)
    return svc


def _make_lifecycle_service(
    finish_side_effect: Exception | None = None,
) -> MagicMock:
    svc = MagicMock()
    if finish_side_effect is not None:
        svc.finish_scene = AsyncMock(side_effect=finish_side_effect)
    else:
        svc.finish_scene = AsyncMock(return_value=None)
    return svc


# ---------------------------------------------------------------------------
# POST /api/stories/{story_id}/scenes/{scene_id}/play
# ---------------------------------------------------------------------------


class TestPlay:
    def test_scene_finished_returns_409(self):
        svc = _make_play_service(play_side_effect=SceneFinishedError())
        app.dependency_overrides[get_scene_play_service] = lambda: svc

        with TestClient(app) as client:
            resp = client.post(
                f"/api/stories/{_STORY_ID}/scenes/{_SCENE_ID}/play",
                json={"content": "Hello"},
            )

        app.dependency_overrides.clear()

        assert resp.status_code == 409
        assert resp.json()["error"]["code"] == "scene_finished"

    def test_not_found_returns_404(self):
        svc = _make_play_service(play_side_effect=NotFoundError("scene"))
        app.dependency_overrides[get_scene_play_service] = lambda: svc

        with TestClient(app) as client:
            resp = client.post(
                f"/api/stories/{_STORY_ID}/scenes/{_SCENE_ID}/play",
                json={"content": "Hello"},
            )

        app.dependency_overrides.clear()

        assert resp.status_code == 404
        assert resp.json()["error"]["code"] == "not_found"

    def test_llm_error_returns_502(self):
        """An LLMError from the client layer must return 502, not 409."""
        svc = _make_play_service(play_side_effect=LLMError("some llm error"))
        app.dependency_overrides[get_scene_play_service] = lambda: svc

        with TestClient(app) as client:
            resp = client.post(
                f"/api/stories/{_STORY_ID}/scenes/{_SCENE_ID}/play",
                json={"content": "Hello"},
            )

        app.dependency_overrides.clear()

        assert resp.status_code == 502
        assert resp.json()["error"]["code"] == "llm_error"

    def test_success_returns_200(self):
        svc = _make_play_service()
        app.dependency_overrides[get_scene_play_service] = lambda: svc

        with TestClient(app) as client:
            resp = client.post(
                f"/api/stories/{_STORY_ID}/scenes/{_SCENE_ID}/play",
                json={"content": "Hello"},
            )

        app.dependency_overrides.clear()

        assert resp.status_code == 200
        data = resp.json()["data"]
        assert data["user_message"]["role"] == "user"
        assert data["assistant_message"]["role"] == "assistant"


# ---------------------------------------------------------------------------
# PUT /api/stories/{story_id}/scenes/{scene_id}/messages/{message_id}
# ---------------------------------------------------------------------------


class TestEditMessage:
    def test_scene_finished_returns_409(self):
        svc = _make_message_service(edit_side_effect=SceneFinishedError())
        app.dependency_overrides[get_scene_message_service] = lambda: svc

        with TestClient(app) as client:
            resp = client.put(
                f"/api/stories/{_STORY_ID}/scenes/{_SCENE_ID}/messages/1",
                json={"content": "Updated"},
            )

        app.dependency_overrides.clear()

        assert resp.status_code == 409
        assert resp.json()["error"]["code"] == "scene_finished"


# ---------------------------------------------------------------------------
# DELETE /api/stories/{story_id}/scenes/{scene_id}/messages/{message_id}
# ---------------------------------------------------------------------------


class TestDeleteMessage:
    def test_scene_finished_returns_409(self):
        svc = _make_message_service(delete_side_effect=SceneFinishedError())
        app.dependency_overrides[get_scene_message_service] = lambda: svc

        with TestClient(app) as client:
            resp = client.delete(
                f"/api/stories/{_STORY_ID}/scenes/{_SCENE_ID}/messages/1",
            )

        app.dependency_overrides.clear()

        assert resp.status_code == 409
        assert resp.json()["error"]["code"] == "scene_finished"


# ---------------------------------------------------------------------------
# POST /api/stories/{story_id}/scenes/{scene_id}/finish
# ---------------------------------------------------------------------------


class TestFinishScene:
    def test_scene_finished_returns_409(self):
        svc = _make_lifecycle_service(finish_side_effect=SceneFinishedError())
        app.dependency_overrides[get_scene_lifecycle_service] = lambda: svc

        with TestClient(app) as client:
            resp = client.post(
                f"/api/stories/{_STORY_ID}/scenes/{_SCENE_ID}/finish",
                json={"scene_summary": ["The hero won."]},
            )

        app.dependency_overrides.clear()

        assert resp.status_code == 409
        assert resp.json()["error"]["code"] == "scene_finished"

    def test_plain_string_summary_returns_422(self):
        svc = _make_lifecycle_service()
        app.dependency_overrides[get_scene_lifecycle_service] = lambda: svc

        with TestClient(app) as client:
            resp = client.post(
                f"/api/stories/{_STORY_ID}/scenes/{_SCENE_ID}/finish",
                json={"scene_summary": "The hero won."},
            )

        app.dependency_overrides.clear()

        assert resp.status_code == 422

    def test_finish_scene_calls_service_with_summary_list(self):
        svc = _make_lifecycle_service()
        app.dependency_overrides[get_scene_lifecycle_service] = lambda: svc

        with TestClient(app) as client:
            client.post(
                f"/api/stories/{_STORY_ID}/scenes/{_SCENE_ID}/finish",
                json={"scene_summary": ["The hero won."]},
            )

        app.dependency_overrides.clear()

        svc.finish_scene.assert_awaited_once_with(_STORY_ID, _SCENE_ID, ["The hero won."])


# ---------------------------------------------------------------------------
# POST /api/stories/{story_id}/scenes/{scene_id}/regenerate
# ---------------------------------------------------------------------------


class TestRegenerate:
    def test_scene_finished_returns_409(self):
        svc = _make_play_service(regen_side_effect=SceneFinishedError())
        app.dependency_overrides[get_scene_play_service] = lambda: svc

        with TestClient(app) as client:
            resp = client.post(
                f"/api/stories/{_STORY_ID}/scenes/{_SCENE_ID}/regenerate",
            )

        app.dependency_overrides.clear()

        assert resp.status_code == 409
        assert resp.json()["error"]["code"] == "scene_finished"

    def test_no_assistant_message_returns_409(self):
        svc = _make_play_service(regen_side_effect=NoAssistantMessageError())
        app.dependency_overrides[get_scene_play_service] = lambda: svc

        with TestClient(app) as client:
            resp = client.post(
                f"/api/stories/{_STORY_ID}/scenes/{_SCENE_ID}/regenerate",
            )

        app.dependency_overrides.clear()

        assert resp.status_code == 409
        assert resp.json()["error"]["code"] == "no_assistant_message"

    def test_no_user_message_returns_409(self):
        svc = _make_play_service(regen_side_effect=NoUserMessageError())
        app.dependency_overrides[get_scene_play_service] = lambda: svc

        with TestClient(app) as client:
            resp = client.post(
                f"/api/stories/{_STORY_ID}/scenes/{_SCENE_ID}/regenerate",
            )

        app.dependency_overrides.clear()

        assert resp.status_code == 409
        assert resp.json()["error"]["code"] == "no_user_message"

    def test_llm_error_returns_502(self):
        svc = _make_play_service(regen_side_effect=LLMError("boom"))
        app.dependency_overrides[get_scene_play_service] = lambda: svc

        with TestClient(app) as client:
            resp = client.post(
                f"/api/stories/{_STORY_ID}/scenes/{_SCENE_ID}/regenerate",
            )

        app.dependency_overrides.clear()

        assert resp.status_code == 502
        assert resp.json()["error"]["code"] == "llm_error"


# ---------------------------------------------------------------------------
# GET /api/stories/{story_id}/scenes/{scene_id}/summarize
# ---------------------------------------------------------------------------


def _make_summarize_service(
    side_effect: Exception | None = None,
    return_value: list[str] | None = None,
) -> MagicMock:
    svc = MagicMock()
    if side_effect is not None:
        svc.summarize = AsyncMock(side_effect=side_effect)
    else:
        svc.summarize = AsyncMock(return_value=return_value or ["Item one", "Item two"])
    return svc


class TestSummarizeScene:
    def test_success_returns_200(self):
        svc = _make_summarize_service()
        app.dependency_overrides[get_scene_summarize_service] = lambda: svc

        with TestClient(app) as client:
            resp = client.get(
                f"/api/stories/{_STORY_ID}/scenes/{_SCENE_ID}/summarize",
            )

        app.dependency_overrides.clear()

        assert resp.status_code == 200
        assert resp.json() == {"data": {"summary": ["Item one", "Item two"]}}

    def test_not_found_returns_404(self):
        svc = _make_summarize_service(side_effect=NotFoundError("scene"))
        app.dependency_overrides[get_scene_summarize_service] = lambda: svc

        with TestClient(app) as client:
            resp = client.get(
                f"/api/stories/{_STORY_ID}/scenes/{_SCENE_ID}/summarize",
            )

        app.dependency_overrides.clear()

        assert resp.status_code == 404
        assert resp.json()["error"]["code"] == "not_found"

    def test_scene_finished_returns_409(self):
        svc = _make_summarize_service(side_effect=SceneFinishedError())
        app.dependency_overrides[get_scene_summarize_service] = lambda: svc

        with TestClient(app) as client:
            resp = client.get(
                f"/api/stories/{_STORY_ID}/scenes/{_SCENE_ID}/summarize",
            )

        app.dependency_overrides.clear()

        assert resp.status_code == 409
        assert resp.json()["error"]["code"] == "scene_finished"

    def test_llm_error_returns_502(self):
        svc = _make_summarize_service(side_effect=LLMError("boom"))
        app.dependency_overrides[get_scene_summarize_service] = lambda: svc

        with TestClient(app) as client:
            resp = client.get(
                f"/api/stories/{_STORY_ID}/scenes/{_SCENE_ID}/summarize",
            )

        app.dependency_overrides.clear()

        assert resp.status_code == 502
        assert resp.json()["error"]["code"] == "llm_error"


# ---------------------------------------------------------------------------
# POST /api/stories/{story_id}/scenes
# ---------------------------------------------------------------------------

_VALID_CREATE_PAYLOAD = {
    "user_character_id": "hero",
    "character_ids": ["villain"],
    "context": ["Previously in the story..."],
    "general_scene_guide": "Build tension.",
    "writing_style": "Cinematic.",
    "first_message": "You enter a dark corridor.",
}


def _make_creation_service(
    side_effect: Exception | None = None,
    return_value: SceneRef | None = None,
) -> MagicMock:
    svc = MagicMock()
    if side_effect is not None:
        svc.create = AsyncMock(side_effect=side_effect)
    else:
        svc.create = AsyncMock(return_value=return_value or SceneRef(id=3, finished=False))
    return svc


class TestCreateScene:
    def test_success_returns_201(self):
        svc = _make_creation_service()
        app.dependency_overrides[get_scene_creation_service] = lambda: svc

        with TestClient(app) as client:
            resp = client.post(
                f"/api/stories/{_STORY_ID}/scenes",
                json=_VALID_CREATE_PAYLOAD,
            )

        app.dependency_overrides.clear()

        assert resp.status_code == 201
        data = resp.json()["data"]
        assert data["id"] == 3
        assert data["finished"] is False

    def test_not_found_returns_404(self):
        svc = _make_creation_service(side_effect=NotFoundError("Story not found"))
        app.dependency_overrides[get_scene_creation_service] = lambda: svc

        with TestClient(app) as client:
            resp = client.post(
                f"/api/stories/{_STORY_ID}/scenes",
                json=_VALID_CREATE_PAYLOAD,
            )

        app.dependency_overrides.clear()

        assert resp.status_code == 404
        assert resp.json()["error"]["code"] == "not_found"

    def test_active_scene_exists_returns_409(self):
        svc = _make_creation_service(side_effect=ActiveSceneExistsError())
        app.dependency_overrides[get_scene_creation_service] = lambda: svc

        with TestClient(app) as client:
            resp = client.post(
                f"/api/stories/{_STORY_ID}/scenes",
                json=_VALID_CREATE_PAYLOAD,
            )

        app.dependency_overrides.clear()

        assert resp.status_code == 409
        assert resp.json()["error"]["code"] == "active_scene_exists"

    def test_user_character_id_in_character_ids_returns_422(self):
        svc = _make_creation_service()
        app.dependency_overrides[get_scene_creation_service] = lambda: svc

        with TestClient(app) as client:
            resp = client.post(
                f"/api/stories/{_STORY_ID}/scenes",
                json={
                    **_VALID_CREATE_PAYLOAD,
                    "character_ids": ["hero"],  # same as user_character_id
                },
            )

        app.dependency_overrides.clear()

        assert resp.status_code == 422
        assert resp.json()["error"]["code"] == "validation_error"
