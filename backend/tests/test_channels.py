from __future__ import annotations

from pathlib import Path

from app.channels.base import ChannelMessage
from app.channels.manager import ChannelManager


async def test_channel_manager_loads_telegram_config() -> None:
    manager = ChannelManager.from_config_dir(Path(__file__).resolve().parents[2] / "config" / "channels")
    status = await manager.status()
    assert any(item["name"] == "telegram" and item["type"] == "telegram" for item in status)


async def test_disabled_telegram_channel_does_not_send() -> None:
    manager = ChannelManager.from_config_dir(Path(__file__).resolve().parents[2] / "config" / "channels")
    result = await manager.send("telegram", ChannelMessage(recipient="123", text="hello"))
    assert not result.ok
    assert result.error == "channel disabled"
