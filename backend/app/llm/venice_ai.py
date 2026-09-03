import asyncio
import logging
from typing import Any, Optional

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage
from langchain_core.outputs import ChatGeneration, ChatResult
from pydantic import PrivateAttr

from app.llm.venice_client import VeniceClient

logger = logging.getLogger(__name__)

_MESSAGE_ROLE_MAP = {
    SystemMessage: "system",
    HumanMessage: "user",
    AIMessage: "assistant",
}


class VeniceAIChatModel(BaseChatModel):
    model: str
    api_key: str
    temperature: float = 0
    max_tokens: Optional[int] = None

    _client: VeniceClient = PrivateAttr()

    def model_post_init(self, __context: Any) -> None:
        self._client = VeniceClient(api_key=self.api_key)

    @property
    def _llm_type(self) -> str:
        return "venice-ai"

    def _prepare_request_payload(self, messages: list[BaseMessage]) -> dict:
        formatted = []
        for msg in messages:
            role = _MESSAGE_ROLE_MAP.get(type(msg))
            if role is None:
                raise ValueError(
                    f"Unsupported message type: {type(msg).__name__}. "
                    f"Expected one of: SystemMessage, HumanMessage, AIMessage."
                )
            formatted.append({"role": role, "content": msg.content})

        payload: dict = {
            "model": self.model,
            "messages": formatted,
            "temperature": self.temperature,
            "venice_parameters": {"include_venice_system_prompt": False},
        }
        if self.max_tokens is not None:
            payload["max_tokens"] = self.max_tokens

        logger.debug(
            f"LLM request model={self.model} temperature={self.temperature} "
            f"max_tokens={self.max_tokens} message_count={len(formatted)}"
        )

        return payload

    async def _agenerate(
        self,
        messages: list[BaseMessage],
        stop: Optional[list[str]] = None,
        run_manager: Any = None,
        **kwargs: Any,
    ) -> ChatResult:
        payload = self._prepare_request_payload(messages)
        content = await self._client.chat_complete(payload)
        generation = ChatGeneration(message=AIMessage(content=content), text=content)
        return ChatResult(generations=[generation])

    def _generate(
        self,
        messages: list[BaseMessage],
        stop: Optional[list[str]] = None,
        run_manager: Any = None,
        **kwargs: Any,
    ) -> ChatResult:
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(
            self._agenerate(messages, stop=stop, run_manager=run_manager, **kwargs)
        )
