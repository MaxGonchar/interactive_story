from __future__ import annotations

from collections.abc import Callable

from app.llm.venice_ai import VeniceAIChatModel

CharacterDrivenModelFactory = Callable[[str], VeniceAIChatModel]


def make_character_driven_model_factory(api_key: str) -> CharacterDrivenModelFactory:
    def create_model(provider_model_id: str) -> VeniceAIChatModel:
        return VeniceAIChatModel(model=provider_model_id, api_key=api_key)

    return create_model