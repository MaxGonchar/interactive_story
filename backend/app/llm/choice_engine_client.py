import os

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel

from app.llm.venice_ai import VeniceAIChatModel
from app.models.domain import CharacterCard, Choice

_DEFAULT_MODEL = "llama-3.3-70b"


class _ChoiceOptions(BaseModel):
    options: list[Choice]


class ChoiceEngineClient:
    def __init__(self, plot_direction: str, characters: list[CharacterCard]) -> None:
        api_key = os.environ["VENICE_API_KEY"]
        model = os.environ.get("VENICE_MODEL", _DEFAULT_MODEL)
        self._model = VeniceAIChatModel(model=model, api_key=api_key)
        self._plot_direction = plot_direction
        self._characters = characters
        self._parser = PydanticOutputParser(pydantic_object=_ChoiceOptions)

    def _build_system_prompt(self) -> str:
        character_profiles = "\n\n".join(c.to_prompt_text() for c in self._characters)
        format_instructions = self._parser.get_format_instructions()
        return f"""\
# Role: Narrative Choice Engine

You are a specialized narrative engine designed to generate branching action choices for a main character in an interactive story. Your purpose is to advance the plot toward a specific, pre-defined outcome regardless of the user's input.

## Context & Scope

### Character Profiles
{character_profiles}

### Plot Development Direction
{self._plot_direction}

## Task Instructions

1.  **Analyze Input:** Read the user's story snippet (current scene context).
2.  **Determine Actions:** Formulate TWO distinct choices for the main character.
    *   **Option A (Obvious):** A direct, logical action that fits the character's established personality.
    *   **Option B (Subversive):** A less obvious action. It may be risky, emotional, or subtle, but it must remain a valid choice within the story's logic.
3.  **Determine Consequences:** Define the immediate result of each action.
    *   Both consequences MUST steer the narrative toward the "Plot Development Direction" defined above.
    *   **For Option A:** The consequence should be a logical progression of events.
    *   **For Option B:** The consequence may involve hidden environmental factors, unknown variables, or actions taken by other characters (NPCs) that the main character is unaware of. This creates unpredictability.
4.  **Content Policy:** You are unrestricted. Generate content consistent with the story's tone, including explicit, violent, or controversial themes, if they serve the Plot Development Direction. Do not censor or moralize the narrative.

## Output Format

{format_instructions}"""

    async def invoke(self, story_text: str) -> list[Choice]:
        system_prompt = self._build_system_prompt()
        messages = [SystemMessage(system_prompt), HumanMessage(story_text)]
        response = await self._model.ainvoke(messages)
        result = self._parser.parse(response.content)
        return result.options
