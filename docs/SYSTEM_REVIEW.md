# System Review

Last reviewed: 2026-05-19.

## Strengths

- Simple install path: `uv tool install ...` plus `piepro start`; source and config live under the PiePro home directory.
- Local-first runtime with no required Docker, database, queue, or cloud dependency.
- Async orchestrator delegates work to subagents and keeps the request path responsive.
- Admin frontend routes are static/client-first, so navigation is fast and API calls happen after render.
- Common runtime actions are wired to real APIs: task control, subagent kill, tool execution, provider tests, memory CRUD/compact, channel send, config save/reload/rollback, and self-update workflow actions.
- Config is file-backed YAML with validation and direct frontend editing.
- Provider layer supports local, OpenAI, OpenAI-compatible, and custom `base_url` providers.
- Telegram channel support keeps secrets in environment variables.
- Windows process launch and autostart avoid extra terminal windows.
- Tests cover orchestrator responsiveness, task controls, config rollback, tools, providers, channels, memory, self-update safety, CLI parsing, and API smoke paths.

## Weaknesses

- Runtime state is still in-memory by default; tasks, subagents, and local memory do not survive backend restart.
- Self-update is a safety-model simulation: candidate copy, test flags, healthcheck, promotion pointer, and rollback exist, but live traffic is not switched by a process supervisor.
- Planner and local provider are deterministic MVP implementations, not full LLM planning/model routing yet.
- Role-based access control and authentication are only architectural/security scaffolding, not enforced across the frontend.
- Tool execution sandboxing is conservative but not a hardened OS/container sandbox.
- Observability is useful for local diagnosis but lacks full OpenTelemetry export and persistent log storage.
- Frontend config editing uses JSON representation of YAML; it is functional but not a rich schema-aware form for every nested field.

## Missing Or Incomplete Capabilities

- Persistent database adapters for tasks, artifacts, audit logs, and memory.
- Production-grade supervisor for stable/candidate promotion, traffic handoff, and rollback.
- Real model routing UI and per-provider cost/token dashboards.
- Full approval queue for dangerous actions.
- User/session authentication and RBAC enforcement in API middleware.
- Persistent scheduler for health checks, memory compaction, cleanup, and recurring tasks.
- Artifact browser for task outputs beyond simple task records.
- Telegram webhook registration helper and inbound auto-reply flow.
- Durable config history across process restarts.
- Packaged frontend asset strategy for running without a Next dev server.

## Recommended Next Work

1. Add persistence: SQLite first, then PostgreSQL optional.
2. Add auth/RBAC middleware before exposing the admin UI beyond localhost.
3. Replace self-update simulation with a real process supervisor and stable/candidate traffic switch.
4. Add artifact storage and task output viewer.
5. Add a scheduler and durable background jobs.
6. Add schema-aware config forms for providers, tools, channels, memory, and security.
