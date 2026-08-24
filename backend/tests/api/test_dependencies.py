from __future__ import annotations

import pytest

from app.api.dependencies import _DEFAULT_MODEL, get_summary_model, get_venice_model


# --- get_venice_model ---

def test_get_venice_model_uses_default_when_env_absent(monkeypatch):
    monkeypatch.setenv("VENICE_API_KEY", "test-key")
    monkeypatch.delenv("VENICE_MODEL", raising=False)

    model = get_venice_model()

    assert model.model == _DEFAULT_MODEL
    assert model.api_key == "test-key"


def test_get_venice_model_uses_custom_model_from_env(monkeypatch):
    monkeypatch.setenv("VENICE_API_KEY", "test-key")
    monkeypatch.setenv("VENICE_MODEL", "my-custom-model")

    model = get_venice_model()

    assert model.model == "my-custom-model"


def test_get_venice_model_raises_when_api_key_missing(monkeypatch):
    monkeypatch.delenv("VENICE_API_KEY", raising=False)

    with pytest.raises(KeyError):
        get_venice_model()


# --- get_summary_model ---

def test_get_summary_model_uses_default_when_env_absent(monkeypatch):
    monkeypatch.setenv("VENICE_API_KEY", "test-key")
    monkeypatch.delenv("SUMMARY_MODEL", raising=False)

    model = get_summary_model()

    assert model.model == _DEFAULT_MODEL
    assert model.api_key == "test-key"


def test_get_summary_model_uses_custom_model_from_env(monkeypatch):
    monkeypatch.setenv("VENICE_API_KEY", "test-key")
    monkeypatch.setenv("SUMMARY_MODEL", "my-summary-model")

    model = get_summary_model()

    assert model.model == "my-summary-model"


def test_get_summary_model_raises_when_api_key_missing(monkeypatch):
    monkeypatch.delenv("VENICE_API_KEY", raising=False)

    with pytest.raises(KeyError):
        get_summary_model()
