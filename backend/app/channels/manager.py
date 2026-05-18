from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from app.channels.base import BaseChannel, ChannelMessage, ChannelSendResult
from app.channels.telegram import TelegramChannel


class ChannelManager:
    def __init__(self, channels: list[BaseChannel] | None = None, configured: list[dict[str, Any]] | None = None) -> None:
        self.channels = {channel.name: channel for channel in channels or []}
        self.configured = configured or []

    @classmethod
    def from_config_dir(cls, config_dir: Path) -> "ChannelManager":
        channels: list[BaseChannel] = []
        configured: list[dict[str, Any]] = []
        for path in sorted(config_dir.glob("*.yaml")):
            data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
            name = str(data.get("name") or path.stem)
            channel_type = str(data.get("type") or name)
            enabled = bool(data.get("enabled", False))
            configured.append(
                {
                    "name": name,
                    "config_path": f"channels/{path.name}",
                    "type": channel_type,
                    "enabled": enabled,
                    "bot_token_env": data.get("bot_token_env"),
                    "default_chat_id": data.get("default_chat_id"),
                    "default_chat_id_configured": bool(data.get("default_chat_id")),
                    "api_base": data.get("api_base"),
                    "timeout_seconds": data.get("timeout_seconds"),
                }
            )
            if channel_type == "telegram":
                channels.append(
                    TelegramChannel(
                        name=name,
                        enabled=enabled,
                        bot_token_env=str(data.get("bot_token_env", "TELEGRAM_BOT_TOKEN")),
                        default_chat_id=str(data["default_chat_id"]) if data.get("default_chat_id") else None,
                        api_base=str(data.get("api_base", "https://api.telegram.org")),
                        timeout_seconds=float(data.get("timeout_seconds", 10)),
                    )
                )
        return cls(channels, configured)

    async def status(self) -> list[dict[str, Any]]:
        status: list[dict[str, Any]] = []
        for item in self.configured:
            channel = self.channels.get(str(item["name"]))
            status.append({**item, "active": channel is not None, "healthy": await channel.health() if channel else False})
        return status

    async def send(self, name: str, message: ChannelMessage) -> ChannelSendResult:
        channel = self.channels.get(name)
        if not channel:
            return ChannelSendResult(ok=False, channel=name, error="channel not configured")
        return await channel.send(message)
