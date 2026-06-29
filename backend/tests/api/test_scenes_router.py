from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi.testclient import TestClient

from app.api.dependencies import (
    get_scene_lifecycle_service,
    get_scene_message_service,
    get_scene_play_service,
)
from app.exceptions import NoAssistantMessageError, NoUserMessageError, NotFoundError, SceneFinishedError, LLMError
from app.main import app
from app.models.domain import Message

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
                json={"scene_summary": "The hero won."},
            )

        app.dependency_overrides.clear()

        assert resp.status_code == 409
        assert resp.json()["error"]["code"] == "scene_finished"


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
