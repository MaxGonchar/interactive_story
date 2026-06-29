from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi.testclient import TestClient

from app.api.dependencies import get_choice_driven_play_service
from app.exceptions import NoStepsError, NotFoundError
from app.main import app
from app.models.domain import Choice, ChoiceDrivenStoryMeta, Step

_STORY_ID = "8fa93a9e-8dad-4fcb-b9cf-8e39f1707ec8"
_MISSING_ID = "00000000-0000-0000-0000-000000000000"

_CHOICE_A = Choice(action="Go left", consequence="Find a shortcut")
_CHOICE_B = Choice(action="Go right", consequence="Meet a stranger")

_STEP_1 = Step(id=1, incoming_choice=None, text="The fog rolled in.", choices=[_CHOICE_A, _CHOICE_B])
_STEP_2 = Step(
    id=2,
    incoming_choice=_CHOICE_A,
    text="A shortcut appeared.",
    choices=[],
)

_META = ChoiceDrivenStoryMeta(
    id=_STORY_ID,
    title="The Black Harbor",
    writing_style="dark, suspenseful",
    plot_directions=["Romance", "Betrayal"],
    character_ids=["c1"],
)


def _make_mock_service(
    steps: list[Step] | None = None,
    choices: list[Choice] | None = None,
    new_step: Step | None = None,
    edited_step: Step | None = None,
    returned_step_id: int = 1,
    story_not_found: bool = False,
    generate_choices_side_effect: Exception | None = None,
    regenerate_choices_side_effect: Exception | None = None,
) -> MagicMock:
    svc = MagicMock()
    svc._repo = MagicMock()

    if story_not_found:
        svc._repo.get_story_meta = AsyncMock(side_effect=NotFoundError(_MISSING_ID))
        svc.get_play_state = AsyncMock(side_effect=NotFoundError(_MISSING_ID))
        svc.generate_choices = AsyncMock(side_effect=NotFoundError(_MISSING_ID))
        svc.regenerate_choices = AsyncMock(side_effect=NotFoundError(_MISSING_ID))
        svc.select_choice = AsyncMock(side_effect=NotFoundError(_MISSING_ID))
        svc.edit_step_text = AsyncMock(side_effect=NotFoundError(_MISSING_ID))
        svc.return_to_step = AsyncMock(side_effect=NotFoundError(_MISSING_ID))
    else:
        svc._repo.get_story_meta = AsyncMock(return_value=_META)
        svc.get_play_state = AsyncMock(return_value=steps or [_STEP_1, _STEP_2])
        if generate_choices_side_effect is not None:
            svc.generate_choices = AsyncMock(side_effect=generate_choices_side_effect)
        else:
            svc.generate_choices = AsyncMock(return_value=choices or [_CHOICE_A, _CHOICE_B])
        if regenerate_choices_side_effect is not None:
            svc.regenerate_choices = AsyncMock(side_effect=regenerate_choices_side_effect)
        else:
            svc.regenerate_choices = AsyncMock(return_value=choices or [_CHOICE_A, _CHOICE_B])
        svc.select_choice = AsyncMock(return_value=new_step or _STEP_2)
        svc.edit_step_text = AsyncMock(return_value=edited_step or _STEP_1)
        svc.return_to_step = AsyncMock(return_value=returned_step_id)

    return svc


# ---------------------------------------------------------------------------
# GET /api/stories/{story_id}/choice-play
# ---------------------------------------------------------------------------


class TestGetChoicePlay:
    def test_returns_play_state(self):
        mock_svc = _make_mock_service()
        app.dependency_overrides[get_choice_driven_play_service] = lambda: mock_svc

        with TestClient(app) as client:
            resp = client.get(f"/api/stories/{_STORY_ID}/choice-play")

        app.dependency_overrides.clear()

        assert resp.status_code == 200
        data = resp.json()["data"]
        assert data["id"] == _STORY_ID
        assert data["title"] == "The Black Harbor"
        assert len(data["steps"]) == 2
        step1 = data["steps"][0]
        assert step1["id"] == 1
        assert step1["incoming_choice"] is None
        assert len(step1["choices"]) == 2

    def test_returns_404_for_unknown_story(self):
        mock_svc = _make_mock_service(story_not_found=True)
        app.dependency_overrides[get_choice_driven_play_service] = lambda: mock_svc

        with TestClient(app) as client:
            resp = client.get(f"/api/stories/{_MISSING_ID}/choice-play")

        app.dependency_overrides.clear()

        assert resp.status_code == 404
        assert resp.json()["error"]["code"] == "not_found"


# ---------------------------------------------------------------------------
# POST /api/stories/{story_id}/choice-play/generate-choices
# ---------------------------------------------------------------------------


class TestGenerateChoices:
    def test_returns_choices(self):
        mock_svc = _make_mock_service()
        app.dependency_overrides[get_choice_driven_play_service] = lambda: mock_svc

        with TestClient(app) as client:
            resp = client.post(f"/api/stories/{_STORY_ID}/choice-play/generate-choices")

        app.dependency_overrides.clear()

        assert resp.status_code == 200
        choices = resp.json()["data"]["choices"]
        assert len(choices) == 2
        assert choices[0]["action"] == "Go left"

    def test_returns_404_for_unknown_story(self):
        mock_svc = _make_mock_service(story_not_found=True)
        app.dependency_overrides[get_choice_driven_play_service] = lambda: mock_svc

        with TestClient(app) as client:
            resp = client.post(f"/api/stories/{_MISSING_ID}/choice-play/generate-choices")

        app.dependency_overrides.clear()

        assert resp.status_code == 404

    def test_returns_409_when_no_steps(self):
        mock_svc = _make_mock_service(generate_choices_side_effect=NoStepsError())
        app.dependency_overrides[get_choice_driven_play_service] = lambda: mock_svc

        with TestClient(app) as client:
            resp = client.post(f"/api/stories/{_STORY_ID}/choice-play/generate-choices")

        app.dependency_overrides.clear()

        assert resp.status_code == 409
        assert resp.json()["error"]["code"] == "no_steps"


