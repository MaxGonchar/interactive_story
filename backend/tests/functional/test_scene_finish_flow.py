from __future__ import annotations

from tests.functional.conftest import _SCENE_ID, _STORY_ID

_PLAY_URL = f"/api/stories/{_STORY_ID}/scenes/{_SCENE_ID}/play"
_FINISH_URL = f"/api/stories/{_STORY_ID}/scenes/{_SCENE_ID}/finish"
_PLAY_PAYLOAD = {"content": "Hello"}
_FINISH_PAYLOAD = {"scene_summary": ["The scene ended."]}


# --- POST /finish then POST /play ---


def test_finish_then_play_returns_409(client):
    finish_response = client.post(_FINISH_URL, json=_FINISH_PAYLOAD)

    assert finish_response.status_code == 200

    play_response = client.post(_PLAY_URL, json=_PLAY_PAYLOAD)

    assert play_response.status_code == 409
