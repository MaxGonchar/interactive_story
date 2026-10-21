from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi.testclient import TestClient

from app.api.dependencies import (
    get_character_driven_scene_creation_service,
    get_character_driven_scene_query_service,
    get_character_driven_scene_turn_service,
)
from app.exceptions import (
    ActiveSceneExistsError,
    CharacterNotInSceneError,
    InvalidModelError,
    LLMError,
    NotFoundError,
    SceneFinishedError,
)
from app.main import app
from app.models.domain import (
    CharacterDrivenInput,
    CharacterDrivenLLMData,
    CharacterDrivenMessage,
)
from app.api.routers.character_play import map_character_driven_item
from tests.factories import make_creation_service, make_scene_metadata

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

_CHARACTER_TURN_PAYLOAD = {
    "actor": {"type": "character", "character_id": "c1"},
    "guidance": "",
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


# --- Character-driven item mapping ---


def test_map_character_driven_item_maps_player_item():
    metadata = make_scene_metadata()
    message = CharacterDrivenMessage(
        id=2,
        input=CharacterDrivenInput(author="max", action="I search the pier."),
        narration="A lantern swings above the water.",
        llm_data=CharacterDrivenLLMData(
            character_model_id=None, narrator_model_id="narrator-model"
        ),
    )

    item = map_character_driven_item(message, metadata)

    assert item.model_dump() == {
        "id": 2,
        "actor": {"type": "player"},
        "input": {"action": "I search the pier."},
        "character_action": None,
        "narration": "A lantern swings above the water.",
        "llm_data": {
            "character_model_id": None,
            "narrator_model_id": "narrator-model",
        },
    }


def test_map_character_driven_item_maps_character_item():
    metadata = make_scene_metadata()
    message = CharacterDrivenMessage(
        id=3,
        input=CharacterDrivenInput(
            author="c1", action="The navigator warns the captain.", guidance="Warn her."
        ),
        narration="The navigator leans closer.",
        llm_data=CharacterDrivenLLMData(
            character_model_id="character-model", narrator_model_id="narrator-model"
        ),
    )

    item = map_character_driven_item(message, metadata)

    assert item.model_dump() == {
        "id": 3,
        "actor": {"type": "character", "character_id": "c1"},
        "input": {"guidance": "Warn her."},
        "character_action": "The navigator warns the captain.",
        "narration": "The navigator leans closer.",
        "llm_data": {
            "character_model_id": "character-model",
            "narrator_model_id": "narrator-model",
        },
    }


def test_map_character_driven_opening_item_keeps_nulls():
    metadata = make_scene_metadata()
    message = CharacterDrivenMessage(
        id=1,
        input=None,
        narration="A bell rings through the fog.",
        llm_data=CharacterDrivenLLMData(
            character_model_id="character-model", narrator_model_id="narrator-model"
        ),
    )

    item = map_character_driven_item(message, metadata)

    assert item.model_dump() == {
        "id": 1,
        "actor": None,
        "input": None,
        "character_action": None,
        "narration": "A bell rings through the fog.",
        "llm_data": {
            "character_model_id": "character-model",
            "narrator_model_id": "narrator-model",
        },
    }


# --- GET /character-play/scenes/{scene_id} ---


def test_get_scene_success_returns_full_character_driven_shape():
    metadata = make_scene_metadata(
        context=["Previously...", "And then..."]
    ).model_copy(update={"user_character_id": None})
    messages = [
        CharacterDrivenMessage(
            id=1,
            input=None,
            narration="A bell rings through the fog.",
            llm_data=CharacterDrivenLLMData(
                character_model_id="character-model", narrator_model_id="narrator-model"
            ),
        ),
        CharacterDrivenMessage(
            id=2,
            input=CharacterDrivenInput(author=None, action="I search the pier."),
            narration="A lantern swings above the water.",
            llm_data=CharacterDrivenLLMData(
                character_model_id=None, narrator_model_id="narrator-model"
            ),
        ),
        CharacterDrivenMessage(
            id=3,
            input=CharacterDrivenInput(
                author="c1", action="The navigator warns the captain.", guidance="Warn her."
            ),
            narration="The navigator leans closer.",
            llm_data=CharacterDrivenLLMData(
                character_model_id="character-model", narrator_model_id="narrator-model"
            ),
        ),
    ]
    svc = MagicMock()
    svc.get_scene = AsyncMock(return_value=(metadata, messages))
    app.dependency_overrides[get_character_driven_scene_query_service] = lambda: svc

    resp = TestClient(app).get(f"/api/stories/{_STORY_ID}/character-play/scenes/1")

    assert resp.status_code == 200
    assert resp.json() == {
        "data": {
            "id": 1,
            "finished": False,
            "user_character_id": None,
            "character_ids": ["c1"],
            "scene_description": {
                "general_scene_guide": "Guide text.",
                "writing_style": "Descriptive.",
            },
            "context": ["Previously...", "And then..."],
            "scene_summary": None,
            "items": [
                {
                    "id": 1,
                    "actor": None,
                    "input": None,
                    "character_action": None,
                    "narration": "A bell rings through the fog.",
                    "llm_data": {
                        "character_model_id": "character-model",
                        "narrator_model_id": "narrator-model",
                    },
                },
                {
                    "id": 2,
                    "actor": {"type": "player"},
                    "input": {"action": "I search the pier."},
                    "character_action": None,
                    "narration": "A lantern swings above the water.",
                    "llm_data": {
                        "character_model_id": None,
                        "narrator_model_id": "narrator-model",
                    },
                },
                {
                    "id": 3,
                    "actor": {"type": "character", "character_id": "c1"},
                    "input": {"guidance": "Warn her."},
                    "character_action": "The navigator warns the captain.",
                    "narration": "The navigator leans closer.",
                    "llm_data": {
                        "character_model_id": "character-model",
                        "narrator_model_id": "narrator-model",
                    },
                },
            ],
        }
    }
    svc.get_scene.assert_awaited_once_with(_STORY_ID, 1)


@pytest.mark.parametrize("missing", ["story", "scene"])
def test_get_scene_not_found_returns_404(missing):
    svc = MagicMock()
    svc.get_scene = AsyncMock(side_effect=NotFoundError(f"{missing} not found"))
    app.dependency_overrides[get_character_driven_scene_query_service] = lambda: svc

    resp = TestClient(app).get(f"/api/stories/{_STORY_ID}/character-play/scenes/1")

    assert resp.status_code == 404
    assert resp.json() == {
        "error": {"code": "not_found", "message": f"{missing} not found"}
    }


# --- POST /character-play/scenes/{scene_id}/turns ---

_TURN_URL = f"{_URL}/1/turns"

_PLAYER_TURN_PAYLOAD = {
    "actor": {"type": "player"},
    "action": "I look for the nearest light source.",
    "character_model_id": "character-model",
    "narrator_model_id": "narrator-model",
}


def _make_turn_service(
    side_effect: Exception | None = None,
    message: CharacterDrivenMessage | None = None,
) -> MagicMock:
    svc = MagicMock()
    message = message or CharacterDrivenMessage(
        id=2,
        input=CharacterDrivenInput(author="max", action="I look for light."),
        narration="A lantern flickers.",
        llm_data=CharacterDrivenLLMData(
            character_model_id=None, narrator_model_id="narrator-model"
        ),
    )
    svc.submit_turn = (
        AsyncMock(side_effect=side_effect)
        if side_effect is not None
        else AsyncMock(return_value=(make_scene_metadata(), message))
    )
    return svc


def test_submit_player_turn_success():
    svc = _make_turn_service()
    app.dependency_overrides[get_character_driven_scene_turn_service] = lambda: svc

    resp = TestClient(app).post(_TURN_URL, json=_PLAYER_TURN_PAYLOAD)

    assert resp.status_code == 200
    assert resp.json() == {
        "data": {
            "id": 2,
            "actor": {"type": "player"},
            "input": {"action": "I look for light."},
            "character_action": None,
            "narration": "A lantern flickers.",
            "llm_data": {
                "character_model_id": None,
                "narrator_model_id": "narrator-model",
            },
        }
    }
    svc.submit_turn.assert_awaited_once()
    assert svc.submit_turn.await_args.args[:2] == (_STORY_ID, 1)


def test_submit_character_turn_success():
    message = CharacterDrivenMessage(
        id=2,
        input=CharacterDrivenInput(
            author="c1", action="ACTION: She raises the lantern.", guidance=""
        ),
        narration="The lantern cuts through the fog.",
        llm_data=CharacterDrivenLLMData(
            character_model_id="character-model",
            narrator_model_id="narrator-model",
        ),
    )
    svc = _make_turn_service(message=message)
    app.dependency_overrides[get_character_driven_scene_turn_service] = lambda: svc

    resp = TestClient(app).post(_TURN_URL, json=_CHARACTER_TURN_PAYLOAD)

    assert resp.status_code == 200
    assert resp.json() == {
        "data": {
            "id": 2,
            "actor": {"type": "character", "character_id": "c1"},
            "input": {"guidance": ""},
            "character_action": "ACTION: She raises the lantern.",
            "narration": "The lantern cuts through the fog.",
            "llm_data": {
                "character_model_id": "character-model",
                "narrator_model_id": "narrator-model",
            },
        }
    }
    svc.submit_turn.assert_awaited_once()


@pytest.mark.parametrize(
    "payload",
    [
        {**_PLAYER_TURN_PAYLOAD, "action": ""},
        {key: v for key, v in _PLAYER_TURN_PAYLOAD.items() if key != "action"},
        {**_PLAYER_TURN_PAYLOAD, "guidance": "Be careful"},
        {key: v for key, v in _PLAYER_TURN_PAYLOAD.items() if key != "character_model_id"},
        {key: v for key, v in _PLAYER_TURN_PAYLOAD.items() if key != "narrator_model_id"},
        {**_PLAYER_TURN_PAYLOAD, "actor": {"type": "unknown"}},
        {key: v for key, v in _PLAYER_TURN_PAYLOAD.items() if key != "actor"},
        {
            **_CHARACTER_TURN_PAYLOAD,
            "actor": {"type": "character"},
        },
    ],
)
def test_submit_turn_invalid_payload(payload):
    svc = _make_turn_service()
    app.dependency_overrides[get_character_driven_scene_turn_service] = lambda: svc

    resp = TestClient(app).post(_TURN_URL, json=payload)

    assert resp.status_code == 422
    assert resp.json()["error"]["code"] == "validation_error"
    svc.submit_turn.assert_not_awaited()


@pytest.mark.parametrize(
    "exc,status,code",
    [
        (NotFoundError("Scene '1' not found"), 404, "not_found"),
        (SceneFinishedError(), 409, "scene_finished"),
        (InvalidModelError(), 422, "validation_error"),
        (CharacterNotInSceneError(), 422, "validation_error"),
        (LLMError("boom"), 502, "llm_error"),
    ],
)
def test_submit_turn_errors(exc, status, code):
    svc = _make_turn_service(side_effect=exc)
    app.dependency_overrides[get_character_driven_scene_turn_service] = lambda: svc

    resp = TestClient(app).post(_TURN_URL, json=_PLAYER_TURN_PAYLOAD)

    assert resp.status_code == status
    assert resp.json()["error"]["code"] == code
