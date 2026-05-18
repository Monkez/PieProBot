# Architecture

PiePro is a local-first AI agent platform. It is designed to be lightweight, fast to start, and easy to inspect.

## Runtime Modules

### Backend

Path: `backend/app`

- FastAPI application: `backend/app/main.py`
- API routers: `backend/app/api`
- Orchestrator: `backend/app/core/orchestrator.py`
- Planner: `backend/app/core/planner.py`
- Subagent manager: `backend/app/subagents/manager.py`
- Tool registry: `backend/app/tools/registry.py`
- Provider router: `backend/app/providers/router.py`
- Memory manager: `backend/app/memory/manager.py`
- Self-update manager: `backend/app/self_update/manager.py`
- Observability: `backend/app/observability`

### Frontend

Path: `frontend`

Next.js admin console with pages for dashboard, chat, tasks, subagents, tools, providers, memory, self-update, logs, and config.

The shared UI shell uses a bright minimal fintech dashboard aesthetic: white and soft-gray surfaces, rounded frame, floating top navigation, blue primary accents, warm yellow/orange highlights, rounded widgets, and subtle neumorphic shadows. Navigation remains topbar-only unless explicitly changed.

### CLI

Path: `piepro/cli.py`

The `piepro` CLI manages local processes without Docker:

- `piepro init`
- `piepro start`
- `piepro status`
- `piepro restart`
- `piepro stop`

For uv tool installs, `piepro start` auto-bootstraps the project source and `config/` into `~/.piepro` by default when no root exists. On Windows for the current user this is `C:\Users\tiend\.piepro`. `piepro init` can be used to run the same bootstrap explicitly.

## Request Flow

1. User sends a chat message to `POST /api/chat` or `POST /api/chat/wait`.
2. Orchestrator creates a task record.
3. Planner creates a structured task plan.
4. Subagent manager spawns a scoped subagent.
5. Subagent runs with allowed tools and provider router.
6. Orchestrator collects result and finalizes task.
7. Memory manager stores task summary and captures the user/assistant turn.
8. Logs include correlation ID, task ID, and subagent ID where available.

## Non-Blocking Principle

The orchestrator must stay responsive. Heavy work is delegated to subagents via `asyncio.create_task`. Blocking IO should be wrapped or delegated.

## Extension Points

- Add providers under `backend/app/providers`.
- Add tools under `backend/app/tools/builtins` and `config/tools`.
- Add memory backends under `backend/app/memory`.
- Add frontend views under `frontend/app`.
