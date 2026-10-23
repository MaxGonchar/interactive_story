const BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

async function apiFetch(url, options) {
  const response = await fetch(BASE_URL + url, options);
  if (!response.ok) {
    const body = await response.json();
    throw new Error(body.error.message);
  }
  return response.json();
}

export async function createCharacterScene(storyId, payload) {
  return apiFetch(`/api/stories/${storyId}/character-play/scenes`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
}

export async function getCharacterScene(storyId, sceneId) {
  return apiFetch(
    `/api/stories/${storyId}/character-play/scenes/${sceneId}`
  );
}

export async function submitCharacterTurn(storyId, sceneId, payload) {
  return apiFetch(
    `/api/stories/${storyId}/character-play/scenes/${sceneId}/turns`,
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    }
  );
}

export async function replaceCharacterTurn(storyId, sceneId, itemId, payload) {
  return apiFetch(
    `/api/stories/${storyId}/character-play/scenes/${sceneId}/turns/${itemId}/replace`,
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    }
  );
}

export async function editCharacterSceneItem(
  storyId,
  sceneId,
  itemId,
  narration
) {
  return apiFetch(
    `/api/stories/${storyId}/character-play/scenes/${sceneId}/items/${itemId}`,
    {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ narration }),
    }
  );
}

export async function deleteCharacterSceneItem(storyId, sceneId, itemId) {
  return apiFetch(
    `/api/stories/${storyId}/character-play/scenes/${sceneId}/items/${itemId}`,
    { method: "DELETE" }
  );
}

export async function getCharacterSceneSummaryDraft(storyId, sceneId) {
  return apiFetch(
    `/api/stories/${storyId}/character-play/scenes/${sceneId}/summary/draft`
  );
}

export async function getCharacterMemoryDraft(storyId, sceneId, characterId) {
  return apiFetch(
    `/api/stories/${storyId}/character-play/scenes/${sceneId}/characters/${characterId}/memory/draft`
  );
}

export async function finishCharacterScene(
  storyId,
  sceneId,
  sceneSummary,
  characterMemoryUpdates
) {
  return apiFetch(
    `/api/stories/${storyId}/character-play/scenes/${sceneId}/finish`,
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        scene_summary: sceneSummary,
        character_memory_updates: characterMemoryUpdates,
      }),
    }
  );
}
