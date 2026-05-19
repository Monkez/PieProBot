from __future__ import annotations

import asyncio
from typing import Any

from app.agent.loop import AgentLoop
from app.core.task_model import SubagentRecord, SubagentStatus
from app.observability.logging import get_logger
from app.providers.router import ProviderRouter
from app.tools.registry import ToolRegistry


class BaseSubagent:
    """Temporary worker owned by a task."""

    agent_type = "BaseAgent"

    def __init__(
        self,
        record: SubagentRecord,
        tool_registry: ToolRegistry,
        provider_router: ProviderRouter,
        root=None,
        memory=None,
        skills=None,
    ) -> None:
        self.record = record
        self.tool_registry = tool_registry
        self.provider_router = provider_router
        self.root = root
        self.memory = memory
        self.skills = skills
        self.logger = get_logger("subagents")

    async def run(self) -> SubagentRecord:
        self.record.status = SubagentStatus.INITIALIZING
        self.record.heartbeat("initializing")
        await asyncio.sleep(0)
        try:
            self.record.status = SubagentStatus.RUNNING
            self.record.heartbeat("running")
            self.logger.info(
                "subagent running",
                extra={"task_id": self.record.task_id, "subagent_id": self.record.id},
            )
            result = await self.execute()
            self.record.status = SubagentStatus.REPORTING
            self.record.result = result
            self.record.logs.append("result ready")
            self.record.status = SubagentStatus.COMPLETED
            self.logger.info(
                "subagent completed",
                extra={"task_id": self.record.task_id, "subagent_id": self.record.id},
            )
        except asyncio.CancelledError:
            self.record.status = SubagentStatus.CANCELLED
            self.record.error = "cancelled"
            raise
        except Exception as exc:
            self.record.status = SubagentStatus.FAILED
            self.record.error = str(exc)
            self.logger.error(
                "subagent failed: %s",
                exc,
                extra={"task_id": self.record.task_id, "subagent_id": self.record.id},
            )
        finally:
            self.record.heartbeat("finished")
        return self.record

    async def execute(self) -> str:
        await asyncio.sleep(0.05)
        if self.root is not None:
            loop = AgentLoop(
                root=self.root,
                provider_router=self.provider_router,
                tool_registry=self.tool_registry,
                memory=self.memory,
                skills=self.skills,
            )
            return await loop.run(self.record)
        goal = str(self.record.context.get("goal", ""))
        provider_response = await self.provider_router.chat([{"role": "user", "content": goal}])
        return provider_response.content


class ResearchAgent(BaseSubagent):
    agent_type = "ResearchAgent"


class CodingAgent(BaseSubagent):
    agent_type = "CodingAgent"


class TestAgent(BaseSubagent):
    agent_type = "TestAgent"


class DeploymentAgent(BaseSubagent):
    agent_type = "DeploymentAgent"


class MemoryAgent(BaseSubagent):
    agent_type = "MemoryAgent"

    async def execute(self) -> str:
        query = str(self.record.context.get("goal", ""))
        if "memory.search" in self.record.allowed_tools:
            result = await self.tool_registry.execute(
                "memory.search",
                {"query": query},
                granted_permissions=self.record.permissions,
                task_id=self.record.task_id,
                subagent_id=self.record.id,
            )
            if result.ok:
                return f"Memory search result: {result.output}"
        return await super().execute()


AGENT_TYPES: dict[str, type[BaseSubagent]] = {
    cls.agent_type: cls
    for cls in [ResearchAgent, CodingAgent, TestAgent, DeploymentAgent, MemoryAgent]
}
