from __future__ import annotations

from app.exceptions import InvalidModelError
from app.models.domain import ModelRegistry
from app.repositories.model_registry_repository import ModelRegistryRepository


class ModelRegistryService:
    def __init__(self, repo: ModelRegistryRepository) -> None:
        self._repo = repo

    async def get_registry(self) -> ModelRegistry:
        return await self._repo.get_registry()

    async def validate_model_ids(self, *model_ids: str) -> None:
        registry = await self._repo.get_registry()
        if any(model_id not in registry.models for model_id in model_ids):
            raise InvalidModelError()
