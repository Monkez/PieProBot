from __future__ import annotations

from pathlib import Path
from typing import Iterable

import yaml


DEFAULT_TOOLSETS: dict[str, dict[str, object]] = {
    "core": {"tools": ["echo", "task.status"]},
    "memory": {"tools": ["memory.search"]},
    "filesystem": {"tools": ["filesystem"]},
    "shell": {"tools": ["shell"]},
    "self_update": {"tools": ["self_update.status"]},
    "safe": {"includes": ["core", "memory", "self_update"]},
    "coding": {"includes": ["core", "filesystem"], "tools": ["task.status"]},
    "research": {"includes": ["core", "memory"]},
    "deployment": {"includes": ["core", "self_update"]},
}


class ToolsetManager:
    def __init__(self, path: Path | None = None) -> None:
        self.path = path
        self.toolsets: dict[str, dict[str, object]] = dict(DEFAULT_TOOLSETS)
        if path and path.exists():
            data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
            configured = data.get("toolsets", data)
            if isinstance(configured, dict):
                self.toolsets.update(configured)

    def resolve(self, names: Iterable[str] | None) -> list[str]:
        resolved: list[str] = []
        seen_toolsets: set[str] = set()

        def visit(name: str) -> None:
            if name in seen_toolsets:
                return
            seen_toolsets.add(name)
            item = self.toolsets.get(name)
            if not isinstance(item, dict):
                return
            for included in item.get("includes", []) or []:
                visit(str(included))
            for tool in item.get("tools", []) or []:
                tool_name = str(tool)
                if tool_name not in resolved:
                    resolved.append(tool_name)

        for name in names or []:
            visit(str(name))
        return resolved

    def toolsets_for_tool(self, tool_name: str) -> list[str]:
        matches: list[str] = []
        for name, item in self.toolsets.items():
            if not isinstance(item, dict):
                continue
            if tool_name in [str(tool) for tool in item.get("tools", []) or []]:
                matches.append(name)
        return matches
