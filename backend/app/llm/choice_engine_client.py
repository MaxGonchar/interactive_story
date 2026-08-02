import os
from pathlib import Path

from jinja2 import Environment, FileSystemLoader
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel

from app.llm.venice_ai import VeniceAIChatModel
from app.models.domain import CharacterCard, Choice

_DEFAULT_MODEL = "llama-3.3-70b"
_TEMPLATES_DIR = Path(__file__).parent / "templates"


class _ChoiceOptions(BaseModel):
    options: list[Choice]


class ChoiceEngineClient:
    def __init__(
        self,
        plot_direction: str,
        user_character: CharacterCard,
        supporting_characters: list[CharacterCard],
    ) -> None:
        api_key = os.environ["VENICE_API_KEY"]
        model = os.environ.get("VENICE_MODEL", _DEFAULT_MODEL)
        self._model = VeniceAIChatModel(model=model, api_key=api_key)
        self._plot_direction = plot_direction
        self._user_character = user_character
        self._supporting_characters = supporting_characters
        self._parser = PydanticOutputParser(pydantic_object=_ChoiceOptions)
        env = Environment(loader=FileSystemLoader(str(_TEMPLATES_DIR)), keep_trailing_newline=True)
        self._system_template = env.get_template("choice_engine_system.j2")

    def _build_system_prompt(self) -> str:
        format_instructions = self._parser.get_format_instructions()
        supporting_character_profiles = "\n\n".join(
            c.to_prompt_text() for c in self._supporting_characters
        )
        return self._system_template.render(
            main_character_profile=self._user_character.to_prompt_text(),
            supporting_character_profiles=supporting_character_profiles or "(no supporting characters)",
            plot_direction=self._plot_direction,
            format_instructions=format_instructions,
        )

    async def invoke(self, story_text: str) -> list[Choice]:
        system_prompt = self._build_system_prompt()
        messages = [SystemMessage(system_prompt), HumanMessage(story_text)]
        response = await self._model.ainvoke(messages)
        result = self._parser.parse(response.content)
        return result.options
