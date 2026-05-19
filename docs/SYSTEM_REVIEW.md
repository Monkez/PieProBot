# System Review

Last reviewed: 2026-05-19.

## Strengths

- Simple install path: `uv tool install ...` plus `piepro start`; source and config live under the PiePro home directory.
- Local-first runtime with no required Docker, database, queue, or cloud dependency.
- Async orchestrator delegates work to subagents and keeps the request path responsive.
- Runtime state is persisted in local SQLite for tasks, subagents, messages, tool calls, schedules, checkpoints, memory, and learning proposals.
- Control-plane API routes can be protected with `ADMIN_API_KEY`; frontend requests can send the key through `NEXT_PUBLIC_ADMIN_API_KEY` or `localStorage.piepro_api_key`.
- Tool execution permissions are derived from the authenticated server-side role, not from client-supplied permission flags.
- Config writes now run schema-aware validation for providers, tools, channels, memory, agent, and security config groups.
- Admin frontend routes are static/client-first, so navigation is fast and API calls happen after render.
- Common runtime actions are wired to real APIs: task control, subagent kill, tool execution, provider tests, memory CRUD/compact, channel send, config save/reload/rollback, and self-update workflow actions.
- Config is file-backed YAML with validation and direct frontend editing.
- Provider layer supports local, OpenAI, OpenAI-compatible, and custom `base_url` providers.
- Telegram channel support keeps secrets in environment variables.
- Windows process launch and autostart avoid extra terminal windows.
- Tests cover orchestrator responsiveness, task controls, config rollback, tools, providers, channels, memory, self-update safety, CLI parsing, and API smoke paths.

## Weaknesses

- SQLite schema creation is direct and does not yet have migrations, schema versions, or downgrade/upgrade tooling.
- Self-update now runs real pytest when a candidate contains a test suite, but candidate startup/promotion is still not a production process supervisor with live traffic handoff.
- Planner and local provider are deterministic MVP implementations, not full LLM planning/model routing yet.
- Role-based access control is enforced for core config/provider/promote/tool permissions, but there is still only a single API-key admin identity by default.
- Tool execution sandboxing is conservative but not a hardened OS/container sandbox, and shell should remain disabled unless the runtime is locked to trusted local users.
- Observability is useful for local diagnosis but lacks full OpenTelemetry export and persistent log storage.
- Frontend config editing uses JSON representation of YAML; it is functional but not a rich schema-aware form for every nested field.

## Missing Or Incomplete Capabilities

- Persistent database adapters for tasks, artifacts, audit logs, and memory.
- SQLite migration/versioning layer.
- Production-grade supervisor for stable/candidate promotion, traffic handoff, and rollback.
- Real model routing UI and per-provider cost/token dashboards.
- Full approval queue for dangerous actions.
- Multi-user/session authentication beyond the local admin API key.
- Persistent scheduler for health checks, memory compaction, cleanup, and recurring tasks.
- Artifact browser for task outputs beyond simple task records.
- Telegram webhook registration helper and inbound auto-reply flow.
- Durable config history across process restarts.
- Packaged frontend asset strategy for running without a Next dev server.

## Recommended Next Work

1. Add SQLite migrations and optional PostgreSQL adapter.
2. Add a multi-user auth/session layer before exposing the admin UI beyond localhost.
3. Replace self-update startup/promotion simulation with a real process supervisor and stable/candidate traffic switch.
4. Add artifact storage and task output viewer.
5. Add a scheduler and durable background jobs.
6. Add schema-aware config forms for providers, tools, channels, memory, and security.
