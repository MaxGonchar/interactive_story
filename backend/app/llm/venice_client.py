import httpx

from app.exceptions import LLMError


class VeniceClient:
    def __init__(self, api_key: str) -> None:
        self.base_url = "https://api.venice.ai/api/v1"
        self.timeout = 300.0
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

    async def chat_complete(self, payload: dict) -> str:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    json=payload,
                    headers=self.headers,
                    timeout=self.timeout,
                )
                response.raise_for_status()
        except httpx.HTTPStatusError as e:
            raise LLMError(f"LLM API returned {e.response.status_code}") from e
        except httpx.RequestError as e:
            raise LLMError(f"LLM request failed: {e}") from e

        data = response.json()
        choices = data.get("choices")
        if not choices:
            raise LLMError(
                f"Unexpected response shape: 'choices' missing or empty. Got: {data}"
            )

        return choices[0]["message"]["content"]
