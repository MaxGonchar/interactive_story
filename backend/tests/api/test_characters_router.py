from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi.testclient import TestClient

from app.api.dependencies import get_character_repository
from app.exceptions import NotFoundError
from app.main import app
from app.models.domain import CharacterCard

_STORY_ID = "8fa93a9e-8dad-4fcb-b9cf-8e39f1707ec8"

_CHARACTERS = [
    CharacterCard(id="mila", name="Mila", features={}, memory=[]),
    CharacterCard(id="bun", name="Bun", features={}, memory=[]),
    CharacterCard(id="max", name="Max", features={}, memory=[]),
]


def _make_repo(
    list_side_effect: Exception | None = None,
    list_return: list[CharacterCard] | None = None,
) -> MagicMock:
    repo = MagicMock()
    if list_side_effect is not None:
        repo.list_characters = AsyncMock(side_effect=list_side_effect)
    else:
        repo.list_characters = AsyncMock(return_value=list_return or _CHARACTERS)
    return repo


# ---------------------------------------------------------------------------
# GET /api/stories/{story_id}/characters
# ---------------------------------------------------------------------------


class TestListCharacters:
    def test_returns_200_with_character_list(self):
        repo = _make_repo()
        app.dependency_overrides[get_character_repository] = lambda: repo

        with TestClient(app) as client:
            resp = client.get(f"/api/stories/{_STORY_ID}/characters")

        app.dependency_overrides.clear()

        assert resp.status_code == 200
        body = resp.json()
        assert "data" in body
        assert len(body["data"]) == 3
        ids = {item["id"] for item in body["data"]}
        assert ids == {"mila", "bun", "max"}

    def test_response_items_have_id_and_name(self):
        repo = _make_repo()
        app.dependency_overrides[get_character_repository] = lambda: repo

        with TestClient(app) as client:
            resp = client.get(f"/api/stories/{_STORY_ID}/characters")

        app.dependency_overrides.clear()

        for item in resp.json()["data"]:
            assert "id" in item
            assert "name" in item

    def test_unknown_story_returns_404(self):
        repo = _make_repo(list_side_effect=NotFoundError("Story not found"))
        app.dependency_overrides[get_character_repository] = lambda: repo

        with TestClient(app) as client:
            resp = client.get("/api/stories/nonexistent-story/characters")

        app.dependency_overrides.clear()

        assert resp.status_code == 404
        assert resp.json()["error"]["code"] == "not_found"
