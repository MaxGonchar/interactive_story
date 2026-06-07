from app.llm.models import SceneContext
from app.models.domain import CharacterCard, Message, SceneDescription


def test_scene_context_construction():
    scene_description = SceneDescription(
        general_scene_guide="Build tension slowly.",
        writing_style="Gothic horror.",
    )
    character = CharacterCard(
        id="char-1",
        story_id="story-1",
        name="Mila",
    )
    message = Message(id=1, role="user", content="Hello?")

    ctx = SceneContext(
        scene_description=scene_description,
        characters=[character],
        messages=[message],
    )

    assert len(ctx.characters) == 1
    assert ctx.characters[0].name == "Mila"
    assert len(ctx.messages) == 1
    assert ctx.messages[0].content == "Hello?"


def test_scene_context_empty_lists():
    scene_description = SceneDescription(
        general_scene_guide="Keep it calm.",
        writing_style="Pastoral.",
    )

    ctx = SceneContext(
        scene_description=scene_description,
        characters=[],
        messages=[],
    )

    assert ctx.characters == []
    assert ctx.messages == []
