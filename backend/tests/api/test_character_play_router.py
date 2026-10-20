from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.api.dependencies import get_character_driven_scene_creation_service
from app.exceptions import ActiveSceneExistsError, InvalidModelError, NotFoundError
from app.main import app
from tests.factories import make_creation_service

_STORY_ID = "8fa93a9e-8dad-4fcb-b9cf-8e39f1707ec8"
_URL = f"/api/stories/{_STORY_ID}/character-play/scenes"

_VALID_PAYLOAD = {
    "user_character_id": None,
    "character_ids": ["navigator", "harbor_guard"],
    "context": ["The ship has reached the harbor."],
    "general_scene_guide": "Keep tension rising.",
    "writing_style": "Cinematic and concise.",
    "first_message": "A bell rings through the fog.",
    "character_model_id": "character-model",
    "narrator_model_id": "narrator-model",
}


# --- POST /character-play/scenes ---


def test_create_scene_success():
    svc = make_creation_service()
    app.dependency_overrides[get_character_driven_scene_creation_service] = lambda: svc

    resp = TestClient(app).post(_URL, json=_VALID_PAYLOAD)

    assert resp.status_code == 201
    assert resp.json() == {"data": {"id": 3, "finished": False}}
    svc.create.assert_awaited_once_with(
        story_id=_STORY_ID,
        user_character_id=None,
        character_ids=["navigator", "harbor_guard"],
        context=["The ship has reached the harbor."],
        general_scene_guide="Keep tension rising.",
        writing_style="Cinematic and concise.",
        first_message="A bell rings through the fog.",
        character_model_id="character-model",
        narrator_model_id="narrator-model",
    )


@pytest.mark.parametrize(
    "exc,status,code",
    [
        (NotFoundError("Character 'x' not found"), 404, "not_found"),
        (ActiveSceneExistsError(), 409, "active_scene_exists"),
        (InvalidModelError(), 422, "validation_error"),
    ],
)
def test_create_scene_domain_errors(exc, status, code):
    svc = make_creation_service(side_effect=exc)
    app.dependency_overrides[get_character_driven_scene_creation_service] = lambda: svc

    resp = TestClient(app).post(_URL, json=_VALID_PAYLOAD)

    assert resp.status_code == status
    assert resp.json() == {"error": {"code": code, "message": exc.message}}


@pytest.mark.parametrize(
    "override",
    [
        {"character_ids": ["navigator", "navigator"]},
        {"user_character_id": "navigator"},
        {"context": []},
        {"context": [""]},
        {"general_scene_guide": ""},
        {"writing_style": ""},
        {"first_message": ""},
        {"first_message": "x" * 4001},
        {"character_model_id": ""},
        {"narrator_model_id": ""},
    ],
)
def test_create_scene_invalid_payload(override):
    svc = make_creation_service()
    app.dependency_overrides[get_character_driven_scene_creation_service] = lambda: svc

    resp = TestClient(app).post(_URL, json={**_VALID_PAYLOAD, **override})

    assert resp.status_code == 422
    assert resp.json()["error"]["code"] == "validation_error"
    svc.create.assert_not_awaited()


def test_create_scene_missing_model_id():
    svc = make_creation_service()
    app.dependency_overrides[get_character_driven_scene_creation_service] = lambda: svc
    payload = {k: v for k, v in _VALID_PAYLOAD.items() if k != "narrator_model_id"}

    resp = TestClient(app).post(_URL, json=payload)

    assert resp.status_code == 422
