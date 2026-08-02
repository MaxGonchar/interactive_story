import os
from pathlib import Path

from jinja2 import Environment, FileSystemLoader
from langchain_core.messages import HumanMessage, SystemMessage

from app.llm.venice_ai import VeniceAIChatModel
from app.models.domain import CharacterCard

_DEFAULT_MODEL = "llama-3.3-70b"
_TEMPLATES_DIR = Path(__file__).parent / "templates"


class StoryEngineClient:
    def __init__(
        self,
        user_character: CharacterCard,
        supporting_characters: list[CharacterCard],
        writing_style: str,
    ) -> None:
        api_key = os.environ["VENICE_API_KEY"]
        model = os.environ.get("VENICE_MODEL", _DEFAULT_MODEL)
        self._model = VeniceAIChatModel(model=model, api_key=api_key)
        self._user_character = user_character
        self._supporting_characters = supporting_characters
        self._writing_style = writing_style
        env = Environment(loader=FileSystemLoader(str(_TEMPLATES_DIR)), keep_trailing_newline=True)
        self._system_template = env.get_template("story_engine_system.j2")
        self._user_template = env.get_template("story_engine_user.j2")

    def _build_system_prompt(self) -> str:
        supporting_character_profiles = "\n\n".join(
            c.to_prompt_text() for c in self._supporting_characters
        )
        return self._system_template.render(
            main_character_profile=self._user_character.to_prompt_text(),
            supporting_character_profiles=supporting_character_profiles or "(no supporting characters)",
            writing_style=self._writing_style,
        )

    async def invoke(self, story_text: str, action: str, consequence: str) -> str:
        system_prompt = self._build_system_prompt()
        user_message = self._user_template.render(
            story_text=story_text,
            action=action,
            consequence=consequence,
        )
        messages = [SystemMessage(system_prompt), HumanMessage(user_message)]
        response = await self._model.ainvoke(messages)
        return response.content
