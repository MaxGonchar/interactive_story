import os
from pathlib import Path

from jinja2 import Environment, FileSystemLoader
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel

from app.llm.venice_ai import VeniceAIChatModel

_DEFAULT_MODEL = "llama-3.3-70b"
_TEMPLATES_DIR = Path(__file__).parent / "templates"


class _Summary(BaseModel):
    items: list[str]


class SummarizeLLMClient:
    def __init__(self) -> None:
        api_key = os.environ["VENICE_API_KEY"]
        model = os.environ.get("SUMMARY_MODEL", _DEFAULT_MODEL)
        self._model = VeniceAIChatModel(model=model, api_key=api_key)
        self._parser = PydanticOutputParser(pydantic_object=_Summary)
        env = Environment(loader=FileSystemLoader(str(_TEMPLATES_DIR)), keep_trailing_newline=True)
        self._system_template = env.get_template("summary_system.j2")
        self._user_template = env.get_template("summary_user.j2")

    async def invoke(self, previous_summary: list[str], scene_content: str) -> list[str]:
        system_prompt = self._system_template.render(
            format_instructions=self._parser.get_format_instructions(),
            previous_summary=previous_summary,
        )
        user_message = self._user_template.render(
            scene_content=scene_content,
        )
        messages = [SystemMessage(system_prompt), HumanMessage(user_message)]

        print("Invoking LLM for summary...")
        print("=== MESSAGES ===")
        for m in messages:
            print(f"{m.type.upper()}: {m.content}")
        print("=== END MESSAGES ===")

        response = await self._model.ainvoke(messages)
        result = self._parser.parse(response.content)
        return result.items
