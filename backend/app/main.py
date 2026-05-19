from __future__ import annotations

import os
from contextlib import asynccontextmanager
from pathlib import Path
from time import perf_counter
from typing import Any
from uuid import uuid4

import yaml
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from app.api import channels, chat, checkpoints, config, health, learning, logs, memory, plugins, providers, schedules, self_update, skills, state as state_api, subagents, tasks, tools
from app.channels.manager import ChannelManager
from app.config.hot_reload import HotReloadManager
from app.config.loader import ConfigLoader
from app.core.event_bus import EventBus
from app.agent.background_review import BackgroundReview
from app.agent.curator import SkillCurator
from app.core.orchestrator import OrchestratorAgent
from app.db.session import SQLiteStateStore
from app.core.planner import TaskPlanner
from app.memory.manager import MemoryManager
from app.memory.tencentdb_agent_memory import TencentDBAgentMemoryBackend
from app.observability.logging import configure_logging, get_logger, set_request_context
from app.observability.metrics import MetricsCollector
from app.plugins.manager import PluginManager
from app.providers.router import ProviderRouter
from app.scheduler.manager import ScheduledTaskManager
from app.self_update.manager import SelfUpdateManager
from app.skills.store import SkillStore
from app.subagents.factory import SubagentFactory
from app.subagents.manager import SubagentManager
from app.tools.checkpoint import CheckpointManager
from app.tools.executor import ToolExecutor
from app.tools.registry import ToolRegistry


class RuntimeState:
    def __init__(self, root: Path) -> None:
        self.root = root
        self.config_loader = ConfigLoader(root / "config")
        self.hot_reload = HotReloadManager(self.config_loader)
        self.state_store = SQLiteStateStore(root / "runtime" / "piepro.sqlite3")
        self.plugins = PluginManager(root)
        self.plugins.discover()
        self.skills = SkillStore(root)
        self.curator = SkillCurator(self.skills)
        self.memory = self._build_memory_manager()
        self.background_review = BackgroundReview(self.memory, self.skills, self.state_store)
        self.providers = ProviderRouter.from_config_dir(
            root / "config" / "providers",
            self.plugins.context.provider_factories,
        )
        self.channels = ChannelManager.from_config_dir(
            root / "config" / "channels",
            self.plugins.context.channel_factories,
        )
        self.checkpoints = CheckpointManager(root, self.state_store)
        self.tools = ToolRegistry(
            root / "config" / "tools",
            executor=ToolExecutor(state_store=self.state_store, checkpoint_manager=self.checkpoints),
        )
        self.event_bus = EventBus()
        self.self_update = SelfUpdateManager(root, root / "runtime")
        self.subagents: SubagentManager
        self.orchestrator: OrchestratorAgent
        self.metrics: MetricsCollector
        self.scheduler: ScheduledTaskManager

    def provider_router_factory(self) -> ProviderRouter:
        return ProviderRouter.from_config_dir(self.root / "config" / "providers", self.plugins.context.provider_factories)

    def channel_manager_factory(self) -> ChannelManager:
        return ChannelManager.from_config_dir(self.root / "config" / "channels", self.plugins.context.channel_factories)

    def _build_memory_manager(self) -> MemoryManager:
        config_path = self.root / "config" / "memory" / "tencentdb_agent_memory.yaml"
        if not config_path.exists():
            manager = MemoryManager(state_store=self.state_store)
            return self._apply_memory_plugins(manager)
        data = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
        if not bool(data.get("enabled", False)):
            manager = MemoryManager(state_store=self.state_store)
            return self._apply_memory_plugins(manager)
        backend = TencentDBAgentMemoryBackend(
            base_url=str(data.get("gateway_url", "http://127.0.0.1:8420")),
            session_key=str(data.get("session_key", "piepro-default")),
            timeout_seconds=float(data.get("timeout_seconds", 3)),
            max_results=int(data.get("max_results", 5)),
        )
        manager = MemoryManager(external_backend=backend, state_store=self.state_store)
        return self._apply_memory_plugins(manager)

    def _apply_memory_plugins(self, manager: MemoryManager) -> MemoryManager:
        for factory in self.plugins.context.memory_factories:
            manager = factory(manager)
        return manager

    def register_runtime_tools(self) -> None:
        async def memory_search(payload: dict[str, Any]) -> dict[str, Any]:
            items = await self.memory.search(str(payload.get("query", "")), int(payload.get("limit", 10)))
            return {"items": [item.model_dump(mode="json") for item in items]}

        async def task_status(payload: dict[str, Any]) -> dict[str, Any]:
            task_id = str(payload.get("task_id", ""))
            task = self.orchestrator.tasks.get(task_id)
            return {"task": task.model_dump(mode="json") if task else None}

        async def self_update_status(payload: dict[str, Any]) -> dict[str, Any]:
            return self.self_update.status()

        async def skills_list(payload: dict[str, Any]) -> dict[str, Any]:
            return {"skills": self.skills.list()}

        async def skills_view(payload: dict[str, Any]) -> dict[str, Any]:
            return self.skills.view(str(payload["name"]))

        async def skills_manage(payload: dict[str, Any]) -> dict[str, Any]:
            action = str(payload.get("action", ""))
            if action == "create":
                return self.skills.create(
                    str(payload["name"]),
                    str(payload.get("description", "")),
                    payload.get("content"),
                )
            if action == "patch":
                return self.skills.patch(
                    str(payload["name"]),
                    str(payload["old"]),
                    str(payload["new"]),
                    str(payload.get("file_path", "SKILL.md")),
                )
            if action == "write_file":
                return self.skills.write_file(str(payload["name"]), str(payload["file_path"]), str(payload.get("content", "")))
            if action == "archive":
                return self.skills.archive(str(payload["name"]), str(payload.get("reason", "")))
            raise ValueError(f"Unsupported skills.manage action: {action}")

        async def self_update_plan(payload: dict[str, Any]) -> dict[str, Any]:
            plan = await self.self_update.create_update_plan(
                str(payload["goal"]),
                list(payload.get("files_to_change", [])),
            )
            return plan.model_dump(mode="json")

        async def curator_run(payload: dict[str, Any]) -> dict[str, Any]:
            return self.curator.run_once(dry_run=bool(payload.get("dry_run", True)))

        self.tools.executor.register_handler("memory.search", memory_search)
        self.tools.executor.register_handler("task.status", task_status)
        self.tools.executor.register_handler("self_update.status", self_update_status)
        self.tools.executor.register_handler("skills.list", skills_list)
        self.tools.executor.register_handler("skills.view", skills_view)
        self.tools.executor.register_handler("skills.manage", skills_manage)
        self.tools.executor.register_handler("self_update.plan", self_update_plan)
        self.tools.executor.register_handler("curator.run", curator_run)

    def boot(self) -> None:
        self.tools.load()
        for definition, handler in self.plugins.context.tool_definitions:
            self.tools.register_definition(definition, handler, config_path="plugin")
        factory = SubagentFactory(self.tools, self.providers, root=self.root, memory=self.memory, skills=self.skills)
        subagent_cfg = self.config_loader.read("agent/subagents.yaml") or {}
        blocked_tools = set(subagent_cfg.get("blocked_tools", ["shell"]))
        self.subagents = SubagentManager(
            factory,
            max_concurrent=int(subagent_cfg.get("max_concurrent", subagent_cfg.get("max_subagents", 3))),
            max_depth=int(subagent_cfg.get("max_spawn_depth", 1)),
            blocked_tools=blocked_tools,
            state_store=self.state_store,
        )
        for record in self.state_store.load_subagents():
            self.subagents.records[record.id] = record
        self.orchestrator = OrchestratorAgent(
            TaskPlanner(),
            self.subagents,
            self.memory,
            self.event_bus,
            state_store=self.state_store,
            background_review=self.background_review,
        )
        self.metrics = MetricsCollector(self.orchestrator, self.subagents)
        self.scheduler = ScheduledTaskManager(self.state_store, lambda: self.orchestrator)
        self.register_runtime_tools()


