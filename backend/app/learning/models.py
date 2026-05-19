from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Literal
from uuid import uuid4

from pydantic import BaseModel, Field


LearningDecision = Literal["safe", "review", "blocked"]
ProposalStatus = Literal["pending", "partially_applied", "applied", "rejected", "blocked"]


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


class LearningItem(BaseModel):
    kind: Literal["memory", "skill_create", "skill_reference", "skill_patch", "skill_archive"]
    target: str
    content: str = ""
    metadata: dict[str, Any] = Field(default_factory=dict)
    decision: LearningDecision = "review"
    reason: str = ""
    applied: bool = False


class LearningProposal(BaseModel):
    id: str = Field(default_factory=lambda: f"learn_{uuid4().hex[:12]}")
    task_id: str
    source: str = "background_review"
    confidence: float = 0.0
    summary: str = ""
    items: list[LearningItem] = Field(default_factory=list)
    status: ProposalStatus = "pending"
    created_at: datetime = Field(default_factory=now_utc)
    updated_at: datetime = Field(default_factory=now_utc)

    def touch(self) -> None:
        self.updated_at = now_utc()
