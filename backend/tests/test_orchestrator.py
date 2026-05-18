from __future__ import annotations

import asyncio
from pathlib import Path

from app.core.event_bus import EventBus
from app.core.orchestrator import OrchestratorAgent
from app.core.planner import TaskPlanner
from app.memory.manager import MemoryManager
from app.providers.router import ProviderRouter
from app.subagents.factory import SubagentFactory
from app.subagents.manager import SubagentManager
from app.tools.registry import ToolRegistry


def build_orchestrator() -> OrchestratorAgent:
    tools = ToolRegistry(Path(__file__).resolve().parents[2] / "config" / "tools")
    tools.load()
    providers = ProviderRouter()
    subagents = SubagentManager(SubagentFactory(tools, providers))
    return OrchestratorAgent(TaskPlanner(), subagents, MemoryManager(), EventBus())


async def test_orchestrator_submit_does_not_block() -> None:
    orchestrator = build_orchestrator()
    response = await asyncio.wait_for(orchestrator.submit_user_message("research current status"), timeout=0.2)
    assert response.status == "pending"
    await asyncio.sleep(0.5)
    assert orchestrator.tasks[response.task_id].status == "completed"


async def test_subagent_spawn_and_destroy_lifecycle() -> None:
    orchestrator = build_orchestrator()
    response = await orchestrator.submit_user_message_and_wait("implement a small code fix")
    task = orchestrator.tasks[response.task_id]
    assert task.status == "completed"
    assert len(task.assigned_subagents) == 1
    record = orchestrator.subagents.get(task.assigned_subagents[0])
    assert record.status == "completed"

