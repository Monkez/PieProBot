from __future__ import annotations

import importlib.util
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable

import yaml

from app.channels.base import BaseChannel
from app.memory.manager import MemoryManager
from app.providers.base import BaseLLMProvider
from app.tools.schemas import ToolDefinition


@dataclass
class PluginContext:
    root: Path
    tool_definitions: list[tuple[ToolDefinition, Callable[[dict[str, Any]], Any] | None]] = field(default_factory=list)
    provider_factories: list[Callable[[], BaseLLMProvider]] = field(default_factory=list)
    channel_factories: list[Callable[[], BaseChannel]] = field(default_factory=list)
    memory_factories: list[Callable[[MemoryManager], MemoryManager]] = field(default_factory=list)

    def register_tool(self, definition: ToolDefinition, handler=None) -> None:
        self.tool_definitions.append((definition, handler))

    def register_provider(self, factory: Callable[[], BaseLLMProvider]) -> None:
        self.provider_factories.append(factory)

    def register_channel(self, factory: Callable[[], BaseChannel]) -> None:
        self.channel_factories.append(factory)

    def register_memory(self, factory: Callable[[MemoryManager], MemoryManager]) -> None:
        self.memory_factories.append(factory)


class PluginManager:
    """Minimal local plugin loader.

    Plugins live under `plugins/<name>/plugin.yaml` with an optional
    `module: some_file.py`. The module may expose `register(ctx)`.
    """

    def __init__(self, root: Path) -> None:
        self.root = root
        self.plugins_dir = root / "plugins"
        self.context = PluginContext(root=root)
        self.loaded: list[dict[str, Any]] = []

    def discover(self) -> None:
        if not self.plugins_dir.exists():
            return
        for manifest in sorted(self.plugins_dir.glob("*/plugin.yaml")):
            self._load_manifest(manifest)

    def _load_manifest(self, manifest_path: Path) -> None:
        data = yaml.safe_load(manifest_path.read_text(encoding="utf-8")) or {}
        if data.get("enabled") is False:
            return
        module_name = str(data.get("module", "__init__.py"))
        module_path = manifest_path.parent / module_name
        entry = {
            "name": data.get("name", manifest_path.parent.name),
            "path": str(manifest_path.parent),
            "kind": data.get("kind", "standalone"),
        }
        if module_path.exists():
            spec = importlib.util.spec_from_file_location(f"piepro_plugin_{manifest_path.parent.name}", module_path)
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                register = getattr(module, "register", None)
                if callable(register):
                    register(self.context)
        self.loaded.append(entry)
