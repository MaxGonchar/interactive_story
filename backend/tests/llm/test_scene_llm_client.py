import os
from unittest.mock import AsyncMock, patch

import pytest

from app.llm.models import SceneContext
from app.llm.scene_llm_client import SceneLLMClient, _DEFAULT_MODEL
from app.models.domain import SceneDescription


def _make_context() -> SceneContext:
    return SceneContext(
        scene_description=SceneDescription(
            entry_point="A dark alley.",
            general_scene_guide="Build tension.",
            writing_style="Gritty noir.",
        ),
        characters=[],
        messages=[],
    )


@pytest.fixture(autouse=True)
def set_api_key(monkeypatch):
    monkeypatch.setenv("VENICE_API_KEY", "test-key")


@pytest.fixture(autouse=True)
def clear_model_env(monkeypatch):
    monkeypatch.delenv("VENICE_MODEL", raising=False)


@pytest.mark.asyncio
async def test_invoke_returns_model_content():
    client = SceneLLMClient()
    with patch.object(client._model._client, "chat_complete", new_callable=AsyncMock) as mock_cc:
        mock_cc.return_value = "hi"
        result = await client.invoke(_make_context(), "Hello")
    assert result == "hi"
    mock_cc.assert_called_once()


def test_default_model_name_used_when_env_absent():
    client = SceneLLMClient()
    assert client._model.model == _DEFAULT_MODEL


def test_custom_model_name_from_env(monkeypatch):
    monkeypatch.setenv("VENICE_MODEL", "my-custom-model")
    client = SceneLLMClient()
    assert client._model.model == "my-custom-model"


def test_raises_when_api_key_missing(monkeypatch):
    monkeypatch.delenv("VENICE_API_KEY", raising=False)
    with pytest.raises(KeyError):
        SceneLLMClient()
