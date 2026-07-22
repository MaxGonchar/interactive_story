from __future__ import annotations

from pathlib import Path

from jinja2 import Environment, FileSystemLoader

from app.llm.models import SceneContext

_TEMPLATES_DIR = Path(__file__).parent / "templates"


class PromptBuilder:
    def __init__(self) -> None:
        env = Environment(loader=FileSystemLoader(str(_TEMPLATES_DIR)), keep_trailing_newline=True)
        self._system_template = env.get_template("scene_system.j2")
        self._config_template = env.get_template("scene_config.j2")

    def build_system_prompt(self, context: SceneContext) -> str:
        context_data = self._build_context_data(context)
        character_profiles = self._build_character_profiles(context)
        scene_configuration = self._config_template.render(
            general_scene_guide=context.scene_description.general_scene_guide,
            writing_style=context.scene_description.writing_style,
        )
        user_character_profile = context.user_character.to_prompt_text()
        return self._system_template.render(
            context_data=context_data,
            character_profiles=character_profiles,
            scene_configuration=scene_configuration,
            user_character_profile=user_character_profile,
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
