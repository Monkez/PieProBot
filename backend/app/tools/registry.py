from __future__ import annotations

import importlib
from pathlib import Path
from typing import Any

import yaml

from app.tools.executor import ToolExecutor
from app.tools.schemas import ToolDefinition, ToolResult


BUILTIN_HANDLERS = {
    "echo": "app.tools.builtins.echo_tool:execute",
    "http.request": "app.tools.builtins.http_tool:execute",
    "filesystem": "app.tools.builtins.filesystem_tool:execute",
    "shell": "app.tools.builtins.shell_tool:execute",
}


def _load_callable(path: str) -> Any:
    module_name, attr = path.split(":", 1)
    module = importlib.import_module(module_name)
    return getattr(module, attr)


class ToolRegistry:
    def __init__(self, config_dir: Path, executor: ToolExecutor | None = None) -> None:
        self.config_dir = config_dir
        self.executor = executor or ToolExecutor()
        self.definitions: dict[str, ToolDefinition] = {}

    def load(self) -> None:
        self.definitions.clear()
        for path in sorted(self.config_dir.glob("*.yaml")):
            data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
            definition = ToolDefinition.model_validate(data)
            self.definitions[definition.name] = definition
            handler_path = definition.handler or BUILTIN_HANDLERS.get(definition.name)
            if handler_path:
                self.executor.register_handler(definition.name, _load_callable(handler_path))

    def list(self) -> list[ToolDefinition]:
        return list(self.definitions.values())

    def get(self, name: str) -> ToolDefinition:
        return self.definitions[name]

    async def execute(self, name: str, payload: dict[str, Any], granted_permissions: dict[str, bool] | None = None) -> ToolResult:
        return await self.executor.execute(self.get(name), payload, granted_permissions)

