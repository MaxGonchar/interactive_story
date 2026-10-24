from langchain_core.exceptions import OutputParserException
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel

from app.exceptions import LLMError
from app.llm.logging_config import (
    configure_llm_logger,
    log_prompt_messages,
    log_response_content,
)
from app.llm.models import LLMCompletion, parse_llm_completion
from app.llm.prompt_builder import CharacterDrivenPromptBuilder, build_memory_agent_context
from app.models.domain import CharacterCard, CharacterDrivenMessage


class _Memories(BaseModel):
    items: list[str]


class MemoryAgentClient:
    def __init__(self, model: BaseChatModel) -> None:
        self._model = model
        self._parser = PydanticOutputParser(pydantic_object=_Memories)
        self._prompt_builder = CharacterDrivenPromptBuilder()
        self._logger = configure_llm_logger("app.llm.memory_agent")

    async def invoke(
        self,
        character: CharacterCard,
        messages: list[CharacterDrivenMessage],
        character_names: dict[str, str],
    ) -> LLMCompletion:
        variables = build_memory_agent_context(character, messages, character_names).model_dump()
        prompt = [
            SystemMessage(self._prompt_builder.render("memory_agent_system.j2", **variables)),
            HumanMessage(self._prompt_builder.render("memory_agent_user.j2", **variables)),
        ]
        log_prompt_messages(self._logger, prompt)

        response = await self._model.ainvoke(prompt)
        if not isinstance(response.content, str):
            raise TypeError("Memory agent model returned non-text content.")

        log_response_content(self._logger, response.content)
        try:
            result = self._parser.parse(response.content)
        except OutputParserException as exc:
            raise LLMError("Memory agent returned invalid structured output.") from exc
        return parse_llm_completion(response).model_copy(update={"result": result.items})
