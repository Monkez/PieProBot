from __future__ import annotations

import time
from pathlib import Path
from types import SimpleNamespace

from app.core.event_bus import EventBus
from app.core.orchestrator import OrchestratorAgent
from app.core.planner import TaskPlanner
from app.db.session import SQLiteStateStore
from app.learning.models import LearningItem, LearningProposal
from app.learning.policy import LearningPolicy
from app.memory.manager import MemoryManager
from app.providers.base import BaseLLMProvider, ProviderResponse
from app.plugins.manager import PluginManager
from app.providers.router import ProviderRouter
from app.scheduler.manager import ScheduledTaskManager
from app.skills.store import SkillStore
from app.subagents.factory import SubagentFactory
from app.subagents.manager import SubagentManager
from app.tools.checkpoint import CheckpointManager
from app.tools.executor import ToolExecutor
from app.tools.registry import ToolRegistry
from app.tools.schemas import ToolDefinition
from app.tools.toolsets import ToolsetManager


class ToolCallingProvider(BaseLLMProvider):
    name = "tool-calling-test"

    def __init__(self) -> None:
        self.calls = 0

    async def chat(self, messages: list[dict[str, str]], model: str | None = None) -> ProviderResponse:
        self.calls += 1
        if self.calls == 1:
            return ProviderResponse(
                content='{"tool_calls":[{"name":"echo","arguments":{"text":"from tool loop"}}]}',
                model="test",
            )
        return ProviderResponse(content="final after tool", model="test")


async def test_sqlite_persists_tasks_messages_and_memory_with_fts(tmp_path: Path) -> None:
    store = SQLiteStateStore(tmp_path / "state.sqlite3")
    memory = MemoryManager(state_store=store)
    tools = ToolRegistry(
        Path(__file__).resolve().parents[2] / "config" / "tools",
        executor=ToolExecutor(state_store=store),
    )
    tools.load()
    subagents = SubagentManager(SubagentFactory(tools, ProviderRouter()), state_store=store)
    orchestrator = OrchestratorAgent(TaskPlanner(), subagents, memory, EventBus(), state_store=store)

    response = await orchestrator.submit_user_message_and_wait("remember qdrant memory")
    restored = SQLiteStateStore(tmp_path / "state.sqlite3")

    assert response.status == "completed"
    assert any(task.id == response.task_id for task in restored.load_tasks())
    results = restored.search_all("qdrant", 10)
    assert results["tasks"]
    assert results["messages"]
    assert results["memory"]
    store.close()
    restored.close()


def test_toolsets_resolve_composed_tools() -> None:
    toolsets = ToolsetManager(Path(__file__).resolve().parents[2] / "config" / "toolsets.yaml")
    assert "memory.search" in toolsets.resolve(["research"])
    assert "filesystem" in toolsets.resolve(["coding"])


def test_checkpoint_snapshot_and_rollback(tmp_path: Path) -> None:
    store = SQLiteStateStore(tmp_path / "state.sqlite3")
    manager = CheckpointManager(tmp_path, store)
    target = tmp_path / "workspace" / "note.txt"
    target.parent.mkdir()
    target.write_text("before", encoding="utf-8")

    checkpoint_id = manager.snapshot_files("test", target.parent, [target])
    target.write_text("after", encoding="utf-8")
    result = manager.rollback(str(checkpoint_id))

    assert target.read_text(encoding="utf-8") == "before"
    assert result["checkpoint_id"] == checkpoint_id
    store.close()


async def test_scheduler_submits_due_task(tmp_path: Path) -> None:
    store = SQLiteStateStore(tmp_path / "state.sqlite3")
    memory = MemoryManager(state_store=store)
    tools = ToolRegistry(
        Path(__file__).resolve().parents[2] / "config" / "tools",
        executor=ToolExecutor(state_store=store),
    )
    tools.load()
    subagents = SubagentManager(SubagentFactory(tools, ProviderRouter()), state_store=store)
    orchestrator = OrchestratorAgent(TaskPlanner(), subagents, memory, EventBus(), state_store=store)
    scheduler = ScheduledTaskManager(store, lambda: orchestrator)

    scheduler.create(name="once", prompt="scheduled hello", run_at=time.time() - 1)
    ran = await scheduler.tick()

    assert ran == 1
    assert any("scheduled hello" == task.message for task in orchestrator.tasks.values())
    store.close()


