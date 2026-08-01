from __future__ import annotations

from tests.functional.conftest import _SCENE_ID, _STORY_ID

_PLAY_URL = f"/api/stories/{_STORY_ID}/scenes/{_SCENE_ID}/play"
_SCENE_URL = f"/api/stories/{_STORY_ID}/scenes/{_SCENE_ID}"
_PLAY_PAYLOAD = {"content": "Hello"}


# --- POST /play ---


def test_play_returns_user_and_assistant_messages(client):
    response = client.post(_PLAY_URL, json=_PLAY_PAYLOAD)

    assert response.status_code == 200
    data = response.json()["data"]
    assert data["user_message"] == {"id": 1, "role": "user", "content": "Hello"}
    assert data["assistant_message"] == {"id": 2, "role": "assistant", "content": "Assistant reply"}


# --- GET /scenes/{scene_id} ---


def test_play_messages_persisted_in_scene(client):
    client.post(_PLAY_URL, json=_PLAY_PAYLOAD)

    response = client.get(_SCENE_URL)

    assert response.status_code == 200
    messages = response.json()["data"]["messages"]
    assert {"id": 1, "role": "user", "content": "Hello"} in messages
    assert {"id": 2, "role": "assistant", "content": "Assistant reply"} in messages
