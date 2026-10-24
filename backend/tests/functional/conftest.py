from __future__ import annotations

from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi.testclient import TestClient

from app.api.dependencies import (
  get_character_agent_client_factory,
  get_memory_agent_client,
  get_narrator_client_factory,
  get_model_registry_service,
  get_scene_llm_client_factory,
  get_summarize_llm_client,
)
from app.main import app
from app.llm.models import LLMCompletion
from app.models.domain import ModelMetadata, ModelRegistry, TokenUsage

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

_CHARACTER_STORY_ID = "character-driven-test-story"

_CHARACTER_STORY_YAML = """\
title: Character Flow Test
type: character_driven
created_at: "2024-01-01T00:00:00Z"
"""

_CAPTAIN_YAML = """\
name: Captain
features: {}
memory:
  - The navigator once saved the ship.
"""

_NAVIGATOR_YAML = """\
name: Navigator
features: {}
memory: []
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


def _write_character_story(root: Path) -> None:
    story_dir = root / "stories" / _CHARACTER_STORY_ID
    story_dir.mkdir(parents=True)
    (story_dir / "story.yaml").write_text(_CHARACTER_STORY_YAML, encoding="utf-8")

    characters_dir = story_dir / "characters"
    characters_dir.mkdir()
    (characters_dir / "captain.yaml").write_text(_CAPTAIN_YAML, encoding="utf-8")
    (characters_dir / "navigator.yaml").write_text(_NAVIGATOR_YAML, encoding="utf-8")
    (story_dir / "scenes").mkdir()


@pytest.fixture
def client(tmp_path, monkeypatch):
    _write_seed_data(tmp_path)
    monkeypatch.setenv("DATA_ROOT", str(tmp_path))

    mock_llm = MagicMock()
    mock_llm.invoke = AsyncMock(
      return_value=LLMCompletion(
        content="Assistant reply",
        model_id="provider-test",
        provider_model_id="provider-test",
        provider_created=1700000000,
        duration_ms=100,
        usage=TokenUsage(prompt_tokens=1, completion_tokens=1, total_tokens=2),
      )
    )
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


@pytest.fixture
def character_driven_client(tmp_path, monkeypatch):
    _write_character_story(tmp_path)
    monkeypatch.setenv("DATA_ROOT", str(tmp_path))

    narrator_client = MagicMock()
    narrator_client.invoke = AsyncMock(
        side_effect=[
            LLMCompletion(
                content=content,
                model_id="provider-narrator",
                provider_model_id="provider-narrator",
                provider_created=1700000000,
                duration_ms=100,
                usage=TokenUsage(prompt_tokens=1, completion_tokens=1, total_tokens=2),
            )
            for content in [
                "The lantern swings over the pier.",
                "The navigator points toward the harbor.",
                "The navigator warns the captain.",
                "The navigator remembers the earlier voyage.",
            ]
        ]
    )
    character_agent_client = MagicMock()
    character_agent_client.invoke = AsyncMock(
        return_value=LLMCompletion(
            content="ACTION: The navigator points toward the harbor.",
            model_id="provider-character",
            provider_model_id="provider-character",
            provider_created=1700000000,
            duration_ms=100,
            usage=TokenUsage(prompt_tokens=1, completion_tokens=1, total_tokens=2),
        )
    )
    summarize_client = MagicMock()
    summarize_client.invoke = AsyncMock(
        return_value=LLMCompletion(
            content='{"items": ["The crew found a safe passage."]}',
            model_id="provider-summary",
            provider_model_id="provider-summary",
            provider_created=1700000000,
            duration_ms=100,
            usage=TokenUsage(prompt_tokens=1, completion_tokens=1, total_tokens=2),
            result=["The crew found a safe passage."],
        )
    )
    memory_client = MagicMock()
    memory_client.invoke = AsyncMock(
        return_value=LLMCompletion(
            content='{"items": ["The crew found a safe passage."]}',
            model_id="provider-memory",
            provider_model_id="provider-memory",
            provider_created=1700000000,
            duration_ms=100,
            usage=TokenUsage(prompt_tokens=1, completion_tokens=1, total_tokens=2),
            result=["The crew found a safe passage."],
        )
    )

    registry_service = MagicMock()
    registry_service.get_registry = AsyncMock(
        return_value=ModelRegistry(
            models={
                "character-model": ModelMetadata(
                    id="character-model",
                    name="Character",
                    provider_model_id="provider-character",
                ),
                "narrator-model": ModelMetadata(
                    id="narrator-model",
                    name="Narrator",
                    provider_model_id="provider-narrator",
                ),
            },
            default_model_id="narrator-model",
        )
    )
    registry_service.validate_model_ids = AsyncMock()

    app.dependency_overrides[get_model_registry_service] = lambda: registry_service
    app.dependency_overrides[get_narrator_client_factory] = (
        lambda: lambda _: narrator_client
    )
    app.dependency_overrides[get_character_agent_client_factory] = (
        lambda: lambda _: character_agent_client
    )
    app.dependency_overrides[get_summarize_llm_client] = lambda: summarize_client
    app.dependency_overrides[get_memory_agent_client] = lambda: memory_client

    return TestClient(app), character_agent_client
