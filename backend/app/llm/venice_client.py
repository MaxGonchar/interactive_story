import httpx


class VeniceClient:
    def __init__(self, api_key: str) -> None:
        self.base_url = "https://api.venice.ai/api/v1"
        self.timeout = 60.0
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

    async def chat_complete(self, payload: dict) -> str:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/chat/completions",
                json=payload,
                headers=self.headers,
                timeout=self.timeout,
            )
            response.raise_for_status()

        data = response.json()
        choices = data.get("choices")
        if not choices:
            raise ValueError(
                f"Unexpected response shape: 'choices' missing or empty. Got: {data}"
            )

        return choices[0]["message"]["content"]
