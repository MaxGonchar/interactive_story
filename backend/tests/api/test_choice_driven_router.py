from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.api.dependencies import get_choice_driven_play_service
from app.exceptions import NoStepsError, NotFoundError
from app.main import app
from tests.factories import make_choice_driven_service

_STORY_ID = "8fa93a9e-8dad-4fcb-b9cf-8e39f1707ec8"
_MISSING_ID = "00000000-0000-0000-0000-000000000000"


# ---------------------------------------------------------------------------
# GET /api/stories/{story_id}/choice-play
# ---------------------------------------------------------------------------


def test_get_choice_play_success():
    svc = make_choice_driven_service()
    app.dependency_overrides[get_choice_driven_play_service] = lambda: svc

    client = TestClient(app)
    resp = client.get(f"/api/stories/{_STORY_ID}/choice-play")

    assert resp.status_code == 200
    assert resp.json() == {
        "data": {
            "id": _STORY_ID,
            "title": "The Black Harbor",
            "steps": [
                {
                    "id": 1,
                    "incoming_choice": None,
                    "text": "The fog rolled in.",
                    "choices": [
                        {"action": "Go left", "consequence": "Find a shortcut"},
                        {"action": "Go right", "consequence": "Meet a stranger"},
                    ],
                },
                {
                    "id": 2,
                    "incoming_choice": {"action": "Go left", "consequence": "Find a shortcut"},
                    "text": "A shortcut appeared.",
                    "choices": [],
                },
            ],
        }
    }


def test_get_choice_play_not_found():
    svc = make_choice_driven_service(story_not_found=True)
    app.dependency_overrides[get_choice_driven_play_service] = lambda: svc

    client = TestClient(app)
    resp = client.get(f"/api/stories/{_MISSING_ID}/choice-play")

    assert resp.status_code == 404
    assert resp.json()["error"]["code"] == "not_found"


# ---------------------------------------------------------------------------
# POST /api/stories/{story_id}/choice-play/generate-choices
# ---------------------------------------------------------------------------


def test_generate_choices_success():
    svc = make_choice_driven_service()
    app.dependency_overrides[get_choice_driven_play_service] = lambda: svc

    client = TestClient(app)
    resp = client.post(f"/api/stories/{_STORY_ID}/choice-play/generate-choices")

    assert resp.status_code == 200
    assert resp.json() == {
        "data": {
            "choices": [
                {"action": "Go left", "consequence": "Find a shortcut"},
                {"action": "Go right", "consequence": "Meet a stranger"},
            ]
        }
    }


@pytest.mark.parametrize("exc,status,code", [
    (NotFoundError(_MISSING_ID), 404, "not_found"),
    (NoStepsError(), 409, "no_steps"),
])
def test_generate_choices_error(exc, status, code):
    svc = make_choice_driven_service(generate_choices_side_effect=exc)
    app.dependency_overrides[get_choice_driven_play_service] = lambda: svc

    client = TestClient(app)
    resp = client.post(f"/api/stories/{_STORY_ID}/choice-play/generate-choices")

    assert resp.status_code == status
    assert resp.json()["error"]["code"] == code


# ---------------------------------------------------------------------------
# POST /api/stories/{story_id}/choice-play/regenerate-choices
# ---------------------------------------------------------------------------


def test_regenerate_choices_success():
    svc = make_choice_driven_service()
    app.dependency_overrides[get_choice_driven_play_service] = lambda: svc

    client = TestClient(app)
    resp = client.post(f"/api/stories/{_STORY_ID}/choice-play/regenerate-choices")

    assert resp.status_code == 200
    assert resp.json() == {
        "data": {
            "choices": [
                {"action": "Go left", "consequence": "Find a shortcut"},
                {"action": "Go right", "consequence": "Meet a stranger"},
            ]
        }
    }


@pytest.mark.parametrize("exc,status,code", [
    (NotFoundError(_MISSING_ID), 404, "not_found"),
    (NoStepsError(), 409, "no_steps"),
])
def test_regenerate_choices_error(exc, status, code):
    svc = make_choice_driven_service(regenerate_choices_side_effect=exc)
    app.dependency_overrides[get_choice_driven_play_service] = lambda: svc

    client = TestClient(app)
    resp = client.post(f"/api/stories/{_STORY_ID}/choice-play/regenerate-choices")

    assert resp.status_code == status
    assert resp.json()["error"]["code"] == code


# ---------------------------------------------------------------------------
# POST /api/stories/{story_id}/choice-play/select-choice
# ---------------------------------------------------------------------------


def test_select_choice_success():
    svc = make_choice_driven_service()
    app.dependency_overrides[get_choice_driven_play_service] = lambda: svc

    client = TestClient(app)
    resp = client.post(
        f"/api/stories/{_STORY_ID}/choice-play/select-choice",
        json={"action": "Go left", "consequence": "Find a shortcut"},
    )

    assert resp.status_code == 200
    assert resp.json() == {
        "data": {
            "id": 2,
            "incoming_choice": {"action": "Go left", "consequence": "Find a shortcut"},
            "text": "A shortcut appeared.",
            "choices": [],
        }
    }


def test_select_choice_not_found():
    svc = make_choice_driven_service(story_not_found=True)
    app.dependency_overrides[get_choice_driven_play_service] = lambda: svc

    client = TestClient(app)
    resp = client.post(
        f"/api/stories/{_MISSING_ID}/choice-play/select-choice",
        json={"action": "Go left", "consequence": "Find a shortcut"},
    )

    assert resp.status_code == 404
    assert resp.json()["error"]["code"] == "not_found"


# ---------------------------------------------------------------------------
# PATCH /api/stories/{story_id}/choice-play/steps/{step_id}
# ---------------------------------------------------------------------------


def test_edit_step_success():
    from app.models.domain import Step
    edited = Step(id=1, incoming_choice=None, text="Corrected text.", choices=[])
    svc = make_choice_driven_service(edited_step=edited)
    app.dependency_overrides[get_choice_driven_play_service] = lambda: svc

    client = TestClient(app)
    resp = client.patch(
        f"/api/stories/{_STORY_ID}/choice-play/steps/1",
        json={"text": "Corrected text."},
    )

    assert resp.status_code == 200
    assert resp.json() == {"data": {"id": 1, "text": "Corrected text."}}


def test_edit_step_not_found():
    svc = make_choice_driven_service(story_not_found=True)
    app.dependency_overrides[get_choice_driven_play_service] = lambda: svc

    client = TestClient(app)
    resp = client.patch(
        f"/api/stories/{_MISSING_ID}/choice-play/steps/1",
        json={"text": "Corrected text."},
    )

    assert resp.status_code == 404
    assert resp.json()["error"]["code"] == "not_found"


# ---------------------------------------------------------------------------
# DELETE /api/stories/{story_id}/choice-play/steps/{step_id}/forward
# ---------------------------------------------------------------------------


def test_return_to_step_success():
    svc = make_choice_driven_service(returned_step_id=1)
    app.dependency_overrides[get_choice_driven_play_service] = lambda: svc

    client = TestClient(app)
    resp = client.delete(f"/api/stories/{_STORY_ID}/choice-play/steps/1/forward")

    assert resp.status_code == 200
    assert resp.json() == {"data": {"step_id": 1}}


def test_return_to_step_not_found():
    svc = make_choice_driven_service(story_not_found=True)
    app.dependency_overrides[get_choice_driven_play_service] = lambda: svc

    client = TestClient(app)
    resp = client.delete(f"/api/stories/{_MISSING_ID}/choice-play/steps/1/forward")

    assert resp.status_code == 404
    assert resp.json()["error"]["code"] == "not_found"
