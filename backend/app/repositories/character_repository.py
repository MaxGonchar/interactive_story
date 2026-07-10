from __future__ import annotations

import asyncio

from app.exceptions import NotFoundError
from app.models.domain import CharacterCard
from app.models.storage import CharacterYaml
from app.utils import file_paths, yaml_storage


class CharacterRepository:
    async def get_character(self, story_id: str, character_id: str) -> CharacterCard:
        try:
            data = await yaml_storage.read_yaml(
                file_paths.character_file(story_id, character_id)
            )
        except FileNotFoundError:
            raise NotFoundError(f"Character '{character_id}' not found")

        char = CharacterYaml(**data)

        return CharacterCard(
            id=character_id,
            name=char.name,
            features=char.features,
            memory=char.memory,
        )

    async def get_characters(
        self, story_id: str, character_ids: list[str]
    ) -> list[CharacterCard]:
        return list(
            await asyncio.gather(
                *[self.get_character(story_id, cid) for cid in character_ids]
            )
        )
