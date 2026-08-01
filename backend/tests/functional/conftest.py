from __future__ import annotations

from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi.testclient import TestClient

from app.api.dependencies import get_scene_llm_client
from app.main import app

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
    app.dependency_overrides[get_scene_llm_client] = lambda: mock_llm

    return TestClient(app)
