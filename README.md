# PiePro

PiePro is a lightweight local AI agent platform. It provides a FastAPI backend, async orchestrator, temporary subagents, tool registry, provider abstraction, memory abstraction, TencentDB Agent Memory integration, self-update simulation, and a Next.js admin console.

The project is intentionally simple to install and run: no Docker, no required database, no required queue service. The default runtime uses local in-memory state and optional external adapters.

## Quick Install With uv Tool

Install the CLI directly from GitHub:

```powershell
uv tool install git+https://github.com/Monkez/PieProBot.git
piepro init PieProBot
piepro start
```

`piepro init` clones the project and saves it as the default PiePro root. After that, `piepro start`, `piepro status`, and `piepro restart` work from any directory.

`piepro start` starts backend and frontend from one terminal command, keeps service logs under `logs/`, and opens the frontend automatically.

If you already cloned the repository:

```powershell
uv venv .venv --python 3.12
uv pip install --python .\.venv\Scripts\python.exe -e ".[test]"
cd frontend
npm install
cd ..
.\.venv\Scripts\piepro.exe start
```

## Requirements

- Python 3.12+
- Node.js 20+ for the PiePro frontend
- Node.js 22.16+ only if you run the optional TencentDB Agent Memory gateway SQLite path

## CLI

```bash
piepro init PieProBot
piepro start
piepro status
piepro restart
piepro stop
piepro use E:\SideProjects\PiePro
```

Useful options:

```bash
piepro start --no-open
piepro start --backend-only
piepro restart --force
piepro --root E:\SideProjects\PiePro start
```

Default URLs:

- Backend: `http://127.0.0.1:8000`
- API docs: `http://127.0.0.1:8000/docs`
- Frontend: `http://127.0.0.1:3000/dashboard`

Runtime files:

- PID state: `runtime/piepro.pid.json`
- Backend log: `logs/backend.cli.log`
- Frontend log: `logs/frontend.cli.log`

## Architecture

- **Orchestrator**: accepts user messages, creates task records, plans work, spawns subagents, collects results, and stays non-blocking.
- **Subagents**: temporary scoped workers with lifecycle, heartbeat, permissions, allowed tools, budget fields, logs, and result/error records.
- **Tools**: YAML-configured registry with schema, timeout, permission, audit level, and built-in handlers.
- **Providers**: provider router loaded from `config/providers/*.yaml`; local mock provider is enabled by default.
- **Memory**: local memory manager with optional TencentDB Agent Memory external backend.
- **Self-update**: safe stable/candidate flow simulation under `runtime/bodies`.
- **Frontend**: Next.js operations console for dashboard, chat, tasks, subagents, tools, providers, memory, self-update, logs, and config.
- **Design system**: soft-modern pastel productivity dashboard with a sage workspace, rounded cards, thick black accents, and only operationally useful widgets.

## TencentDB Agent Memory

PiePro integrates with [TencentDB Agent Memory](https://github.com/Tencent/TencentDB-Agent-Memory) through its standalone TDAI Gateway HTTP API.

Config:

```yaml
# config/memory/tencentdb_agent_memory.yaml
version: 1
enabled: true
gateway_url: http://127.0.0.1:8420
session_key: piepro-default
timeout_seconds: 3
max_results: 5
fallback_to_local: true
```

When enabled, PiePro:

- Captures completed task turns through `POST /capture`.
- Searches structured memories through `POST /search/memories`.
- Falls back to conversation search through `POST /search/conversations`.
- Checks gateway health through `GET /health`.
- Keeps local fallback memory active if the gateway is unavailable.

Run the gateway separately:

```powershell
git clone https://github.com/Tencent/TencentDB-Agent-Memory.git C:\tmp\TencentDB-Agent-Memory
$env:TENCENTDB_AGENT_MEMORY_HOME = "C:\tmp\TencentDB-Agent-Memory"
$env:TDAI_LLM_API_KEY = "<memory-extraction-model-key>"
powershell -ExecutionPolicy Bypass -File scripts/start_tencentdb_memory_gateway.ps1
```

## Testing

```powershell
cd backend
..\.venv\Scripts\python.exe -m pytest
cd ..\frontend
npm run build
npm audit --audit-level=moderate
```

Current coverage includes orchestrator non-blocking behavior, subagent lifecycle, tool registry, memory fallback/external adapter behavior, provider config loading, self-update promotion safety, API smoke tests, CLI parsing, and observability logs.

## Documentation Is Runtime Knowledge

PiePro treats `docs/` as part of the bot self-knowledge base. Any code change that alters behavior, config, operations, architecture, memory, security, self-update, or install flow must update the relevant docs in the same change.

Start here:

- [Architecture](docs/ARCHITECTURE.md)
- [Operations](docs/OPERATIONS.md)
- [Memory](docs/MEMORY.md)
- [Self-Update](docs/SELF_UPDATE.md)
- [Development](docs/DEVELOPMENT.md)
- [Design System](docs/DESIGN_SYSTEM.md)
- [Self Knowledge](docs/SELF_KNOWLEDGE.md)
- [Documentation Policy](docs/DOCS_POLICY.md)

## Current Boundaries

- Default LLM calls use `LocalProvider`.
- State is in-memory by default.
- TencentDB Agent Memory is optional and accessed via external gateway.
- Self-update candidate startup is simulated; promotion safety checks exist but do not yet switch live traffic.
- Frontend is operational but intentionally minimal.
