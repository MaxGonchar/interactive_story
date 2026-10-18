from __future__ import annotations

from pathlib import Path

from jinja2 import Environment, FileSystemLoader

from app.llm.models import SceneContext

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
