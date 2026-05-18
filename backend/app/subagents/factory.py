from __future__ import annotations

from app.core.task_model import SubagentRecord
from app.providers.router import ProviderRouter
from app.subagents.base import AGENT_TYPES, BaseSubagent
from app.tools.registry import ToolRegistry


class SubagentFactory:
    def __init__(self, tool_registry: ToolRegistry, provider_router: ProviderRouter) -> None:
        self.tool_registry = tool_registry
        self.provider_router = provider_router

    def create(self, record: SubagentRecord) -> BaseSubagent:
        cls = AGENT_TYPES.get(record.type, BaseSubagent)
        return cls(record, self.tool_registry, self.provider_router)

