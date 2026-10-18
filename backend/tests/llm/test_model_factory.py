from __future__ import annotations

from app.api.dependencies import get_character_driven_model_factory
from app.llm.model_factory import make_character_driven_model_factory


def test_model_factory_builds_model_for_provider_model_id():
    factory = make_character_driven_model_factory("test-key")

    model = factory("provider/model-name")

    assert model.model == "provider/model-name"
    assert model.api_key == "test-key"


def test_dependency_model_factory_uses_venice_api_key(monkeypatch):
    monkeypatch.setenv("VENICE_API_KEY", "test-key")

    model = get_character_driven_model_factory()("provider/model-name")

    assert model.model == "provider/model-name"
    assert model.api_key == "test-key"