from __future__ import annotations

import asyncio
from pathlib import Path

from app.exceptions import NotFoundError
from app.models.domain import CharacterCard
from app.models.storage import CharacterYaml
from app.utils import file_paths, yaml_storage
from app.utils.atomic_write import atomic_write


class CharacterRepository:
    async def _read_character_yaml(
        self, story_id: str, character_id: str
    ) -> tuple[Path, dict, CharacterYaml]:
        path = file_paths.character_file(story_id, character_id)
        try:
            data = await yaml_storage.read_yaml(path)
        except FileNotFoundError:
            raise NotFoundError(f"Character '{character_id}' not found")

        return path, data, CharacterYaml(**data)

    async def _write_character_yaml(
        self, path: Path, data: dict, character: CharacterYaml
    ) -> None:
        serialized = character.model_dump()
        # Keep hand-written fields that CharacterYaml does not model.
        serialized.update(
            {
                key: value
                for key, value in data.items()
                if key not in CharacterYaml.model_fields
            }
        )
        await atomic_write(path, yaml_storage.dump_yaml(serialized))

    async def get_character(self, story_id: str, character_id: str) -> CharacterCard:
        _, _, char = await self._read_character_yaml(story_id, character_id)

        return CharacterCard(
            id=character_id,
            name=char.name,
            features=char.features,
            memory=char.memory,
        )

    async def append_memory(
        self, story_id: str, character_id: str, entries: list[str]
    ) -> None:
        path, data, character = await self._read_character_yaml(
            story_id, character_id
        )
        memory = list(character.memory)
        known_entries = set(memory)
        for entry in entries:
            if entry not in known_entries:
                memory.append(entry)
                known_entries.add(entry)

        character.memory = memory
        await self._write_character_yaml(path, data, character)

    async def set_memory(
        self, story_id: str, character_id: str, memory: list[str]
    ) -> None:
        path, data, character = await self._read_character_yaml(
            story_id, character_id
        )
        character.memory = memory
        await self._write_character_yaml(path, data, character)

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
