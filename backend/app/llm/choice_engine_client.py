from pathlib import Path

from jinja2 import Environment, FileSystemLoader
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel

from app.llm.logging_config import (
    configure_llm_logger,
    log_prompt_messages,
    log_response_content,
)
from app.models.domain import CharacterCard, Choice

_TEMPLATES_DIR = Path(__file__).parent / "templates"


class _ChoiceOptions(BaseModel):
    options: list[Choice]


class ChoiceEngineClient:
    def __init__(self, model: BaseChatModel) -> None:
        self._model = model
        self._parser = PydanticOutputParser(pydantic_object=_ChoiceOptions)
        env = Environment(loader=FileSystemLoader(str(_TEMPLATES_DIR)), keep_trailing_newline=True)
        self._system_template = env.get_template("choice_engine_system.j2")
        self._logger = configure_llm_logger("app.llm.choice_engine")

    def _build_system_prompt(
        self,
        plot_direction: str,
        user_character: CharacterCard,
        supporting_characters: list[CharacterCard],
    ) -> str:
        format_instructions = self._parser.get_format_instructions()
        supporting_character_profiles = "\n\n".join(
            c.to_prompt_text() for c in supporting_characters
        )
        return self._system_template.render(
            main_character_profile=user_character.to_prompt_text(),
            supporting_character_profiles=supporting_character_profiles or "(no supporting characters)",
            plot_direction=plot_direction,
            format_instructions=format_instructions,
        )

    async def invoke(
        self,
        story_text: str,
        plot_direction: str,
        user_character: CharacterCard,
        supporting_characters: list[CharacterCard],
    ) -> list[Choice]:
        system_prompt = self._build_system_prompt(plot_direction, user_character, supporting_characters)
        messages = [SystemMessage(system_prompt), HumanMessage(story_text)]
        log_prompt_messages(self._logger, messages)

        response = await self._model.ainvoke(messages)
        log_response_content(self._logger, response.content)
        result = self._parser.parse(response.content)
        return result.options
