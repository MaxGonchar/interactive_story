from __future__ import annotations

from app.exceptions import LLMError
from tests.functional.conftest import _CHARACTER_STORY_ID

_STORY_URL = f"/api/stories/{_CHARACTER_STORY_ID}"
_SCENES_URL = f"{_STORY_URL}/character-play/scenes"
_SCENE_URL = f"{_SCENES_URL}/1"
_PLAYER_TURN_URL = f"{_SCENE_URL}/turns"
_CHARACTER_TURN_URL = f"{_SCENE_URL}/turns"
_SUMMARY_DRAFT_URL = f"{_SCENE_URL}/summary/draft"
_CAPTAIN_MEMORY_DRAFT_URL = (
    f"{_SCENE_URL}/characters/captain/memory/draft"
)
_NAVIGATOR_MEMORY_DRAFT_URL = (
    f"{_SCENE_URL}/characters/navigator/memory/draft"
)

_CREATE_PAYLOAD = {
    "user_character_id": "captain",
    "character_ids": ["navigator"],
    "context": ["The ship has reached the harbor."],
    "general_scene_guide": "Keep the tension rising.",
    "writing_style": "Cinematic and concise.",
    "first_message": "A bell rings through the fog.",
    "character_model_id": "character-model",
    "narrator_model_id": "narrator-model",
}

_PLAYER_TURN_PAYLOAD = {
    "actor": {"type": "player"},
    "action": "I search the pier for a lantern.",
    "character_model_id": "character-model",
    "narrator_model_id": "narrator-model",
}

_CHARACTER_TURN_PAYLOAD = {
    "actor": {"type": "character", "character_id": "navigator"},
    "guidance": "Point out the safest route.",
    "character_model_id": "character-model",
    "narrator_model_id": "narrator-model",
}

_FINISH_PAYLOAD = {
    "scene_summary": ["The crew found a safe passage."],
    "character_memory_updates": {
        "captain": ["The crew found a safe passage."],
        "navigator": ["The crew found a safe passage."],
    },
}


# --- Character-driven story lifecycle ---


