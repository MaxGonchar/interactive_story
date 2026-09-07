from __future__ import annotations

from pydantic import ValidationError
import yaml

from app.exceptions import ModelRegistryError
from app.models.domain import ModelMetadata, ModelRegistry
from app.models.storage import ModelRegistryYaml
from app.utils import file_paths, yaml_storage


class ModelRegistryRepository:
    async def get_registry(self) -> ModelRegistry:
        try:
            data = await yaml_storage.read_yaml(file_paths.model_registry_file())
            storage_registry = ModelRegistryYaml.model_validate(data)
        except (FileNotFoundError, OSError, TypeError, ValidationError, yaml.YAMLError) as exc:
            raise ModelRegistryError() from exc

        default_ids = [
            model_id
            for model_id, model in storage_registry.models.items()
            if model.default
        ]
        if not storage_registry.models or any(
            not model_id.strip() for model_id in storage_registry.models
        ) or len(default_ids) != 1:
            raise ModelRegistryError()

        models = {
            model_id: ModelMetadata(
                id=model_id,
                name=model.name,
                provider_model_id=model.provider_model_id,
            )
            for model_id, model in storage_registry.models.items()
        }
        default_model_id = default_ids[0]
        if default_model_id not in models:
            raise ModelRegistryError()

        return ModelRegistry(models=models, default_model_id=default_model_id)
