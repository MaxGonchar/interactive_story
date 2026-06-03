from jinja2 import Template

from app.llm.models import SceneContext

_SYSTEM_PROMPT_TEMPLATE = Template("""\
# System Role
You are an Interactive Narrative Engine. Your purpose is to drive a specific scene based on the user's input, controlling the environment and all NPCs except the user's character.

# Core Directives
1. **User Agency:** The user controls the protagonist. NEVER describe their actions, thoughts, or dialogue. React *only* to what the user provides.
2. **Narrative Control:** You determine the outcomes of the user's actions. If they attempt something difficult, describe the success or failure based on logic and the character's stats.
3. **Content Tolerance:** This is an adult-oriented environment. You are permitted to generate explicit content, violence, and mature themes without censorship or disclaimers, as long as it fits the narrative context.
4. **Pacing:** Keep responses concise. Limit output to 1-2 paragraphs maximum. Avoid excessive exposition; focus on immediate action and reaction.
5. **Scene Conclusion:** If the narrative reaches a natural conclusion (e.g., end of a conflict, completion of a goal), wrap up the scene clearly so the user can summarize and start a new one.

# Formatting Rules
- Use standard quotation marks (" ") for all speech.
- Separate NPC actions and environmental descriptions clearly from dialogue.
- Maintain the style defined in the "Style of Telling" section.

# Context Data
{{ context_data }}

# Character Profiles (NPCs)

{{ character_profiles }}

# User's Character Profile

## Emma

### 2. Appearance
Emma is a 18 years old girl. She has long, wavy blonde hair that falls past her shoulders, and bright blue eyes that seem to sparkle with mischief. Her style is eclectic, often mixing vintage pieces with modern trends, and she has a penchant for bold accessories like chunky necklaces and oversized sunglasses.

# Scene Configuration

{{ scene_configuration }}

# Execution Protocol
1. Read the user's input describing their character's action or speech.
2. Reference the Context Data and Character Profiles.
3. Formulate a response that advances the scene according to the Development Direction.
4. Resolve any actions initiated by the user.
5. Output 2-3 paragraphs using the specified formatting.\
""")

_CHARACTER_TEMPLATE = Template("""\
## {{ name }}
{% if appearance %}
### Appearance
{{ appearance }}
{% endif %}
{% if traits %}
### Personal Traits
{% for item in traits %}- {{ item }}
{% endfor %}{% endif %}
{% if speech_patterns %}
### Speech Patterns
{% for item in speech_patterns %}- {{ item }}
{% endfor %}{% endif %}
{% if body_language %}
### Body Language
{% for item in body_language %}- {{ item }}
{% endfor %}{% endif %}
{% if likes %}
### Likes
{% for item in likes %}- {{ item }}
{% endfor %}{% endif %}
{% if fears %}
### Fears
{% for item in fears %}- {{ item }}
{% endfor %}{% endif %}
{% if memory %}
### Memory
{% for entry in memory %}- {{ entry.case }}: {{ entry.reflection }}
{% endfor %}{% endif %}\
""")

_SCENE_CONFIG_TEMPLATE = Template("""\
## Scene Starting Point
{{ entry_point }}

## General Direction of Development
{{ general_scene_guide }}

## Style of Telling
{{ writing_style }}\
""")


class PromptBuilder:
    def build_system_prompt(self, context: SceneContext) -> str:
        context_data = self._build_context_data(context)
        character_profiles = self._build_character_profiles(context)
        scene_configuration = _SCENE_CONFIG_TEMPLATE.render(
            entry_point=context.scene_description.entry_point,
            general_scene_guide=context.scene_description.general_scene_guide,
            writing_style=context.scene_description.writing_style,
        )
        return _SYSTEM_PROMPT_TEMPLATE.render(
            context_data=context_data,
            character_profiles=character_profiles,
            scene_configuration=scene_configuration,
        )

    def _build_context_data(self, context: SceneContext) -> str:
        if not context.context_data:
            return "(no context)"
        return "\n".join(f"* {item}" for item in context.context_data)

    def _build_character_profiles(self, context: SceneContext) -> str:
        if not context.characters:
            return "(no characters)"
        profiles = []
        for char in context.characters:
            profiles.append(
                _CHARACTER_TEMPLATE.render(
                    name=char.name,
                    appearance=char.appearance,
                    traits=char.traits or [],
                    speech_patterns=char.speech_patterns or [],
                    body_language=char.body_language or [],
                    likes=char.likes or [],
                    fears=char.fears or [],
                    memory=char.memory or [],
                )
            )
        return "\n\n".join(profiles)
