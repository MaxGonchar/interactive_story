
import os
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage

from app.llm.models import SceneContext
from app.llm.prompt_builder import PromptBuilder
from app.llm.venice_ai import VeniceAIChatModel

_DEFAULT_MODEL = "llama-3.3-70b"


class SceneLLMClient:
    def __init__(self) -> None:
        api_key = os.environ["VENICE_API_KEY"]
        model = os.environ.get("VENICE_MODEL", _DEFAULT_MODEL)
        self._model = VeniceAIChatModel(model=model, api_key=api_key)
        self._prompt_builder = PromptBuilder()

    async def invoke(self, context: SceneContext, user_message: str) -> str:
        system_prompt = self._prompt_builder.build_system_prompt(context)
        history_msgs = context.messages
        history = [
            AIMessage(m.content) if m.role == "assistant" else HumanMessage(m.content)
            for m in history_msgs
        ]
        messages = [SystemMessage(system_prompt)] + history + [HumanMessage(user_message)]

        print("=== MESSAGES ===")
        for m in messages:
            print(f"{m.type.upper()}: {m.content}")
        print("=== END MESSAGES ===")

        response = await self._model.ainvoke(messages)
        return response.content
