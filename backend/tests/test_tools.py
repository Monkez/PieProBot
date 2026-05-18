from __future__ import annotations

from pathlib import Path

from app.tools.registry import ToolRegistry


async def test_tool_registry_loading_and_schema() -> None:
    registry = ToolRegistry(Path(__file__).resolve().parents[2] / "config" / "tools")
    registry.load()
    names = {tool.name for tool in registry.list()}
    assert {"echo", "filesystem", "shell", "memory.search", "self_update.status"}.issubset(names)
    assert registry.get("shell").enabled is False


async def test_tool_timeout_or_permission_failure() -> None:
    registry = ToolRegistry(Path(__file__).resolve().parents[2] / "config" / "tools")
    registry.load()
    result = await registry.execute("shell", {"command": "echo hello", "allowlist": ["echo"]}, {"shell": True})
    assert result.ok is False
    assert "disabled" in (result.error or "")