@asynccontextmanager
async def lifespan(app: FastAPI):
    configure_logging(os.getenv("LOG_LEVEL", "INFO"))
    root = Path(os.getenv("TWIN_AGENT_ROOT", Path(__file__).resolve().parents[2])).resolve()
    state = RuntimeState(root)
    state.boot()
    state.scheduler.start()
    for key, value in state.__dict__.items():
        setattr(app.state, key, value)
    app.state.register_runtime_tools = state.register_runtime_tools
    app.state.provider_router_factory = state.provider_router_factory
    app.state.channel_manager_factory = state.channel_manager_factory
    get_logger("api").info("PiePro backend started")
    yield
    await state.scheduler.stop()
    state.state_store.close()
    get_logger("api").info("PiePro backend stopped")


app = FastAPI(title="PiePro", version="0.1.0", lifespan=lifespan)


@app.middleware("http")
async def correlation_middleware(request: Request, call_next):
    correlation_id = request.headers.get("x-correlation-id") or f"corr_{uuid4().hex[:16]}"
    set_request_context(correlation_id)
    start = perf_counter()
    response = await call_next(request)
    duration_ms = round((perf_counter() - start) * 1000, 2)
    response.headers["x-correlation-id"] = correlation_id
    get_logger("api.request").info(
        "%s %s %s %.2fms",
        request.method,
        request.url.path,
        response.status_code,
        duration_ms,
        extra={"correlation_id": correlation_id},
    )
    return response

app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(chat.router)
app.include_router(tasks.router)
app.include_router(subagents.router)
app.include_router(tools.router)
app.include_router(providers.router)
app.include_router(channels.router)
app.include_router(memory.router)
app.include_router(learning.router)
app.include_router(self_update.router)
app.include_router(config.router)
app.include_router(logs.router)
app.include_router(schedules.router)
app.include_router(checkpoints.router)
app.include_router(plugins.router)
app.include_router(state_api.router)
app.include_router(skills.router)
