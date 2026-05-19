from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from typing import Any

from app.core.task_model import SubagentRecord, SubagentStatus
from app.subagents.factory import SubagentFactory


class SubagentManager:
    DEFAULT_BLOCKED_TOOLS = {"shell", "filesystem"}

    def __init__(
        self,
        factory: SubagentFactory,
        orchestrator_id: str = "orch_local",
        *,
        max_concurrent: int = 3,
        max_depth: int = 1,
        blocked_tools: set[str] | None = None,
        state_store=None,
    ) -> None:
        self.factory = factory
        self.orchestrator_id = orchestrator_id
        self.records: dict[str, SubagentRecord] = {}
        self._tasks: dict[str, asyncio.Task[SubagentRecord]] = {}
        self.max_concurrent = max(1, max_concurrent)
        self.max_depth = max(0, max_depth)
        self.blocked_tools = blocked_tools or set(self.DEFAULT_BLOCKED_TOOLS)
        self._semaphore = asyncio.Semaphore(self.max_concurrent)
        self._children: dict[str, set[str]] = {}
        self._state_store = state_store

    async def spawn(
        self,
        agent_type: str,
        task_id: str,
        context: dict[str, Any],
        allowed_tools: list[str],
        allowed_toolsets: list[str] | None = None,
        permissions: dict[str, bool] | None = None,
        parent_subagent_id: str | None = None,
        depth: int = 0,
    ) -> SubagentRecord:
        if depth > self.max_depth:
            raise RuntimeError(f"Subagent max depth exceeded: {depth} > {self.max_depth}")
        filtered_tools = [tool for tool in allowed_tools if tool not in self.blocked_tools]
        record = SubagentRecord(
            type=agent_type,
            task_id=task_id,
            parent_orchestrator_id=self.orchestrator_id,
            parent_subagent_id=parent_subagent_id,
            depth=depth,
            context=context,
            allowed_tools=filtered_tools,
            allowed_toolsets=allowed_toolsets or [],
            permissions=permissions or {"memory": True},
        )
        self.records[record.id] = record
        if parent_subagent_id:
            self._children.setdefault(parent_subagent_id, set()).add(record.id)
        agent = self.factory.create(record)
        self._tasks[record.id] = asyncio.create_task(self._run_guarded(agent, record))
        self._persist(record)
        return record

    async def _run_guarded(self, agent, record: SubagentRecord) -> SubagentRecord:
        async with self._semaphore:
            try:
                return await asyncio.wait_for(agent.run(), timeout=record.time_budget_seconds)
            except asyncio.TimeoutError:
                record.status = SubagentStatus.FAILED
                record.error = "time budget exceeded"
                record.heartbeat("timeout")
                return record
            finally:
                self._persist(record)

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
        self._persist(record)
        return record

    async def interrupt_tree(self, subagent_id: str) -> list[SubagentRecord]:
        interrupted: list[SubagentRecord] = []
        for child_id in list(self._children.get(subagent_id, set())):
            interrupted.extend(await self.interrupt_tree(child_id))
        if subagent_id in self.records:
            interrupted.append(await self.kill(subagent_id))
        return interrupted

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
                    self._persist(record)
                    lost.append(record)
        return lost

    def _persist(self, record: SubagentRecord) -> None:
        if not self._state_store:
            return
        try:
            self._state_store.save_subagent(record)
        except Exception:
            pass
