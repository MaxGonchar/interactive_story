const BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

async function apiFetch(url, options) {
  const response = await fetch(BASE_URL + url, options);
  if (!response.ok) {
    const body = await response.json();
    throw new Error(body.error.message);
  }
  return response.json();
}

export async function getScene(storyId, sceneId) {
  return apiFetch(`/api/stories/${storyId}/scenes/${sceneId}`);
}

export async function playScene(storyId, sceneId, content) {
  return apiFetch(`/api/stories/${storyId}/scenes/${sceneId}/play`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ content }),
  });
}

export async function editMessage(storyId, sceneId, messageId, content) {
  return apiFetch(
    `/api/stories/${storyId}/scenes/${sceneId}/messages/${messageId}`,
    {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ content }),
    }
  );
}

export async function deleteMessage(storyId, sceneId, messageId) {
  return apiFetch(
    `/api/stories/${storyId}/scenes/${sceneId}/messages/${messageId}`,
    { method: "DELETE" }
  );
}

export async function finishScene(storyId, sceneId, sceneSummary) {
  return apiFetch(`/api/stories/${storyId}/scenes/${sceneId}/finish`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ scene_summary: sceneSummary }),
  });
}

export async function regenerateLastAssistantMessage(storyId, sceneId) {
  return apiFetch(
    `/api/stories/${storyId}/scenes/${sceneId}/regenerate`,
    { method: "POST" }
  );
}

export async function generateSceneSummary(storyId, sceneId) {
  return apiFetch(`/api/stories/${storyId}/scenes/${sceneId}/summarize`);
}

export async function createScene(storyId, payload) {
  return apiFetch(`/api/stories/${storyId}/scenes`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
}
