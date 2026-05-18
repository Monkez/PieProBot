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

from app.api import channels, chat, config, health, logs, memory, providers, self_update, subagents, tasks, tools
from app.channels.manager import ChannelManager
from app.config.hot_reload import HotReloadManager
from app.config.loader import ConfigLoader
from app.core.event_bus import EventBus
from app.core.orchestrator import OrchestratorAgent
from app.core.planner import TaskPlanner
from app.memory.manager import MemoryManager
from app.memory.tencentdb_agent_memory import TencentDBAgentMemoryBackend
from app.observability.logging import configure_logging, get_logger, set_request_context
from app.observability.metrics import MetricsCollector
from app.providers.router import ProviderRouter
from app.self_update.manager import SelfUpdateManager
from app.subagents.factory import SubagentFactory
from app.subagents.manager import SubagentManager
from app.tools.registry import ToolRegistry


class RuntimeState:
    def __init__(self, root: Path) -> None:
        self.root = root
        self.config_loader = ConfigLoader(root / "config")
        self.hot_reload = HotReloadManager(self.config_loader)
        self.memory = self._build_memory_manager()
        self.providers = ProviderRouter.from_config_dir(root / "config" / "providers")
        self.channels = ChannelManager.from_config_dir(root / "config" / "channels")
        self.tools = ToolRegistry(root / "config" / "tools")
        self.event_bus = EventBus()
        self.self_update = SelfUpdateManager(root, root / "runtime")
        self.subagents: SubagentManager
        self.orchestrator: OrchestratorAgent
        self.metrics: MetricsCollector

    def provider_router_factory(self) -> ProviderRouter:
        return ProviderRouter.from_config_dir(self.root / "config" / "providers")

    def channel_manager_factory(self) -> ChannelManager:
        return ChannelManager.from_config_dir(self.root / "config" / "channels")

    def _build_memory_manager(self) -> MemoryManager:
        config_path = self.root / "config" / "memory" / "tencentdb_agent_memory.yaml"
        if not config_path.exists():
            return MemoryManager()
        data = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
        if not bool(data.get("enabled", False)):
            return MemoryManager()
        backend = TencentDBAgentMemoryBackend(
            base_url=str(data.get("gateway_url", "http://127.0.0.1:8420")),
            session_key=str(data.get("session_key", "piepro-default")),
            timeout_seconds=float(data.get("timeout_seconds", 3)),
            max_results=int(data.get("max_results", 5)),
        )
        return MemoryManager(external_backend=backend)

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

        self.tools.executor.register_handler("memory.search", memory_search)
        self.tools.executor.register_handler("task.status", task_status)
        self.tools.executor.register_handler("self_update.status", self_update_status)

    def boot(self) -> None:
        self.tools.load()
        factory = SubagentFactory(self.tools, self.providers)
        self.subagents = SubagentManager(factory)
        self.orchestrator = OrchestratorAgent(TaskPlanner(), self.subagents, self.memory, self.event_bus)
        self.metrics = MetricsCollector(self.orchestrator, self.subagents)
        self.register_runtime_tools()


@asynccontextmanager
async def lifespan(app: FastAPI):
    configure_logging(os.getenv("LOG_LEVEL", "INFO"))
    root = Path(os.getenv("TWIN_AGENT_ROOT", Path(__file__).resolve().parents[2])).resolve()
    state = RuntimeState(root)
    state.boot()
    for key, value in state.__dict__.items():
        setattr(app.state, key, value)
    app.state.register_runtime_tools = state.register_runtime_tools
    app.state.provider_router_factory = state.provider_router_factory
    app.state.channel_manager_factory = state.channel_manager_factory
    get_logger("api").info("PiePro backend started")
    yield
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
app.include_router(self_update.router)
app.include_router(config.router)
app.include_router(logs.router)
