const BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

async function apiFetch(url, options) {
  const response = await fetch(BASE_URL + url, options);
  if (!response.ok) {
    const body = await response.json();
    throw new Error(body.error.message);
  }
  return response.json();
}

export async function getChoiceDrivenPlay(storyId) {
  return apiFetch(`/api/stories/${storyId}/choice-play`);
}

export async function generateChoices(storyId) {
  return apiFetch(`/api/stories/${storyId}/choice-play/generate-choices`, {
    method: "POST",
  });
}

export async function regenerateChoices(storyId) {
  return apiFetch(`/api/stories/${storyId}/choice-play/regenerate-choices`, {
    method: "POST",
  });
}

export async function selectChoice(storyId, action, consequence) {
  return apiFetch(`/api/stories/${storyId}/choice-play/select-choice`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ action, consequence }),
  });
}

export async function editStepText(storyId, stepId, text) {
  return apiFetch(`/api/stories/${storyId}/choice-play/steps/${stepId}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text }),
  });
}

export async function returnToStep(storyId, stepId) {
  return apiFetch(
    `/api/stories/${storyId}/choice-play/steps/${stepId}/forward`,
    { method: "DELETE" }
  );
}
