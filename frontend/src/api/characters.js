const BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

async function apiFetch(url, options) {
  const response = await fetch(BASE_URL + url, options);
  if (!response.ok) {
    const body = await response.json();
    throw new Error(body.error.message);
  }
  return response.json();
}

export async function getCharacters(storyId) {
  return apiFetch(`/api/stories/${storyId}/characters`);
}
