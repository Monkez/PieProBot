# Architecture

PiePro is a local-first AI agent platform. It is designed to be lightweight, fast to start, and easy to inspect.

## Runtime Modules

### Backend

Path: `backend/app`

- FastAPI application: `backend/app/main.py`
- API routers: `backend/app/api`
- Orchestrator: `backend/app/core/orchestrator.py`
- Planner: `backend/app/core/planner.py`
- Agent loop: `backend/app/agent/loop.py`
- System prompt builder: `backend/app/agent/system_prompt.py`
- Context engine: `backend/app/agent/context_engine.py`
- Background review: `backend/app/agent/background_review.py`
- Learning policy/applier: `backend/app/learning`
- Skill curator: `backend/app/agent/curator.py`
- Subagent manager: `backend/app/subagents/manager.py`
- Tool registry: `backend/app/tools/registry.py`
- Provider router: `backend/app/providers/router.py`
- Channel manager: `backend/app/channels/manager.py`
- Memory manager: `backend/app/memory/manager.py`
- Skill store: `backend/app/skills/store.py`
- SQLite runtime state: `backend/app/db/session.py`
- Scheduler: `backend/app/scheduler/manager.py`
- Plugin manager: `backend/app/plugins/manager.py`
- Checkpoint manager: `backend/app/tools/checkpoint.py`
- Self-update manager: `backend/app/self_update/manager.py`
- Observability: `backend/app/observability`

### Frontend

Path: `frontend`

Next.js admin console with pages for dashboard, chat, tasks, subagents, tools, providers, channels, memory, self-update, logs, and config.

The shared UI shell uses a bright minimal fintech dashboard aesthetic: white and soft-gray surfaces, rounded frame, left sidebar navigation, blue primary accents, warm yellow/orange highlights, rounded widgets, and subtle neumorphic shadows.

Frontend route transitions are intentionally client-first: pages render immediately, then fetch operational data from the API after navigation. Sidebar routes are prefetched to keep tab switching responsive.

### CLI

Path: `piepro/cli.py`

The `piepro` CLI manages local processes without Docker:

- `piepro init`
- `piepro start`
- `piepro status`
- `piepro restart`
- `piepro stop`
- `piepro autostart enable|disable|status`

For uv tool installs, `piepro start` auto-bootstraps the project source and `config/` into `~/.piepro` by default when no root exists. On Windows for the current user this is `C:\Users\tiend\.piepro`. `piepro init` can be used to run the same bootstrap explicitly.

## Request Flow

1. User sends a chat message to `POST /api/chat` or `POST /api/chat/wait`.
2. Orchestrator creates a task record.
3. Planner creates a structured task plan.
4. Subagent manager spawns a scoped subagent.
5. Toolsets resolve the plan's requested capabilities into concrete allowed tools.
6. Subagent manager applies concurrency, depth, budget, and blocked-tool limits.
7. Agent loop builds the dynamic system prompt from identity, runtime context, memory, skills, allowed tools, and execution discipline.
8. Provider response may contain JSON tool calls. The agent loop executes allowed tools, appends tool results, compacts long context, and repeats.
9. Orchestrator collects result and finalizes task.
10. SQLite persists tasks, subagents, messages, tool calls, local memory, and learning proposals with FTS search.
11. Memory manager stores task summary and captures the user/assistant turn.
12. Background review creates learning proposals, policy classifies them as safe/review/blocked, and only safe items are auto-applied.
13. Channel webhooks, such as Telegram, can submit inbound messages into the orchestrator as tasks.
14. Logs include correlation ID, task ID, and subagent ID where available.

## Non-Blocking Principle

The orchestrator must stay responsive. Heavy work is delegated to subagents via `asyncio.create_task`. Blocking IO should be wrapped or delegated.

## Extension Points

- Add providers under `backend/app/providers`.
- Add channels under `backend/app/channels` and `config/channels`.
- Add tools under `backend/app/tools/builtins` and `config/tools`.
- Add memory backends under `backend/app/memory`.
- Add local plugins under `plugins/<name>/plugin.yaml` with a Python module exposing `register(ctx)`.
- Add frontend views under `frontend/app`.

Plugins can register providers, channels, memory wrappers, and tool definitions without changing core modules. Runtime discovery is local-only and opt-out via `enabled: false` in the plugin manifest.

## Runtime Persistence

PiePro stores runtime state in `runtime/piepro.sqlite3`. The SQLite store uses WAL mode and FTS5 tables for task, message, and memory search. It is still treated as local operational state, not as an external dependency.

Search across persisted tasks/messages/memory:

```bash
GET /api/state/search?q=<term>
```

## Toolsets And Subagents

Toolsets live in `config/toolsets.yaml`. The planner requests both explicit tools and named toolsets; the registry resolves them before spawning a subagent. Subagent limits are configured in `config/agent/subagents.yaml`:

- `max_concurrent`
- `max_spawn_depth`
- `blocked_tools`
- heartbeat settings

Blocked tools are stripped from child agents even if a plan requests a toolset that contains them.

## Agent Cognition Loop

PiePro subagents use `AgentLoop` instead of a single provider call. A model can request tool execution by returning JSON:

```json
{"tool_calls":[{"name":"echo","arguments":{"text":"hello"}}]}
```

The loop executes only tools already granted to the subagent, stores tool call records, feeds the result back as a `tool` message, and asks the provider again. This continues until the model returns a normal final response or the iteration/tool budget is exhausted.

The system prompt builder injects:

- PiePro identity and self-knowledge.
- `AGENT.md`, `SOULD.md`, `HEARTBEAT.md`, and `docs/SELF_KNOWLEDGE.md`.
- Fenced memory context.
- Relevant skills from the skill store.
- Allowed tools/toolsets and tool-call JSON contract.
- Execution discipline for tool use, memory, and skills.

## Skills And Learning

Skills live under `skills/<name>/SKILL.md` and may include:

- `references/`
- `templates/`
- `scripts/`
- `assets/`

Runtime tools:

- `skills.list`
- `skills.view`
- `skills.manage`
- `curator.run`

Completed tasks pass through `BackgroundReview`, which now uses a hybrid learning pipeline:

- `LearningReviewer` proactively proposes memory and skill updates from completed work.
- `LearningPolicy` blocks transient task progress, likely secrets, and narrow one-off skills.
- `LearningApplier` auto-applies safe items such as explicit durable preferences and class-level skill references.
- Review items stay in SQLite until an operator approves or rejects them through `/api/learning/proposals`.

`SkillCurator` remains conservative and proposes umbrella-skill consolidations. It can create umbrella skills when run with `dry_run=false`.

## Scheduler And Checkpoints

The scheduler is a simple local task submitter backed by SQLite. It supports one-shot `run_at` timestamps and fixed `every_seconds` intervals through `/api/schedules`.

Filesystem writes and shell commands with `checkpoint_paths` create file-level checkpoints before mutation. Rollback is exposed through:

```bash
POST /api/checkpoints/{checkpoint_id}/rollback
```
