from __future__ import annotations

from app.providers.base import BaseLLMProvider, ProviderResponse


class LocalProvider(BaseLLMProvider):
    name = "local"

    async def chat(self, messages: list[dict[str, str]], model: str | None = None) -> ProviderResponse:
        latest = messages[-1]["content"] if messages else ""
        return ProviderResponse(
            content=f"LocalProvider processed: {latest}",
            model=model or "local-mock",
            input_tokens=sum(len(m.get("content", "").split()) for m in messages),
            output_tokens=max(1, len(latest.split())),
        )

