from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

from fastapi.testclient import TestClient

from app.api.dependencies import get_model_registry_service
from app.exceptions import ModelRegistryError
from app.main import app
from app.models.domain import ModelMetadata, ModelRegistry


def test_get_models_returns_registry_shape():
    service = MagicMock()
    service.get_registry = AsyncMock(
        return_value=ModelRegistry(
            models={
                "gpt-4o-mini": ModelMetadata(
                    id="gpt-4o-mini",
                    name="GPT-4o-mini",
                    provider_model_id="gpt-4o-mini",
                ),
                "llama-3.3-70b": ModelMetadata(
                    id="llama-3.3-70b",
                    name="Llama 3.3 70B",
                    provider_model_id="llama-3.3-70b",
                ),
            },
            default_model_id="gpt-4o-mini",
        )
    )
    app.dependency_overrides[get_model_registry_service] = lambda: service

    response = TestClient(app).get("/api/models")

    assert response.status_code == 200
    assert response.json() == {
        "data": {
            "models": {
                "gpt-4o-mini": {
                    "name": "GPT-4o-mini",
                    "providerModelID": "gpt-4o-mini",
                },
                "llama-3.3-70b": {
                    "name": "Llama 3.3 70B",
                    "providerModelID": "llama-3.3-70b",
                },
            },
            "default_model_id": "gpt-4o-mini",
        }
    }


def test_get_models_returns_controlled_error_for_invalid_registry():
    service = MagicMock()
    service.get_registry = AsyncMock(side_effect=ModelRegistryError())
    app.dependency_overrides[get_model_registry_service] = lambda: service

    response = TestClient(app).get("/api/models")

    assert response.status_code == 500
    assert response.json() == {
        "error": {
            "code": "internal_error",
            "message": "Model registry configuration is invalid",
        }
    }
