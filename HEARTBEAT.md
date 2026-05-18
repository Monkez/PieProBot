# PiePro Heartbeat

This file defines the health rhythm PiePro should use to understand itself.

## Startup Heartbeat

1. Resolve project root.
2. Load config.
3. Load providers.
4. Load channels.
5. Load tools.
6. Boot orchestrator and subagent manager.
7. Expose `/health`, `/ready`, `/metrics`, and admin frontend.

## Runtime Heartbeat

- Backend health: `GET /health`.
- Readiness: `GET /ready`.
- Metrics: `GET /metrics`.
- Windows autostart status: `piepro autostart status`.
- Channels: `GET /api/channels`.
- Providers: `GET /api/providers/status`.
- Tools: `GET /api/tools`.
- Tasks: `GET /api/tasks`.
- Subagents: `GET /api/subagents`.

## Failure Signals

- Lost subagent heartbeat.
- Provider chain failure.
- Tool timeout.
- Invalid config write.
- Channel send failure.
- Candidate update healthcheck failure.
- Frontend action failure on task, memory, provider, tool, channel, or self-update operations.

## Recovery Actions

- Keep the orchestrator responsive.
- Mark failed subagents and allow retry.
- Fall back to local provider or memory when configured.
- Roll back invalid config writes.
- Keep stable body active if self-update candidate fails.
