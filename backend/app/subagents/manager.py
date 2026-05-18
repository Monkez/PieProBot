from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from typing import Any

from app.core.task_model import SubagentRecord, SubagentStatus
from app.subagents.factory import SubagentFactory


class SubagentManager:
    def __init__(self, factory: SubagentFactory, orchestrator_id: str = "orch_local") -> None:
        self.factory = factory
        self.orchestrator_id = orchestrator_id
        self.records: dict[str, SubagentRecord] = {}
        self._tasks: dict[str, asyncio.Task[SubagentRecord]] = {}

    async def spawn(
        self,
        agent_type: str,
        task_id: str,
        context: dict[str, Any],
        allowed_tools: list[str],
        permissions: dict[str, bool] | None = None,
    ) -> SubagentRecord:
        record = SubagentRecord(
            type=agent_type,
            task_id=task_id,
            parent_orchestrator_id=self.orchestrator_id,
            context=context,
            allowed_tools=allowed_tools,
            permissions=permissions or {"memory": True},
        )
        self.records[record.id] = record
        agent = self.factory.create(record)
        self._tasks[record.id] = asyncio.create_task(agent.run())
        return record

    async def wait(self, subagent_id: str) -> SubagentRecord:
        task = self._tasks[subagent_id]
        return await task

    async def kill(self, subagent_id: str) -> SubagentRecord:
        task = self._tasks.get(subagent_id)
        record = self.records[subagent_id]
        if task and not task.done():
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
        record.status = SubagentStatus.CANCELLED
        record.heartbeat("killed")
        return record

    def list(self) -> list[SubagentRecord]:
        return list(self.records.values())

    def get(self, subagent_id: str) -> SubagentRecord:
        return self.records[subagent_id]

    async def detect_lost_heartbeats(self, max_age_seconds: int = 30) -> list[SubagentRecord]:
        now = datetime.now(timezone.utc)
        lost: list[SubagentRecord] = []
        for record in self.records.values():
            if record.status in {SubagentStatus.RUNNING, SubagentStatus.WAITING_FOR_TOOL}:
                if (now - record.heartbeat_at).total_seconds() > max_age_seconds:
                    record.status = SubagentStatus.FAILED
                    record.error = "heartbeat timeout"
                    lost.append(record)
        return lost

