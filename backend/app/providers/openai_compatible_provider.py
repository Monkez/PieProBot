from __future__ import annotations

import os

import httpx

from app.providers.base import BaseLLMProvider, ProviderResponse


class OpenAICompatibleProvider(BaseLLMProvider):
    def __init__(self, name: str, base_url: str, api_key_env: str, default_model: str) -> None:
        self.name = name
        self.base_url = base_url.rstrip("/")
        self.api_key_env = api_key_env
        self.default_model = default_model

    async def chat(self, messages: list[dict[str, str]], model: str | None = None) -> ProviderResponse:
        api_key = os.getenv(self.api_key_env, "")
        headers = {"Authorization": f"Bearer {api_key}"} if api_key else {}
        payload = {"model": model or self.default_model, "messages": messages}
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(f"{self.base_url}/chat/completions", json=payload, headers=headers)
            response.raise_for_status()
        data = response.json()
        content = data["choices"][0]["message"]["content"]
        usage = data.get("usage", {})
        return ProviderResponse(
            content=content,
            model=payload["model"],
            input_tokens=usage.get("prompt_tokens", 0),
            output_tokens=usage.get("completion_tokens", 0),
        )

