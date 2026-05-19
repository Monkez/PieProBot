from __future__ import annotations

from datetime import datetime, timezone
from enum import StrEnum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


class TaskStatus(StrEnum):
    PENDING = "pending"
    PLANNING = "planning"
    RUNNING = "running"
    WAITING = "waiting"
    FAILED = "failed"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    PAUSED = "paused"
    INTERRUPTED = "interrupted"


class SubagentStatus(StrEnum):
    CREATED = "created"
    INITIALIZING = "initializing"
    RUNNING = "running"
    WAITING_FOR_TOOL = "waiting_for_tool"
    REPORTING = "reporting"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    DESTROYED = "destroyed"


class TaskPlan(BaseModel):
    goal: str
    constraints: list[str] = Field(default_factory=list)
    assumptions: list[str] = Field(default_factory=list)
    subtasks: list[str] = Field(default_factory=list)
    required_tools: list[str] = Field(default_factory=list)
    required_toolsets: list[str] = Field(default_factory=list)
    required_subagents: list[str] = Field(default_factory=list)
    success_criteria: list[str] = Field(default_factory=list)
    validation_steps: list[str] = Field(default_factory=list)
    fallback_plan: str = "Retry with a smaller scope and safer tools."
    estimated_cost: float = 0.0
    estimated_runtime_seconds: int = 5


class TaskRecord(BaseModel):
    id: str = Field(default_factory=lambda: f"task_{uuid4().hex[:12]}")
    message: str
    status: TaskStatus = TaskStatus.PENDING
    priority: int = 5
    owner: str = "user"
    plan: TaskPlan | None = None
    assigned_subagents: list[str] = Field(default_factory=list)
    artifacts: list[dict[str, Any]] = Field(default_factory=list)
    result: str | None = None
    error: str | None = None
    created_at: datetime = Field(default_factory=now_utc)
    updated_at: datetime = Field(default_factory=now_utc)

    def touch(self) -> None:
        self.updated_at = now_utc()


class SubagentRecord(BaseModel):
    id: str = Field(default_factory=lambda: f"sub_{uuid4().hex[:12]}")
    type: str
    task_id: str
    parent_orchestrator_id: str
    parent_subagent_id: str | None = None
    depth: int = 0
    status: SubagentStatus = SubagentStatus.CREATED
    permissions: dict[str, bool] = Field(default_factory=dict)
    allowed_tools: list[str] = Field(default_factory=list)
    allowed_toolsets: list[str] = Field(default_factory=list)
    context: dict[str, Any] = Field(default_factory=dict)
    memory_scope: str = "task"
    token_budget: int = 8_000
    time_budget_seconds: int = 60
    retry_budget: int = 1
    tool_call_budget: int = 25
    current_step: str = "created"
    logs: list[str] = Field(default_factory=list)
    result: str | None = None
    error: str | None = None
    heartbeat_at: datetime = Field(default_factory=now_utc)
    created_at: datetime = Field(default_factory=now_utc)
    updated_at: datetime = Field(default_factory=now_utc)

    def heartbeat(self, step: str | None = None) -> None:
        self.heartbeat_at = now_utc()
        self.updated_at = self.heartbeat_at
        if step:
            self.current_step = step


class ChatRequest(BaseModel):
    message: str
    priority: int = 5
    attachments: list[dict[str, Any]] = Field(default_factory=list)


class ChatResponse(BaseModel):
    task_id: str
    status: TaskStatus
    response: str
    attachments: list[dict[str, Any]] = Field(default_factory=list)
