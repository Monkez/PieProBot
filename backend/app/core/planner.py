from __future__ import annotations

from app.core.task_model import TaskPlan


class TaskPlanner:
    """Small deterministic planner used by the MVP orchestrator."""

    def create_plan(self, message: str) -> TaskPlan:
        lower = message.lower()
        agent_type = "ResearchAgent"
        tools = ["echo"]
        toolsets = ["research"]
        subtasks = ["Analyze request", "Execute safe local work", "Summarize result"]

        if any(word in lower for word in ["code", "bug", "test", "fix", "implement"]):
            agent_type = "CodingAgent"
            tools = ["echo", "task.status"]
            toolsets = ["coding"]
            subtasks = ["Inspect requested change", "Produce implementation guidance", "Validate output"]
        elif any(word in lower for word in ["memory", "remember", "search"]):
            agent_type = "MemoryAgent"
            tools = ["memory.search"]
            toolsets = ["memory"]
            subtasks = ["Search memory", "Summarize relevant facts"]
        elif any(word in lower for word in ["deploy", "rollback", "release"]):
            agent_type = "DeploymentAgent"
            tools = ["self_update.status"]
            toolsets = ["deployment"]
            subtasks = ["Assess deployment request", "Check update state", "Return safe next action"]

        return TaskPlan(
            goal=message,
            constraints=["Do not block the orchestrator event loop", "Use only explicitly allowed tools"],
            assumptions=["MVP local runtime with mock provider unless configured otherwise"],
            subtasks=subtasks,
            required_tools=tools,
            required_toolsets=toolsets,
            required_subagents=[agent_type],
            success_criteria=["Task has a recorded result", "Subagent lifecycle is completed"],
            validation_steps=["Check subagent status", "Persist task result"],
            estimated_runtime_seconds=2,
        )
