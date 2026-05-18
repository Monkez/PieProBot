from __future__ import annotations

import os
from typing import Any

import httpx

from app.channels.base import BaseChannel, ChannelMessage, ChannelSendResult


class TelegramChannel(BaseChannel):
    def __init__(
        self,
        name: str = "telegram",
        enabled: bool = False,
        bot_token_env: str = "TELEGRAM_BOT_TOKEN",
        default_chat_id: str | None = None,
        api_base: str = "https://api.telegram.org",
        timeout_seconds: float = 10,
    ) -> None:
        self.name = name
        self.enabled = enabled
        self.bot_token_env = bot_token_env
        self.default_chat_id = default_chat_id
        self.api_base = api_base.rstrip("/")
        self.timeout_seconds = timeout_seconds

    async def send(self, message: ChannelMessage) -> ChannelSendResult:
        if not self.enabled:
            return ChannelSendResult(ok=False, channel=self.name, error="channel disabled")
        token = os.getenv(self.bot_token_env, "")
        if not token:
            return ChannelSendResult(ok=False, channel=self.name, error=f"missing env {self.bot_token_env}")
        chat_id = message.recipient or self.default_chat_id
        if not chat_id:
            return ChannelSendResult(ok=False, channel=self.name, error="missing telegram chat_id")
        payload: dict[str, Any] = {"chat_id": chat_id, "text": message.text}
        async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
            response = await client.post(f"{self.api_base}/bot{token}/sendMessage", json=payload)
            response.raise_for_status()
        data = response.json()
        result = data.get("result", {}) if isinstance(data, dict) else {}
        return ChannelSendResult(ok=bool(data.get("ok", True)), channel=self.name, message_id=str(result.get("message_id")) if result.get("message_id") is not None else None)

    async def health(self) -> bool:
        return self.enabled and bool(os.getenv(self.bot_token_env, ""))
