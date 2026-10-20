from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import HumanMessage, SystemMessage

from app.exceptions import LLMError
from app.llm.logging_config import (
    configure_llm_logger,
    log_prompt_messages,
    log_response_content,
)
from app.llm.models import LLMCompletion, parse_llm_completion
from app.llm.prompt_builder import CharacterDrivenPromptBuilder, build_narrator_context


class NarratorClient:
    def __init__(self, model: BaseChatModel) -> None:
        self._model = model
        self._prompt_builder = CharacterDrivenPromptBuilder()
        self._logger = configure_llm_logger("app.llm.narrator")

    async def invoke(
        self,
        story_context: list[str],
        general_scene_guide: str,
        writing_style: str,
        scene_narrations: list[str],
        actor_name: str,
        current_turn: str,
    ) -> LLMCompletion:
        context = build_narrator_context(
            story_context,
            general_scene_guide,
            writing_style,
            scene_narrations,
            actor_name,
            current_turn,
        )
        variables = context.model_dump()
        messages = [
            SystemMessage(self._prompt_builder.render("narrator_system.j2", **variables)),
            HumanMessage(self._prompt_builder.render("narrator_user.j2", **variables)),
        ]
        log_prompt_messages(self._logger, messages)

        response = await self._model.ainvoke(messages)
        if not isinstance(response.content, str) or not response.content.strip():
            raise LLMError("Narrator returned an empty response.")

        log_response_content(self._logger, response.content)
        return parse_llm_completion(response).model_copy(update={"result": response.content})
