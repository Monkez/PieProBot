from __future__ import annotations

from abc import ABC, abstractmethod
from typing import AsyncIterator

from pydantic import BaseModel


class ProviderResponse(BaseModel):
    content: str
    model: str
    input_tokens: int = 0
    output_tokens: int = 0
    cost_estimate: float = 0.0


class BaseLLMProvider(ABC):
    name: str

    @abstractmethod
    async def chat(self, messages: list[dict[str, str]], model: str | None = None) -> ProviderResponse:
        raise NotImplementedError

    async def stream(self, messages: list[dict[str, str]], model: str | None = None) -> AsyncIterator[str]:
        response = await self.chat(messages, model)
        for token in response.content.split():
            yield token + " "

    async def embed(self, text: str) -> list[float]:
        return [float((sum(text.encode("utf-8")) % 997) / 997)]

    async def estimate_tokens(self, text: str) -> int:
        return max(1, len(text.split()))

    async def health(self) -> bool:
        return True

