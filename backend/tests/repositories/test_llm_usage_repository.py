from __future__ import annotations

import shutil
from pathlib import Path
from uuid import UUID

import pytest
import yaml
from pydantic import ValidationError

from app.models.domain import LLMUsage, TokenUsage
from app.repositories.llm_usage_repository import LLMUsageRepository

FIXTURE_STORY_ID = "8fa93a9e-8dad-4fcb-b9cf-8e39f1707ec8"
FIXTURE_DATA_ROOT = Path(__file__).parents[3] / "data-test"


@pytest.fixture()
def writable_data_root(monkeypatch, tmp_path):
    copy = tmp_path / "data-test"
    shutil.copytree(FIXTURE_DATA_ROOT, copy)
    monkeypatch.setenv("DATA_ROOT", str(copy))
    return copy


def _make_scene_usage(record_id: str, *, cost_usd: float | None = 0.00042) -> LLMUsage:
    return LLMUsage(
        id=UUID(record_id),
        operation="scene_reply",
        model_id="default",
        provider_model_id="provider-model",
        provider_created=1739928524,
        duration_ms=1243,
        usage=TokenUsage(prompt_tokens=612, completion_tokens=146, total_tokens=758),
        cost_usd=cost_usd,
        scene_id=2,
        message_id=17,
    )


# --- get_calls ---


@pytest.mark.asyncio
async def test_get_calls_returns_empty_list_when_file_is_missing(writable_data_root):
    repo = LLMUsageRepository()

    result = await repo.get_calls(FIXTURE_STORY_ID)

    assert result == []


@pytest.mark.asyncio
async def test_get_calls_rejects_malformed_document(writable_data_root):
    path = writable_data_root / "stories" / FIXTURE_STORY_ID / "llm_usage.yaml"
    path.write_text("calls: [", encoding="utf-8")
    repo = LLMUsageRepository()

    with pytest.raises((yaml.YAMLError, ValidationError)):
        await repo.get_calls(FIXTURE_STORY_ID)


# --- append ---


@pytest.mark.asyncio
async def test_append_writes_complete_record_with_null_cost(writable_data_root):
    repo = LLMUsageRepository()
    usage = _make_scene_usage(
        "f58ec747-7004-4d2c-b749-67b8f0c2e845", cost_usd=None
    )

    await repo.append(FIXTURE_STORY_ID, usage)

    path = writable_data_root / "stories" / FIXTURE_STORY_ID / "llm_usage.yaml"
    assert yaml.safe_load(path.read_text(encoding="utf-8")) == {
        "calls": [
            {
                "cost_usd": None,
                "duration_ms": 1243,
                "id": "f58ec747-7004-4d2c-b749-67b8f0c2e845",
                "message_id": 17,
                "model_id": "default",
                "operation": "scene_reply",
                "provider_created": 1739928524,
                "provider_model_id": "provider-model",
                "scene_id": 2,
                "step_id": None,
                "usage": {
                    "completion_tokens": 146,
                    "prompt_tokens": 612,
                    "total_tokens": 758,
                },
            }
        ]
    }

    assert await repo.get_calls(FIXTURE_STORY_ID) == [usage]


@pytest.mark.asyncio
async def test_append_preserves_existing_records_and_ids(writable_data_root):
    repo = LLMUsageRepository()
    first = _make_scene_usage("f58ec747-7004-4d2c-b749-67b8f0c2e845")
    second = _make_scene_usage("f58ec747-7004-4d2c-b749-67b8f0c2e846")

    await repo.append(FIXTURE_STORY_ID, first)
    await repo.append(FIXTURE_STORY_ID, second)

    result = await repo.get_calls(FIXTURE_STORY_ID)

    assert result == [first, second]
    assert [call.id for call in result] == [first.id, second.id]


@pytest.mark.asyncio
async def test_append_round_trips_choice_reference(writable_data_root):
    repo = LLMUsageRepository()
    usage = LLMUsage(
        id=UUID("f58ec747-7004-4d2c-b749-67b8f0c2e847"),
        operation="choice_generation",
        model_id="default",
        provider_model_id="provider-model",
        provider_created=1739928524,
        duration_ms=1243,
        usage=TokenUsage(prompt_tokens=10, completion_tokens=20, total_tokens=30),
        step_id=3,
    )

    await repo.append(FIXTURE_STORY_ID, usage)

    assert await repo.get_calls(FIXTURE_STORY_ID) == [usage]
