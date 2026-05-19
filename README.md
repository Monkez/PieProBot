# PiePro

PiePro is a lightweight local AI agent platform. It provides a FastAPI backend, async orchestrator, temporary subagents, a Hermes-inspired agent loop, dynamic system prompts, SQLite runtime persistence with FTS search, toolsets, a tool registry, provider abstraction, channel adapters, memory abstraction, skills, background learning, local plugins, simple schedules, checkpoint rollback, TencentDB Agent Memory integration, self-update planning, and a Next.js admin console.

The project is intentionally simple to install and run: no Docker, no required database, no required queue service. The default runtime uses local in-memory state and optional external adapters.

## Quick Install With uv Tool

Install the CLI directly from GitHub:

```powershell
uv tool install git+https://github.com/Monkez/PieProBot.git
piepro start
```

On the first `piepro start`, PiePro bootstraps the full project source into the default PiePro home directory if it is not already there. On Windows this is `C:\Users\tiend\.piepro`; on other systems it is `~/.piepro`. The `config/` directory is stored there with the source, and CLI runtime metadata is kept under `.runtime/`.

You can also run `piepro init` explicitly before `piepro start`. After initialization, `piepro start`, `piepro status`, and `piepro restart` work from any directory. You do not need to `cd` into the repository.

`piepro start` starts backend and frontend from one terminal command, avoids extra terminal windows, keeps service logs under `logs/`, and opens the frontend automatically.

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
piepro init
piepro start
piepro status
piepro restart
piepro stop
piepro autostart enable
piepro autostart status
piepro autostart disable
piepro use E:\SideProjects\PiePro
```

Useful options:

```bash
piepro start --no-open
piepro start --backend-only
piepro restart --force
piepro --root E:\SideProjects\PiePro start
piepro autostart enable --open
```

Default URLs:

- Backend: `http://127.0.0.1:8000`
- API docs: `http://127.0.0.1:8000/docs`
- Frontend: `http://127.0.0.1:3000/dashboard`

Runtime files:

- Default source/config root: `C:\Users\tiend\.piepro` on Windows, `~/.piepro` elsewhere
- CLI user config: `.runtime/user_config.json`
- PID state: `runtime/piepro.pid.json`
- Backend log: `logs/backend.cli.log`
- Frontend log: `logs/frontend.cli.log`
- Windows autostart script: `%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\PieProAutostart.vbs`

## Architecture

- **Orchestrator**: accepts user messages, creates task records, plans work, spawns subagents, collects results, and stays non-blocking.
- **Agent loop**: subagents build a dynamic self/context prompt, call the provider, execute model-requested tool calls, append tool results, compact long context, and iterate to a final answer.
- **Subagents**: temporary scoped workers with lifecycle, heartbeat, permissions, allowed tools/toolsets, budget fields, logs, and result/error records.
- **Persistence**: SQLite state store under `runtime/piepro.sqlite3` for tasks, subagents, messages, tool calls, schedules, checkpoints, and local memory, with FTS search.
- **Tools**: YAML-configured registry with schema, timeout, permission, audit level, built-in handlers, and named toolsets from `config/toolsets.yaml`.
- **Providers**: provider router loaded from `config/providers/*.yaml`; local mock provider is enabled by default. Custom OpenAI-compatible providers can be configured with `provider_type: custom` and `base_url`.
- **Channels**: channel manager loaded from `config/channels/*.yaml`; Telegram is available through `TELEGRAM_BOT_TOKEN` and optional `default_chat_id`.
- **Memory**: local memory manager with optional TencentDB Agent Memory external backend.
- **Skills**: class-level procedural memory under `skills/<name>/SKILL.md`, with references/templates/scripts support and `skills.*` tools.
- **Background learning**: completed tasks are reviewed for durable memory and reusable skill updates.
- **Plugins**: local `plugins/<name>/plugin.yaml` modules can register tools, providers, channels, or memory wrappers.
- **Schedules**: simple one-shot or fixed-interval scheduled prompts submit into the orchestrator.
- **Checkpoints**: file-level checkpoints are created before filesystem writes and can be restored through the checkpoint API.
- **Self-update**: safe stable/candidate flow simulation under `runtime/bodies`, plus a `self_update.plan` tool for gated improvement planning.
- **Frontend**: Next.js operations console for dashboard, chat, task actions, subagent kill, tool execution, provider tests, memory CRUD/compact, self-update workflow, channels, logs, and config.
- **Design system**: bright minimal fintech dashboard with white/soft-gray surfaces, blue primary accents, warm yellow/orange highlights, rounded cards, subtle neumorphic shadows, and only operationally useful widgets.

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

## Providers And Channels

Custom provider config:

```yaml
# config/providers/custom.yaml
version: 1
name: custom
provider_type: custom
enabled: true
api_key_env: CUSTOM_PROVIDER_API_KEY
base_url: http://127.0.0.1:8080/v1
default_model: custom-model
```

Telegram channel config:

```yaml
# config/channels/telegram.yaml
version: 1
name: telegram
type: telegram
enabled: true
bot_token_env: TELEGRAM_BOT_TOKEN
default_chat_id: "123456789"
```

Set secrets in the environment, not in config files:

```powershell
$env:CUSTOM_PROVIDER_API_KEY = "<custom-provider-key>"
$env:TELEGRAM_BOT_TOKEN = "<telegram-bot-token>"
```

The frontend Config page can edit YAML-backed config as validated JSON, then reload tools, providers, and channels without restarting the whole runtime.

## Testing

```powershell
cd backend
..\.venv\Scripts\python.exe -m pytest
cd ..\frontend
npm run build
npm audit --audit-level=moderate
```

Current coverage includes orchestrator non-blocking behavior, task pause/resume controls, subagent lifecycle, tool registry, memory fallback/external adapter behavior, provider config loading, channel config loading, self-update promotion safety, API smoke tests, CLI parsing, and observability logs.

## Documentation Is Runtime Knowledge

PiePro treats `docs/` as part of the bot self-knowledge base. Any code change that alters behavior, config, operations, architecture, memory, security, self-update, or install flow must update the relevant docs in the same change.

The root runtime knowledge files are loaded first by convention:

- [AGENT.md](AGENT.md): agent runtime contract.
- [SOULD.md](SOULD.md): operating philosophy.
- [HEARTBEAT.md](HEARTBEAT.md): health rhythm and recovery signals.

Start here:

- [Architecture](docs/ARCHITECTURE.md)
- [Operations](docs/OPERATIONS.md)
- [Memory](docs/MEMORY.md)
- [Self-Update](docs/SELF_UPDATE.md)
- [Development](docs/DEVELOPMENT.md)
- [Design System](docs/DESIGN_SYSTEM.md)
- [Self Knowledge](docs/SELF_KNOWLEDGE.md)
- [System Review](docs/SYSTEM_REVIEW.md)
- [Documentation Policy](docs/DOCS_POLICY.md)

## Current Boundaries

- Default LLM calls use `LocalProvider`.
- Runtime state is local SQLite by default.
- TencentDB Agent Memory is optional and accessed via external gateway.
- Self-update candidate startup is simulated; promotion safety checks exist but do not yet switch live traffic.
- Frontend covers the main runtime actions; deeper charts, RBAC screens, and persistent DB adapters remain future work.
