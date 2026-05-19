from __future__ import annotations

import os

import httpx

from app.providers.base import BaseLLMProvider, ProviderResponse


class OpenAICompatibleProvider(BaseLLMProvider):
    def __init__(
        self,
        name: str,
        base_url: str,
        api_key_env: str,
        default_model: str,
        timeout_seconds: float = 120,
    ) -> None:
        self.name = name
        self.base_url = base_url.rstrip("/")
        self.api_key_env = api_key_env
        self.default_model = default_model
        self.timeout_seconds = timeout_seconds

    async def chat(self, messages: list[dict[str, str]], model: str | None = None) -> ProviderResponse:
        api_key = os.getenv(self.api_key_env, "")
        headers = {"Authorization": f"Bearer {api_key}"} if api_key else {}
        payload = {"model": model or self.default_model, "messages": messages}
        try:
            async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
                response = await client.post(f"{self.base_url}/chat/completions", json=payload, headers=headers)
                response.raise_for_status()
        except httpx.TimeoutException as exc:
            raise RuntimeError(f"{self.name} timed out after {self.timeout_seconds:g}s") from exc
        except httpx.HTTPStatusError as exc:
            detail = exc.response.text[:500]
            raise RuntimeError(f"{self.name} returned HTTP {exc.response.status_code}: {detail}") from exc
        except httpx.RequestError as exc:
            raise RuntimeError(f"{self.name} request failed: {exc!r}") from exc
        data = response.json()
        try:
            content = data["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as exc:
            raise RuntimeError(f"{self.name} returned an invalid chat response shape") from exc
        usage = data.get("usage", {})
        return ProviderResponse(
            content=content,
            model=payload["model"],
            input_tokens=usage.get("prompt_tokens", 0),
            output_tokens=usage.get("completion_tokens", 0),
        )