# ---------------------------------------------------------------------------
# POST /api/stories/{story_id}/choice-play/regenerate-choices
# ---------------------------------------------------------------------------


class TestRegenerateChoices:
    def test_returns_choices(self):
        mock_svc = _make_mock_service()
        app.dependency_overrides[get_choice_driven_play_service] = lambda: mock_svc

        with TestClient(app) as client:
            resp = client.post(f"/api/stories/{_STORY_ID}/choice-play/regenerate-choices")

        app.dependency_overrides.clear()

        assert resp.status_code == 200
        choices = resp.json()["data"]["choices"]
        assert len(choices) == 2

    def test_returns_404_for_unknown_story(self):
        mock_svc = _make_mock_service(story_not_found=True)
        app.dependency_overrides[get_choice_driven_play_service] = lambda: mock_svc

        with TestClient(app) as client:
            resp = client.post(f"/api/stories/{_MISSING_ID}/choice-play/regenerate-choices")

        app.dependency_overrides.clear()

        assert resp.status_code == 404

    def test_returns_409_when_no_steps(self):
        mock_svc = _make_mock_service(regenerate_choices_side_effect=NoStepsError())
        app.dependency_overrides[get_choice_driven_play_service] = lambda: mock_svc

        with TestClient(app) as client:
            resp = client.post(f"/api/stories/{_STORY_ID}/choice-play/regenerate-choices")

        app.dependency_overrides.clear()

        assert resp.status_code == 409
        assert resp.json()["error"]["code"] == "no_steps"


# ---------------------------------------------------------------------------
# POST /api/stories/{story_id}/choice-play/select-choice
# ---------------------------------------------------------------------------


class TestSelectChoice:
    def test_returns_new_step(self):
        mock_svc = _make_mock_service()
        app.dependency_overrides[get_choice_driven_play_service] = lambda: mock_svc

        with TestClient(app) as client:
            resp = client.post(
                f"/api/stories/{_STORY_ID}/choice-play/select-choice",
                json={"action": "Go left", "consequence": "Find a shortcut"},
            )

        app.dependency_overrides.clear()

        assert resp.status_code == 200
        data = resp.json()["data"]
        assert data["id"] == 2
        assert data["incoming_choice"]["action"] == "Go left"
        assert data["text"] == "A shortcut appeared."

    def test_returns_404_for_unknown_story(self):
        mock_svc = _make_mock_service(story_not_found=True)
        app.dependency_overrides[get_choice_driven_play_service] = lambda: mock_svc

        with TestClient(app) as client:
            resp = client.post(
                f"/api/stories/{_MISSING_ID}/choice-play/select-choice",
                json={"action": "Go left", "consequence": "Find a shortcut"},
            )

        app.dependency_overrides.clear()

        assert resp.status_code == 404


# ---------------------------------------------------------------------------
# PATCH /api/stories/{story_id}/choice-play/steps/{step_id}
# ---------------------------------------------------------------------------


class TestEditStep:
    def test_returns_updated_step(self):
        edited = Step(id=1, incoming_choice=None, text="Corrected text.", choices=[])
        mock_svc = _make_mock_service(edited_step=edited)
        app.dependency_overrides[get_choice_driven_play_service] = lambda: mock_svc

        with TestClient(app) as client:
            resp = client.patch(
                f"/api/stories/{_STORY_ID}/choice-play/steps/1",
                json={"text": "Corrected text."},
            )

        app.dependency_overrides.clear()

        assert resp.status_code == 200
        data = resp.json()["data"]
        assert data["id"] == 1
        assert data["text"] == "Corrected text."

    def test_returns_404_for_unknown_story(self):
        mock_svc = _make_mock_service(story_not_found=True)
        app.dependency_overrides[get_choice_driven_play_service] = lambda: mock_svc

        with TestClient(app) as client:
            resp = client.patch(
                f"/api/stories/{_MISSING_ID}/choice-play/steps/1",
                json={"text": "Corrected text."},
            )

        app.dependency_overrides.clear()

        assert resp.status_code == 404


# ---------------------------------------------------------------------------
# DELETE /api/stories/{story_id}/choice-play/steps/{step_id}/forward
# ---------------------------------------------------------------------------


class TestReturnToStep:
    def test_returns_step_id(self):
        mock_svc = _make_mock_service(returned_step_id=1)
        app.dependency_overrides[get_choice_driven_play_service] = lambda: mock_svc

        with TestClient(app) as client:
            resp = client.delete(f"/api/stories/{_STORY_ID}/choice-play/steps/1/forward")

        app.dependency_overrides.clear()

        assert resp.status_code == 200
        assert resp.json()["data"]["step_id"] == 1

    def test_returns_404_for_unknown_story(self):
        mock_svc = _make_mock_service(story_not_found=True)
        app.dependency_overrides[get_choice_driven_play_service] = lambda: mock_svc

        with TestClient(app) as client:
            resp = client.delete(f"/api/stories/{_MISSING_ID}/choice-play/steps/1/forward")

        app.dependency_overrides.clear()

        assert resp.status_code == 404
