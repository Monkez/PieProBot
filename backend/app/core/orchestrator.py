from __future__ import annotations

import asyncio
from typing import Any

from app.core.event_bus import EventBus
from app.core.planner import TaskPlanner
from app.core.task_model import ChatResponse, TaskRecord, TaskStatus
from app.memory.manager import MemoryItem, MemoryManager
from app.observability.logging import get_logger
from app.subagents.manager import SubagentManager


class OrchestratorAgent:
    """Main agent that stays responsive and delegates heavy work."""

    def __init__(
        self,
        planner: TaskPlanner,
        subagents: SubagentManager,
        memory: MemoryManager,
        event_bus: EventBus,
    ) -> None:
        self.id = "orch_local"
        self.planner = planner
        self.subagents = subagents
        self.memory = memory
        self.event_bus = event_bus
        self.tasks: dict[str, TaskRecord] = {}
        self._runners: dict[str, asyncio.Task[None]] = {}
        self.logger = get_logger("orchestrator")

    async def submit_user_message(self, message: str, priority: int = 5) -> ChatResponse:
        task = await self.create_task(message, priority)
        self._start_runner(task.id)
        return ChatResponse(task_id=task.id, status=task.status, response="Task accepted and delegated.")

    async def submit_user_message_and_wait(self, message: str, priority: int = 5) -> ChatResponse:
        task = await self.create_task(message, priority)
        await self._run_task(task.id)
        done = self.tasks[task.id]
        return ChatResponse(task_id=done.id, status=done.status, response=done.result or done.error or "")

    async def create_task(self, message: str, priority: int = 5) -> TaskRecord:
        task = TaskRecord(message=message, priority=priority)
        self.tasks[task.id] = task
        self.logger.info("task created", extra={"task_id": task.id})
        await self.event_bus.publish("tasks", {"type": "task.created", "task_id": task.id})
        await self.memory.save(MemoryItem(type="user_message", content=message, source=task.id, importance=0.4))
        return task

    async def plan_task(self, task_id: str) -> TaskRecord:
        task = self.tasks[task_id]
        task.status = TaskStatus.PLANNING
        task.plan = self.planner.create_plan(task.message)
        task.touch()
        self.logger.info("task planned", extra={"task_id": task.id})
        await self.event_bus.publish("tasks", {"type": "task.planned", "task_id": task.id})
        return task

    async def spawn_subagent(self, task: TaskRecord) -> str:
        if task.plan is None:
            raise ValueError("Task has no plan")
        agent_type = task.plan.required_subagents[0]
        record = await self.subagents.spawn(
            agent_type=agent_type,
            task_id=task.id,
            context={"goal": task.message, "plan": task.plan.model_dump()},
            allowed_tools=task.plan.required_tools,
            permissions={"memory": True, "network": False, "filesystem": False, "shell": False},
        )
        task.assigned_subagents.append(record.id)
        task.status = TaskStatus.RUNNING
        task.touch()
        self.logger.info("subagent spawned", extra={"task_id": task.id, "subagent_id": record.id})
        await self.event_bus.publish("subagents", {"type": "subagent.spawned", "task_id": task.id, "subagent_id": record.id})
        return record.id

    async def monitor_subagents(self, task_id: str) -> list[str]:
        task = self.tasks[task_id]
        return [self.subagents.get(sub_id).status for sub_id in task.assigned_subagents]

    async def revise_plan(self, task_id: str, reason: str) -> TaskRecord:
        task = self.tasks[task_id]
        task.plan = self.planner.create_plan(f"{task.message}\nRevision reason: {reason}")
        task.touch()
        return task

    async def collect_results(self, task_id: str) -> list[str]:
        task = self.tasks[task_id]
        results: list[str] = []
        for subagent_id in task.assigned_subagents:
            record = await self.subagents.wait(subagent_id)
            if record.result:
                results.append(record.result)
            if record.error:
                task.error = record.error
        return results

    async def finalize_task(self, task_id: str, results: list[str]) -> TaskRecord:
        task = self.tasks[task_id]
        if task.error and not results:
            task.status = TaskStatus.FAILED
            task.result = None
        else:
            task.status = TaskStatus.COMPLETED
            task.result = "\n".join(results) if results else "Completed without subagent output."
            await self.memory.save(MemoryItem(type="task_summary", content=task.result, source=task.id, importance=0.6))
            await self.memory.capture_turn(
                user_content=task.message,
                assistant_content=task.result,
                session_key=task.owner,
                session_id=task.id,
                metadata={"task_id": task.id},
            )
        task.touch()
        self.logger.info("task finalized status=%s", task.status, extra={"task_id": task.id})
        await self.event_bus.publish("tasks", {"type": "task.finalized", "task_id": task.id, "status": task.status})
        return task

    async def cancel_task(self, task_id: str) -> TaskRecord:
        task = self.tasks[task_id]
        for subagent_id in task.assigned_subagents:
            await self.subagents.kill(subagent_id)
        task.status = TaskStatus.CANCELLED
        task.touch()
        return task

    async def pause_task(self, task_id: str) -> TaskRecord:
        task = self.tasks[task_id]
        runner = self._runners.get(task_id)
        if runner and not runner.done():
            runner.cancel()
            try:
                await runner
            except asyncio.CancelledError:
                pass
        for subagent_id in task.assigned_subagents:
            record = self.subagents.records.get(subagent_id)
            if record and record.status not in {"completed", "failed", "cancelled", "destroyed"}:
                await self.subagents.kill(subagent_id)
        task.status = TaskStatus.PAUSED
        task.touch()
        return task

    async def resume_task(self, task_id: str) -> TaskRecord:
        task = self.tasks[task_id]
        if task.status == TaskStatus.PAUSED:
            task.assigned_subagents = []
            task.error = None
            task.status = TaskStatus.PENDING
            self._start_runner(task.id)
        return task

    async def retry_task(self, task_id: str) -> TaskRecord:
        task = self.tasks[task_id]
        runner = self._runners.get(task_id)
        if runner and not runner.done():
            runner.cancel()
        for subagent_id in list(task.assigned_subagents):
            record = self.subagents.records.get(subagent_id)
            if record and record.status not in {"completed", "failed", "cancelled", "destroyed"}:
                await self.subagents.kill(subagent_id)
        task.status = TaskStatus.PENDING
        task.error = None
        task.result = None
        task.assigned_subagents = []
        self._start_runner(task.id)
        return task

    def _start_runner(self, task_id: str) -> None:
        self._runners[task_id] = asyncio.create_task(self._run_task(task_id))

    async def _run_task(self, task_id: str) -> None:
        task = await self.plan_task(task_id)
        await self.spawn_subagent(task)
        results = await self.collect_results(task_id)
        await self.finalize_task(task_id, results)
