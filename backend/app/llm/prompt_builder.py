from __future__ import annotations

import re
from pathlib import Path

from jinja2 import Environment, FileSystemLoader
from pydantic import BaseModel

from app.llm.models import SceneContext
from app.models.domain import CharacterCard, CharacterDrivenMessage

# TODO: remove after no stories use the legacy character action format
_LEGACY_CHARACTER_ACTION_FIELD = re.compile(
    r"(?m)^[ \t]*(?P<opening>\*{0,2})(?P<name>INTERNAL|ACTION|SPEECH|TONE):"
    r"(?P<closing>\*{0,2})[ \t]*(?P<value>[^\n]*)"
)
_TEMPLATES_DIR = Path(__file__).parent / "templates"
_CHARACTER_DRIVEN_TEMPLATES_DIR = _TEMPLATES_DIR / "character_driven"


class CharacterDrivenPromptBuilder:
    def __init__(self, templates_dir: Path | None = None) -> None:
        self._env = Environment(
            loader=FileSystemLoader(str(templates_dir or _CHARACTER_DRIVEN_TEMPLATES_DIR)),
            keep_trailing_newline=True,
        )

    def render(self, template_name: str, **context: object) -> str:
        return self._env.get_template(template_name).render(**context)


class CharacterAgentContext(BaseModel):
    character_name: str
    character_profile: str
    accumulated_memories: list[str]
    current_scene_context: str
    player_guidance: str | None = None


def build_character_agent_context(
    character: CharacterCard,
    scene_messages: list[CharacterDrivenMessage],
    player_guidance: str | None = None,
    player_character_id: str | None = None,
) -> CharacterAgentContext:
    return CharacterAgentContext(
        character_name=character.name,
        character_profile=character.to_profile_text(),
        accumulated_memories=list(character.memory),
        current_scene_context=_build_character_scene_context(
            character.id, scene_messages, player_character_id
        ),
        player_guidance=player_guidance or None,
    )


def _legacy_character_action_parts(action: str) -> tuple[str, str] | None:
    fields = list(_LEGACY_CHARACTER_ACTION_FIELD.finditer(action))
    if (
        len(fields) < 2
        or action[: fields[0].start()].strip()
        or fields[0].group("name") != "INTERNAL"
        or not any(field.group("name") == "ACTION" for field in fields)
    ):
        return None

    parsed_fields: list[tuple[str, str, str]] = []
    for index, field in enumerate(fields):
        end = fields[index + 1].start() if index + 1 < len(fields) else len(action)
        value = (field.group("value") + action[field.end() : end]).strip()
        label = f"{field.group('opening')}{field.group('name')}:{field.group('closing')}"
        parsed_fields.append((field.group("name"), label, value))

    internal = next(value for name, _, value in parsed_fields if name == "INTERNAL")
    public_action = "\n\n".join(
        f"{label} {value}" for name, label, value in parsed_fields if name != "INTERNAL"
    )
    return internal, public_action


def _message_internal(
    message: CharacterDrivenMessage,
    owner_character_id: str,
    player_character_id: str | None,
) -> str | None:
    message_input = message.input
    if (
        message_input is None
        or message_input.author != owner_character_id
        or message_input.author == player_character_id
    ):
        return None
    if message_input.internal is not None:
        return message_input.internal
    legacy_parts = _legacy_character_action_parts(message_input.action)
    return legacy_parts[0] if legacy_parts is not None else None


def _message_public_action(message: CharacterDrivenMessage) -> str:
    message_input = message.input
    if message_input is None or message_input.internal is not None:
        return message_input.action if message_input is not None else ""
    legacy_parts = _legacy_character_action_parts(message_input.action)
    return legacy_parts[1] if legacy_parts is not None else message_input.action


def _build_character_scene_context(
    owner_character_id: str,
    messages: list[CharacterDrivenMessage],
    player_character_id: str | None,
) -> str:
    entries: list[str] = []
    for message in messages:
        internal = _message_internal(message, owner_character_id, player_character_id)
        if internal is None:
            entries.append(message.narration)
        else:
            entries.append(
                f"INTERNAL:\n{internal}\n\nNarration:\n{message.narration}"
            )
    return "\n\n".join(entries)


class MemoryAgentContext(BaseModel):
    character_name: str
    character_profile: str
    accumulated_memories: list[str]
    completed_scene: str


def build_scene_transcript(
    messages: list[CharacterDrivenMessage],
    character_names: dict[str, str],
    owner_character_id: str,
    player_character_id: str | None = None,
) -> str:
    entries: list[str] = []
    for message in messages:
        if message.input is None:
            entries.append(message.narration)
            continue
        author = message.input.author
        actor = "Player" if author is None else character_names.get(author, author)
        entry = f"Actor: {actor}\n{_message_public_action(message)}"
        internal = _message_internal(message, owner_character_id, player_character_id)
        if internal is not None:
            entry += f"\n\nINTERNAL:\n{internal}"
        entries.append(f"{entry}\n\nNarration:\n{message.narration}")
    return "\n\n".join(entries)


def build_memory_agent_context(
    character: CharacterCard,
    messages: list[CharacterDrivenMessage],
    character_names: dict[str, str],
    player_character_id: str | None = None,
) -> MemoryAgentContext:
    return MemoryAgentContext(
        character_name=character.name,
        character_profile=character.to_profile_text(),
        accumulated_memories=list(character.memory),
        completed_scene=build_scene_transcript(
            messages, character_names, character.id, player_character_id
        ),
    )


class NarratorContext(BaseModel):
    story_context: str
    general_scene_guide: str
    writing_style: str
    current_scene_context: str
    actor_name: str
    current_turn: str


def build_narrator_context(
    story_context: list[str],
    general_scene_guide: str,
    writing_style: str,
    scene_narrations: list[str],
    actor_name: str,
    current_turn: str,
) -> NarratorContext:
    return NarratorContext(
        story_context="\n".join(f"* {item}" for item in story_context) or "(no context)",
        general_scene_guide=general_scene_guide,
        writing_style=writing_style,
        current_scene_context="\n\n".join(scene_narrations),
        actor_name=actor_name,
        current_turn=current_turn,
    )


class PromptBuilder:
    def __init__(self) -> None:
        env = Environment(loader=FileSystemLoader(str(_TEMPLATES_DIR)), keep_trailing_newline=True)
        self._system_template = env.get_template("scene_system.j2")
        self._narrator_system_template = env.get_template("scene_system_narrator.j2")
        self._config_template = env.get_template("scene_config.j2")

    def build_system_prompt(self, context: SceneContext) -> str:
        context_data = self._build_context_data(context)
        character_profiles = self._build_character_profiles(context)
        scene_configuration = self._config_template.render(
            general_scene_guide=context.scene_description.general_scene_guide,
            writing_style=context.scene_description.writing_style,
        )
        template = self._system_template
        template_context = {
            "context_data": context_data,
            "character_profiles": character_profiles,
            "scene_configuration": scene_configuration,
        }
        if context.user_character is not None:
            template_context["user_character_profile"] = context.user_character.to_prompt_text()
        else:
            template = self._narrator_system_template
        return template.render(
            **template_context,
        )

    def _build_context_data(self, context: SceneContext) -> str:
        if not context.context_data:
            return "(no context)"
        return "\n".join(f"* {item}" for item in context.context_data)

    def _build_character_profiles(self, context: SceneContext) -> str:
        if not context.characters:
            return "(no characters)"
        profiles = [char.to_prompt_text() for char in context.characters]
        return "\n\n".join(profiles)
