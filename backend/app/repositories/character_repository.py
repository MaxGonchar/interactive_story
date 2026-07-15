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

    async def list_characters(self, story_id: str) -> list[CharacterCard]:
        try:
            await yaml_storage.read_yaml(file_paths.story_file(story_id))
        except FileNotFoundError:
            raise NotFoundError(f"Story '{story_id}' not found")

        def _scan_character_ids() -> list[str]:
            d = file_paths.characters_dir(story_id)
            return [p.stem for p in d.iterdir() if p.suffix == ".yaml"]

        character_ids = await asyncio.to_thread(_scan_character_ids)
        return await self.get_characters(story_id, character_ids)
