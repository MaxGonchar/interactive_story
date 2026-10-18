from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import HumanMessage, SystemMessage

from app.exceptions import LLMError
from app.llm.logging_config import (
    configure_llm_logger,
    log_prompt_messages,
    log_response_content,
)
from app.llm.models import LLMCompletion, parse_llm_completion
from app.llm.prompt_builder import CharacterDrivenPromptBuilder, build_character_agent_context
from app.models.domain import CharacterCard


class CharacterAgentClient:
    def __init__(self, model: BaseChatModel) -> None:
        self._model = model
        self._prompt_builder = CharacterDrivenPromptBuilder()
        self._logger = configure_llm_logger("app.llm.character_agent")

    async def invoke(
        self,
        character: CharacterCard,
        scene_narrations: list[str],
        player_guidance: str | None = None,
    ) -> LLMCompletion:
        context = build_character_agent_context(character, scene_narrations, player_guidance)
        variables = context.model_dump()
        messages = [
            SystemMessage(self._prompt_builder.render("character_agent_system.j2", **variables)),
            HumanMessage(self._prompt_builder.render("character_agent_user.j2", **variables)),
        ]
        log_prompt_messages(self._logger, messages)

        response = await self._model.ainvoke(messages)
        if not isinstance(response.content, str) or not response.content.strip():
            raise LLMError("Character agent returned an empty response.")

        log_response_content(self._logger, response.content)
        return parse_llm_completion(response).model_copy(update={"result": response.content})