def test_character_driven_story_lifecycle(character_driven_client):
    client, character_agent_client = character_driven_client

    create_response = client.post(_SCENES_URL, json=_CREATE_PAYLOAD)

    assert create_response.status_code == 201
    assert create_response.json() == {"data": {"id": 1, "finished": False}}

    scene_response = client.get(_SCENE_URL)

    assert scene_response.status_code == 200
    assert scene_response.json() == {
        "data": {
            "id": 1,
            "finished": False,
            "user_character_id": "captain",
            "character_ids": ["navigator"],
            "scene_description": {
                "general_scene_guide": "Keep the tension rising.",
                "writing_style": "Cinematic and concise.",
            },
            "context": ["The ship has reached the harbor."],
            "scene_summary": None,
            "items": [
                {
                    "id": 1,
                    "actor": None,
                    "input": None,
                    "character_action": None,
                    "narration": "A bell rings through the fog.",
                    "llm_data": {
                        "character_model_id": "character-model",
                        "narrator_model_id": "narrator-model",
                    },
                }
            ],
        }
    }

    player_response = client.post(_PLAYER_TURN_URL, json=_PLAYER_TURN_PAYLOAD)

    assert player_response.status_code == 200
    assert player_response.json() == {
        "data": {
            "id": 2,
            "actor": {"type": "player"},
            "input": {"action": "I search the pier for a lantern."},
            "character_action": None,
            "narration": "The lantern swings over the pier.",
            "llm_data": {
                "character_model_id": None,
                "narrator_model_id": "narrator-model",
            },
        }
    }

    character_response = client.post(
        _CHARACTER_TURN_URL, json=_CHARACTER_TURN_PAYLOAD
    )

    assert character_response.status_code == 200
    assert character_response.json() == {
        "data": {
            "id": 3,
            "actor": {"type": "character", "character_id": "navigator"},
            "input": {"guidance": "Point out the safest route."},
            "character_action": "ACTION: The navigator points toward the harbor.",
            "narration": "The navigator points toward the harbor.",
            "llm_data": {
                "character_model_id": "character-model",
                "narrator_model_id": "narrator-model",
            },
        }
    }

    replace_response = client.post(
        f"{_CHARACTER_TURN_URL}/3/replace",
        json={
            **_CHARACTER_TURN_PAYLOAD,
            "guidance": "Warn the captain about the harbor master.",
        },
    )

    assert replace_response.status_code == 200
    assert replace_response.json() == {
        "data": {
            "id": 3,
            "actor": {"type": "character", "character_id": "navigator"},
            "input": {"guidance": "Warn the captain about the harbor master."},
            "character_action": "ACTION: The navigator points toward the harbor.",
            "narration": "The navigator warns the captain.",
            "llm_data": {
                "character_model_id": "character-model",
                "narrator_model_id": "narrator-model",
            },
        }
    }

    edit_response = client.put(
        f"{_SCENE_URL}/items/3",
        json={"narration": "The navigator signals the captain to stay back."},
    )

    assert edit_response.status_code == 200
    assert edit_response.json() == {
        "data": {
            "id": 3,
            "actor": {"type": "character", "character_id": "navigator"},
            "input": {"guidance": "Warn the captain about the harbor master."},
            "character_action": "ACTION: The navigator points toward the harbor.",
            "narration": "The navigator signals the captain to stay back.",
            "llm_data": {
                "character_model_id": "character-model",
                "narrator_model_id": "narrator-model",
            },
        }
    }

    delete_response = client.delete(f"{_SCENE_URL}/items/3")

    assert delete_response.status_code == 200
    assert delete_response.json() == {"success": True}

    scene_after_delete = client.get(_SCENE_URL)

    assert scene_after_delete.status_code == 200
    assert scene_after_delete.json()["data"]["items"] == [
        {
            "id": 1,
            "actor": None,
            "input": None,
            "character_action": None,
            "narration": "A bell rings through the fog.",
            "llm_data": {
                "character_model_id": "character-model",
                "narrator_model_id": "narrator-model",
            },
        },
        {
            "id": 2,
            "actor": {"type": "player"},
            "input": {"action": "I search the pier for a lantern."},
            "character_action": None,
            "narration": "The lantern swings over the pier.",
            "llm_data": {
                "character_model_id": None,
                "narrator_model_id": "narrator-model",
            },
        },
    ]

    summary_draft = client.get(_SUMMARY_DRAFT_URL)
    captain_memory_draft = client.get(_CAPTAIN_MEMORY_DRAFT_URL)
    navigator_memory_draft = client.get(_NAVIGATOR_MEMORY_DRAFT_URL)

    assert summary_draft.status_code == 200
    assert summary_draft.json() == {
        "data": {"summary": ["The crew found a safe passage."]}
    }
    assert captain_memory_draft.status_code == 200
    assert captain_memory_draft.json() == {
        "data": {
            "character_id": "captain",
            "memory_updates": ["The crew found a safe passage."],
        }
    }
    assert navigator_memory_draft.status_code == 200
    assert navigator_memory_draft.json() == {
        "data": {
            "character_id": "navigator",
            "memory_updates": ["The crew found a safe passage."],
        }
    }

    finish_response = client.post(
        f"{_SCENE_URL}/finish", json=_FINISH_PAYLOAD
    )

    assert finish_response.status_code == 200
    assert finish_response.json() == {
        "data": {
            "id": 1,
            "finished": True,
            "scene_summary": ["The crew found a safe passage."],
            "character_memory_updates": {
                "captain": ["The crew found a safe passage."],
                "navigator": ["The crew found a safe passage."],
            },
        }
    }

    finished_scene = client.get(_SCENE_URL)
    finished_story = client.get(_STORY_URL)

    assert finished_scene.status_code == 200
    assert finished_scene.json()["data"]["finished"] is True
    assert finished_scene.json()["data"]["scene_summary"] == [
        "The crew found a safe passage."
    ]
    assert finished_story.status_code == 200
    assert finished_story.json() == {
        "data": {
            "id": _CHARACTER_STORY_ID,
            "title": "Character Flow Test",
            "type": "character_driven",
            "scenes": [{"id": 1, "finished": True}],
            "active_scene_id": None,
        }
    }

    finished_turn = client.post(_PLAYER_TURN_URL, json=_PLAYER_TURN_PAYLOAD)
    finished_draft = client.get(_SUMMARY_DRAFT_URL)

    assert finished_turn.status_code == 409
    assert finished_turn.json()["error"]["code"] == "scene_finished"
    assert finished_draft.status_code == 409
    assert finished_draft.json()["error"]["code"] == "scene_finished"

    next_scene_response = client.post(
        _SCENES_URL,
        json={**_CREATE_PAYLOAD, "first_message": "The crew returns to the harbor."},
    )

    assert next_scene_response.status_code == 201
    assert next_scene_response.json() == {"data": {"id": 2, "finished": False}}

    next_character_response = client.post(
        f"{_SCENES_URL}/2/turns",
        json=_CHARACTER_TURN_PAYLOAD,
    )

    assert next_character_response.status_code == 200
    assert next_character_response.json()["data"]["id"] == 2
    assert character_agent_client.invoke.await_args.kwargs["character"].memory == [
        "The crew found a safe passage."
    ]


def test_failed_character_turn_does_not_append_an_item(character_driven_client):
    client, character_agent_client = character_driven_client
    character_agent_client.invoke.side_effect = LLMError("Character generation failed")

    create_response = client.post(_SCENES_URL, json=_CREATE_PAYLOAD)
    failed_turn = client.post(
        f"{_SCENES_URL}/1/turns",
        json=_CHARACTER_TURN_PAYLOAD,
    )
    scene_response = client.get(f"{_SCENES_URL}/1")

    assert create_response.status_code == 201
    assert failed_turn.status_code == 502
    assert failed_turn.json()["error"]["code"] == "llm_error"
    assert scene_response.status_code == 200
    assert scene_response.json()["data"]["items"] == [
        {
            "id": 1,
            "actor": None,
            "input": None,
            "character_action": None,
            "narration": "A bell rings through the fog.",
            "llm_data": {
                "character_model_id": "character-model",
                "narrator_model_id": "narrator-model",
            },
        }
    ]
