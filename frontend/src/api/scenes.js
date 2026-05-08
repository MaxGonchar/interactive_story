const SCENES = {
  3: {
    id: 3,
    finished: false,
    scene_description: {
      entry_point: "Fog rolls over the black harbor as bells ring in distance.",
      general_scene_guide:
        "Keep tension rising with small discoveries and choices.",
      writing_style: "Cinematic, sensory details, concise dialog turns.",
    },
    scene_summary: null,
    messages: [
      {
        id: 1,
        role: "assistant",
        content: "You step into the foggy harbor. The air smells of salt and smoke.",
      },
      {
        id: 2,
        role: "user",
        content: "I look for the nearest light source.",
      },
      {
        id: 3,
        role: "assistant",
        content: "A lantern swings near a wooden post at the end of the pier.",
      },
    ],
  },
};

export async function getScene(storyId, sceneId) {
  return { data: SCENES[sceneId] };
}

export async function playScene() {
  throw new Error("not implemented");
}

export async function editMessage() {
  throw new Error("not implemented");
}

export async function deleteMessage() {
  throw new Error("not implemented");
}

export async function finishScene() {
  throw new Error("not implemented");
}
