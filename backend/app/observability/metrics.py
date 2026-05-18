from __future__ import annotations

from app.core.orchestrator import OrchestratorAgent
from app.subagents.manager import SubagentManager


class MetricsCollector:
    def __init__(self, orchestrator: OrchestratorAgent, subagents: SubagentManager) -> None:
        self.orchestrator = orchestrator
        self.subagents = subagents

    def collect(self) -> dict[str, int]:
        return {
            "tasks_total": len(self.orchestrator.tasks),
            "subagents_total": len(self.subagents.records),
            "active_subagents": sum(1 for item in self.subagents.records.values() if item.status == "running"),
        }

