from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from pydantic import BaseModel, Field


class UpdatePlan(BaseModel):
    id: str = Field(default_factory=lambda: f"upd_{uuid4().hex[:10]}")
    goal: str
    files_to_change: list[str] = Field(default_factory=list)
    config_files: list[str] = Field(default_factory=list)
    tests_to_run: list[str] = Field(default_factory=lambda: ["pytest"])
    migrations: list[str] = Field(default_factory=list)
    risk_assessment: str = "low for MVP simulation"
    rollback_plan: str = "Keep current stable pointer and destroy failed candidate."
    success_criteria: list[str] = Field(default_factory=lambda: ["tests pass", "health check passes"])
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class CandidateRecord(BaseModel):
    id: str
    path: Path
    plan_id: str
    status: str = "created"
    test_passed: bool = False
    health_passed: bool = False
    report: str | None = None

