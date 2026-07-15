from __future__ import annotations

from fastapi import APIRouter, Depends

from app.api.dependencies import get_character_repository
from app.models.api import CharacterListResponse
from app.repositories.character_repository import CharacterRepository

router = APIRouter(prefix="/stories", tags=["characters"])


@router.get(
    "/{story_id}/characters",
    response_model=CharacterListResponse,
)
async def list_characters(
    story_id: str,
    repo: CharacterRepository = Depends(get_character_repository),
):
    characters = await repo.list_characters(story_id)
    return {"data": [{"id": c.id, "name": c.name} for c in characters]}
