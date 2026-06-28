from __future__ import annotations

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from app.api.dependencies import get_choice_driven_play_service
from app.models.api import (
    ChoiceDrivenPlayResponse,
    EditStepRequest,
    EditStepResponse,
    GenerateChoicesResponse,
    ReturnToStepResponse,
    SelectChoiceRequest,
    SelectChoiceResponse,
)
from app.models.domain import Choice
from app.services.choice_driven_play_service import ChoiceDrivenPlayService

router = APIRouter(prefix="/stories", tags=["choice-driven"])


def _not_found(story_id: str) -> JSONResponse:
    return JSONResponse(
        status_code=404,
        content={"error": {"code": "not_found", "message": f"Story '{story_id}' not found"}},
    )


def _step_to_dict(step) -> dict:
    return {
        "id": step.id,
        "incoming_choice": (
            {"action": step.incoming_choice.action, "consequence": step.incoming_choice.consequence}
            if step.incoming_choice is not None
            else None
        ),
        "text": step.text,
        "choices": [{"action": c.action, "consequence": c.consequence} for c in step.choices],
    }


@router.get(
    "/{story_id}/choice-play",
    response_model=ChoiceDrivenPlayResponse,
)
async def get_choice_play(
    story_id: str,
    svc: ChoiceDrivenPlayService = Depends(get_choice_driven_play_service),
):
    try:
        meta = await svc._repo.get_story_meta(story_id)
        steps = await svc.get_play_state(story_id)
    except KeyError:
        return _not_found(story_id)
    return {
        "data": {
            "id": meta.id,
            "title": meta.title,
            "steps": [_step_to_dict(s) for s in steps],
        }
    }


@router.post(
    "/{story_id}/choice-play/generate-choices",
    response_model=GenerateChoicesResponse,
)
async def generate_choices(
    story_id: str,
    svc: ChoiceDrivenPlayService = Depends(get_choice_driven_play_service),
):
    try:
        choices = await svc.generate_choices(story_id)
    except KeyError:
        return _not_found(story_id)
    return {"data": {"choices": [{"action": c.action, "consequence": c.consequence} for c in choices]}}


@router.post(
    "/{story_id}/choice-play/regenerate-choices",
    response_model=GenerateChoicesResponse,
)
async def regenerate_choices(
    story_id: str,
    svc: ChoiceDrivenPlayService = Depends(get_choice_driven_play_service),
):
    try:
        choices = await svc.regenerate_choices(story_id)
    except KeyError:
        return _not_found(story_id)
    return {"data": {"choices": [{"action": c.action, "consequence": c.consequence} for c in choices]}}


@router.post(
    "/{story_id}/choice-play/select-choice",
    response_model=SelectChoiceResponse,
)
async def select_choice(
    story_id: str,
    request: SelectChoiceRequest,
    svc: ChoiceDrivenPlayService = Depends(get_choice_driven_play_service),
):
    try:
        choice = Choice(action=request.action, consequence=request.consequence)
        step = await svc.select_choice(story_id, choice)
    except KeyError:
        return _not_found(story_id)
    return {"data": _step_to_dict(step)}


@router.patch(
    "/{story_id}/choice-play/steps/{step_id}",
    response_model=EditStepResponse,
)
async def edit_step(
    story_id: str,
    step_id: int,
    request: EditStepRequest,
    svc: ChoiceDrivenPlayService = Depends(get_choice_driven_play_service),
):
    try:
        step = await svc.edit_step_text(story_id, step_id, request.text)
    except KeyError:
        return _not_found(story_id)
    return {"data": {"id": step.id, "text": step.text}}


@router.delete(
    "/{story_id}/choice-play/steps/{step_id}/forward",
    response_model=ReturnToStepResponse,
)
async def return_to_step(
    story_id: str,
    step_id: int,
    svc: ChoiceDrivenPlayService = Depends(get_choice_driven_play_service),
):
    try:
        returned_step_id = await svc.return_to_step(story_id, step_id)
    except KeyError:
        return _not_found(story_id)
    return {"data": {"step_id": returned_step_id}}
