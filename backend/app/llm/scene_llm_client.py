
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage

from app.llm.logging_config import (
    configure_llm_logger,
    log_prompt_messages,
    log_response_content,
)
from app.llm.models import SceneContext
from app.llm.prompt_builder import PromptBuilder


class SceneLLMClient:
    def __init__(self, model: BaseChatModel) -> None:
        self._model = model
        self._prompt_builder = PromptBuilder()
        self._logger = configure_llm_logger("app.llm.scene")

    async def invoke(self, context: SceneContext, user_message: str) -> str:
        system_prompt = self._prompt_builder.build_system_prompt(context)
        history_msgs = context.messages
        history = [
            AIMessage(m.content) if m.role == "assistant" else HumanMessage(m.content)
            for m in history_msgs
        ]
        messages = [SystemMessage(system_prompt)] + history + [HumanMessage(user_message)]
        log_prompt_messages(self._logger, messages)

        response = await self._model.ainvoke(messages)
        log_response_content(self._logger, response.content)
        return response.content
