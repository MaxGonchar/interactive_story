from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi.testclient import TestClient

from app.api.dependencies import get_story_query_service
from app.main import app
from app.models.domain import SceneRef, StoryMeta

_STORY_ID = "8fa93a9e-8dad-4fcb-b9cf-8e39f1707ec8"


@pytest.mark.parametrize("story_type", ["scene", "choice_driven", "character_driven"])
def test_get_story_returns_type_for_each_story_type(story_type):
    service = MagicMock()
    service.get_story = AsyncMock(
        return_value=StoryMeta(
            id=_STORY_ID,
            title="The Black Harbor",
            type=story_type,
            scenes=[SceneRef(id=1, finished=True), SceneRef(id=2, finished=False)],
            active_scene_id=2,
        )
    )

    app.dependency_overrides[get_story_query_service] = lambda: service

    response = TestClient(app).get(f"/api/stories/{_STORY_ID}")

    assert response.status_code == 200
    assert response.json() == {
        "data": {
            "id": _STORY_ID,
            "title": "The Black Harbor",
            "type": story_type,
            "scenes": [
                {"id": 1, "finished": True},
                {"id": 2, "finished": False},
            ],
            "active_scene_id": 2,
        }
    }
