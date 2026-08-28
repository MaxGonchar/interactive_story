from __future__ import annotations

import yaml

from app.utils import file_paths
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


def test_narrator_scene_play_persists_messages(client):
    meta_path = file_paths.scene_metadata_file(_STORY_ID, _SCENE_ID)
    metadata = yaml.safe_load(meta_path.read_text())
    metadata["user_character_id"] = None
    meta_path.write_text(yaml.safe_dump(metadata))

    response = client.post(_PLAY_URL, json={"content": "Have the villain reveal the map."})

    assert response.status_code == 200
    assert response.json() == {
        "data": {
            "user_message": {
                "id": 1,
                "role": "user",
                "content": "Have the villain reveal the map.",
            },
            "assistant_message": {
                "id": 2,
                "role": "assistant",
                "content": "Assistant reply",
            },
        }
    }

    scene_response = client.get(_SCENE_URL)
    assert scene_response.json()["data"]["messages"] == [
        {"id": 1, "role": "user", "content": "Have the villain reveal the map."},
        {"id": 2, "role": "assistant", "content": "Assistant reply"},
    ]
