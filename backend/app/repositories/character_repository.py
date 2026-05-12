from __future__ import annotations

import asyncio

from app.models.domain import CharacterCard, MemoryEntry
from app.models.storage import CharacterYaml
from app.utils import file_paths, yaml_storage


class CharacterRepository:
    async def get_character(self, story_id: str, character_id: str) -> CharacterCard:
        try:
            data = await yaml_storage.read_yaml(
                file_paths.character_file(story_id, character_id)
            )
        except FileNotFoundError:
            raise KeyError(character_id)

        char = CharacterYaml(**data)

        return CharacterCard(
            id=char.id,
            story_id=char.story_id if char.story_id is not None else story_id,
            name=char.name,
            appearance=char.appearance,
            traits=char.traits,
            speech_patterns=char.speech_patterns,
            body_language=char.body_language,
            likes=char.likes,
            fears=char.fears,
            memory=(
                [MemoryEntry(case=m.case, reflection=m.reflection) for m in char.memory]
                if char.memory is not None
                else None
            ),
        )

    async def get_characters(
        self, story_id: str, character_ids: list[str]
    ) -> list[CharacterCard]:
        return list(
            await asyncio.gather(
                *[self.get_character(story_id, cid) for cid in character_ids]
            )
        )
