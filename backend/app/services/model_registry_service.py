from __future__ import annotations

from app.models.domain import ModelRegistry
from app.repositories.model_registry_repository import ModelRegistryRepository


class ModelRegistryService:
    def __init__(self, repo: ModelRegistryRepository) -> None:
        self._repo = repo

    async def get_registry(self) -> ModelRegistry:
        return await self._repo.get_registry()
