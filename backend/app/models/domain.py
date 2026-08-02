from __future__ import annotations

from typing import Literal

from pydantic import BaseModel

StoryType = Literal["scene", "choice_driven"]


class StoryIndexItem(BaseModel):
    id: str
    title: str
    created_at: str
    type: StoryType


class SceneRef(BaseModel):
    id: int
    finished: bool


class StoryMeta(BaseModel):
    id: str
    title: str
    scenes: list[SceneRef]
    active_scene_id: int | None


class CharacterCard(BaseModel):
    id: str
    name: str
    features: dict[str, str | list[str]] = {}
    memory: list[str] = []

    def to_prompt_text(self) -> str:
        lines: list[str] = [f"## {self.name}"]
        for key, value in self.features.items():
            heading = key.replace("_", " ").title()
            lines.append(f"### {heading}")
            if isinstance(value, list):
                for item in value:
                    lines.append(f"- {item}")
            else:
                lines.append(value)
        if self.memory:
            lines.append("### Memory")
            for entry in self.memory:
                lines.append(f"- {entry}")
        return "\n".join(lines)


class SceneDescription(BaseModel):
    general_scene_guide: str
    writing_style: str


class SceneMetadata(BaseModel):
    id: int
    story_id: str
    character_ids: list[str]
    user_character_id: str
    finished: bool
    scene_description: SceneDescription
    scene_summary: list[str] | None = None
    context: list[str] | None = None


class Message(BaseModel):
    id: int
    role: Literal["user", "assistant"]
    content: str


class Choice(BaseModel):
    action: str
    consequence: str


class Step(BaseModel):
    id: int
    incoming_choice: Choice | None
    text: str
    choices: list[Choice]


class ChoiceDrivenStoryMeta(BaseModel):
    id: str
    title: str
    writing_style: str
    plot_directions: list[str]
    user_character_id: str
    character_ids: list[str]
