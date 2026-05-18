from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from pydantic import BaseModel, Field


class ChannelMessage(BaseModel):
    recipient: str | None = None
    text: str
    metadata: dict[str, Any] = Field(default_factory=dict)


class ChannelSendResult(BaseModel):
    ok: bool
    channel: str
    message_id: str | None = None
    error: str | None = None


class BaseChannel(ABC):
    name: str
    enabled: bool

    @abstractmethod
    async def send(self, message: ChannelMessage) -> ChannelSendResult:
        raise NotImplementedError

    async def health(self) -> bool:
        return self.enabled