def test_plugin_manager_registers_tool(tmp_path: Path) -> None:
    plugin_dir = tmp_path / "plugins" / "demo"
    plugin_dir.mkdir(parents=True)
    (plugin_dir / "plugin.yaml").write_text("name: demo\nmodule: plugin.py\n", encoding="utf-8")
    (plugin_dir / "plugin.py").write_text(
        """
from app.tools.schemas import ToolDefinition

async def execute(payload):
    return {"seen": payload}

def register(ctx):
    ctx.register_tool(ToolDefinition(name="demo.tool", description="demo"), execute)
""",
        encoding="utf-8",
    )

    manager = PluginManager(tmp_path)
    manager.discover()

    assert manager.loaded[0]["name"] == "demo"
    assert manager.context.tool_definitions[0][0].name == "demo.tool"


async def test_agent_loop_executes_model_requested_tool(tmp_path: Path) -> None:
    store = SQLiteStateStore(tmp_path / "state.sqlite3")
    skills = SkillStore(tmp_path)
    memory = MemoryManager(state_store=store)
    tools = ToolRegistry(
        Path(__file__).resolve().parents[2] / "config" / "tools",
        executor=ToolExecutor(state_store=store),
    )
    tools.load()
    provider = ToolCallingProvider()
    subagents = SubagentManager(
        SubagentFactory(tools, ProviderRouter([provider]), root=tmp_path, memory=memory, skills=skills),
        state_store=store,
    )
    orchestrator = OrchestratorAgent(TaskPlanner(), subagents, memory, EventBus(), state_store=store)

    response = await orchestrator.submit_user_message_and_wait("use echo tool")

    assert response.response == "final after tool"
    assert provider.calls == 2
    assert store.execute("SELECT tool_name FROM tool_calls WHERE tool_name='echo'")
    store.close()


async def test_background_review_creates_class_level_skill(tmp_path: Path) -> None:
    store = SQLiteStateStore(tmp_path / "state.sqlite3")
    skills = SkillStore(tmp_path)
    memory = MemoryManager(state_store=store)
    tools = ToolRegistry(Path(__file__).resolve().parents[2] / "config" / "tools")
    tools.load()
    subagents = SubagentManager(
        SubagentFactory(tools, ProviderRouter(), root=tmp_path, memory=memory, skills=skills),
        state_store=store,
    )
    from app.agent.background_review import BackgroundReview

    orchestrator = OrchestratorAgent(
        TaskPlanner(),
        subagents,
        memory,
        EventBus(),
        state_store=store,
        background_review=BackgroundReview(memory, skills, store),
    )

    response = await orchestrator.submit_user_message_and_wait("implement a reusable code fix workflow")

    assert response.status == "completed"
    assert any(item["name"] == "coding-workflows" for item in skills.list())
    proposals = store.list_learning_proposals()
    assert proposals
    assert proposals[0]["status"] == "applied"
    store.close()


def test_learning_policy_blocks_transient_task_progress() -> None:
    proposal = LearningProposal(
        task_id="task_1",
        items=[
            LearningItem(
                kind="memory",
                target="user_preference",
                content="Today phase 2 is complete after commit abc123",
            )
        ],
    )

    classified = LearningPolicy().classify(proposal)

    assert classified.status == "blocked"
    assert classified.items[0].decision == "blocked"


async def test_learning_api_approves_and_rejects_review_items(tmp_path: Path) -> None:
    from app.api.learning import approve_learning_proposal, reject_learning_proposal

    store = SQLiteStateStore(tmp_path / "state.sqlite3")
    skills = SkillStore(tmp_path)
    memory = MemoryManager(state_store=store)
    skills.create("coding-workflows", "Reusable workflow for coding tasks.", "before")
    request = SimpleNamespace(app=SimpleNamespace(state=SimpleNamespace(state_store=store, skills=skills, memory=memory)))

    proposal = LearningProposal(
        task_id="task_review",
        items=[
            LearningItem(
                kind="skill_patch",
                target="coding-workflows",
                content="after",
                metadata={"old": "before"},
                decision="review",
            )
        ],
    )
    store.save_learning_proposal(proposal)

    approved = await approve_learning_proposal(request, proposal.id)

    assert approved["status"] == "applied"
    assert "after" in skills.view("coding-workflows")["content"]

    rejectable = LearningProposal(
        task_id="task_reject",
        items=[LearningItem(kind="skill_archive", target="coding-workflows", content="too broad", decision="review")],
    )
    store.save_learning_proposal(rejectable)

    rejected = await reject_learning_proposal(request, rejectable.id)

    assert rejected["status"] == "rejected"
    store.close()
