from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends

from app.api.dependencies import get_model_registry_service
from app.models.api import ModelRegistryResponse
from app.services.model_registry_service import ModelRegistryService

router = APIRouter(prefix="/models", tags=["models"])


@router.get("", response_model=ModelRegistryResponse)
async def get_models(
    svc: Annotated[ModelRegistryService, Depends(get_model_registry_service)],
):
    registry = await svc.get_registry()
    return {
        "data": {
            "models": {
                model_id: {
                    "name": model.name,
                    "providerModelID": model.provider_model_id,
                }
                for model_id, model in registry.models.items()
            },
            "default_model_id": registry.default_model_id,
        }
    }
