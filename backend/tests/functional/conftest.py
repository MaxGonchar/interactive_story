from __future__ import annotations

from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi.testclient import TestClient

from app.api.dependencies import (
  get_model_registry_service,
  get_scene_llm_client_factory,
)
from app.main import app
from app.models.domain import ModelMetadata, ModelRegistry

_STORY_ID = "test-story-1"
_SCENE_ID = 1

_STORY_YAML = """\
title: Test Story
type: scene
created_at: "2024-01-01T00:00:00Z"
"""

_HERO_YAML = """\
name: Hero
features: {}
memory: []
"""

_VILLAIN_YAML = """\
name: Villain
features: {}
memory: []
"""

_SCENE_META_YAML = """\
finished: false
character_ids:
  - villain
user_character_id: hero
scene_description:
  general_scene_guide: Move the story forward.
  writing_style: Descriptive prose.
scene_summary: null
context: null
"""


def _write_seed_data(root: Path) -> None:
    story_dir = root / "stories" / _STORY_ID
    (story_dir).mkdir(parents=True)
    (story_dir / "story.yaml").write_text(_STORY_YAML, encoding="utf-8")

    characters_dir = story_dir / "characters"
    characters_dir.mkdir()
    (characters_dir / "hero.yaml").write_text(_HERO_YAML, encoding="utf-8")
    (characters_dir / "villain.yaml").write_text(_VILLAIN_YAML, encoding="utf-8")

    scene_dir = story_dir / "scenes" / str(_SCENE_ID)
    scene_dir.mkdir(parents=True)
    (scene_dir / "meta.yaml").write_text(_SCENE_META_YAML, encoding="utf-8")


@pytest.fixture
def client(tmp_path, monkeypatch):
    _write_seed_data(tmp_path)
    monkeypatch.setenv("DATA_ROOT", str(tmp_path))

    mock_llm = MagicMock()
    mock_llm.invoke = AsyncMock(return_value="Assistant reply")
    registry_service = MagicMock()
    registry_service.get_registry = AsyncMock(
      return_value=ModelRegistry(
        models={
          "test-model": ModelMetadata(
            id="test-model", name="Test", provider_model_id="provider-test"
          )
        },
        default_model_id="test-model",
      )
    )
    app.dependency_overrides[get_scene_llm_client_factory] = lambda: lambda _: mock_llm
    app.dependency_overrides[get_model_registry_service] = lambda: registry_service

    return TestClient(app)
