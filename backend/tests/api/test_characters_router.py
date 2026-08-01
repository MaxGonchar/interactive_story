from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.api.dependencies import get_character_repository
from app.exceptions import NotFoundError
from app.main import app
from tests.factories import make_character_repo

_STORY_ID = "8fa93a9e-8dad-4fcb-b9cf-8e39f1707ec8"


# ---------------------------------------------------------------------------
# GET /api/stories/{story_id}/characters
# ---------------------------------------------------------------------------


def test_list_characters_success():
    repo = make_character_repo()
    app.dependency_overrides[get_character_repository] = lambda: repo

    client = TestClient(app)
    resp = client.get(f"/api/stories/{_STORY_ID}/characters")

    assert resp.status_code == 200
    assert resp.json() == {
        "data": [
            {"id": "mila", "name": "Mila"},
            {"id": "bun", "name": "Bun"},
            {"id": "max", "name": "Max"},
        ]
    }


def test_list_characters_unknown_story_returns_404():
    repo = make_character_repo(list_side_effect=NotFoundError("Story not found"))
    app.dependency_overrides[get_character_repository] = lambda: repo

    client = TestClient(app)
    resp = client.get("/api/stories/nonexistent-story/characters")

    assert resp.status_code == 404
    assert resp.json()["error"]["code"] == "not_found"
