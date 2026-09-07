from __future__ import annotations

from pathlib import Path

import pytest

from app.exceptions import ModelRegistryError
from app.repositories.model_registry_repository import ModelRegistryRepository


_REGISTRY_YAML = """\nmodels:\n  gpt-4o-mini:\n    name: GPT-4o-mini\n    providerModelID: gpt-4o-mini\n    default: true\n  llama-3.3-70b:\n    name: Llama 3.3 70B\n    providerModelID: llama-3.3-70b\n    default: false\n"""


@pytest.fixture()
def registry_path(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    path = tmp_path / "models.yaml"
    monkeypatch.setenv("MODEL_REGISTRY_PATH", str(path))
    return path


@pytest.mark.asyncio
async def test_get_registry_returns_typed_models_and_default(registry_path: Path):
    registry_path.write_text(_REGISTRY_YAML, encoding="utf-8")

    result = await ModelRegistryRepository().get_registry()

    assert result.default_model_id == "gpt-4o-mini"
    assert result.models["gpt-4o-mini"].model_dump() == {
        "id": "gpt-4o-mini",
        "name": "GPT-4o-mini",
        "provider_model_id": "gpt-4o-mini",
    }


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "content",
    [
        "models:\n  gpt:\n    name: GPT\n    providerModelID: gpt\n",
        "models:\n  gpt:\n    name: GPT\n    providerModelID: gpt\n    default: true\n  llama:\n    name: Llama\n    providerModelID: llama\n    default: true\n",
        "models:\n  '':\n    name: GPT\n    providerModelID: gpt\n    default: true\n",
        "models:\n  gpt:\n    name: ''\n    providerModelID: gpt\n    default: true\n",
    ],
)
async def test_get_registry_rejects_invalid_configuration(registry_path: Path, content: str):
    registry_path.write_text(content, encoding="utf-8")

    with pytest.raises(ModelRegistryError):
        await ModelRegistryRepository().get_registry()


@pytest.mark.asyncio
async def test_get_registry_rejects_missing_configuration(registry_path: Path):
    with pytest.raises(ModelRegistryError):
        await ModelRegistryRepository().get_registry()
