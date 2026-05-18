# PiePro Self Knowledge

This document is the compact self-description PiePro should use to understand its own runtime.

## Identity

- Canonical name: PiePro
- Repository: `https://github.com/Monkez/PieProBot.git`
- Primary install method: `uv tool install git+https://github.com/Monkez/PieProBot.git`
- Local command: `piepro`
- `piepro start` auto-installs the full source tree into the default PiePro home if it is missing; `piepro init` can do the same bootstrap explicitly.

## Runtime Facts

- Backend framework: FastAPI
- Frontend framework: Next.js
- Frontend design language: bright minimal fintech dashboard with white/soft-gray surfaces, blue primary accents, warm yellow/orange highlights, rounded cards, subtle neumorphic shadows, and premium SaaS spacing. Use the style without adding unnecessary decorative modules.
- Navigation is topbar-only by default; no sidebar unless explicitly requested.
- Runtime style: local-first, no Docker required
- State: in-memory by default
- External memory: TencentDB Agent Memory via TDAI Gateway
- Providers: local, OpenAI, OpenAI-compatible, and custom OpenAI-compatible providers loaded from `config/providers/*.yaml`; custom providers use `base_url`.
- Channels: Telegram channel support loaded from `config/channels/telegram.yaml`; secrets stay in environment variables such as `TELEGRAM_BOT_TOKEN`.
- Config UI: frontend Config page can edit YAML-backed config as JSON, validate, and hot reload tools/providers/channels.
- Config rollback is implemented in-process for the last saved versions during the current backend runtime.
- Process manager: `piepro/cli.py`
- Windows process launch avoids extra terminal windows with `CREATE_NO_WINDOW`.
- Default installed source/config root: `~/.piepro`; on Windows for the current user this is `C:\Users\tiend\.piepro`.
- User config path: `~/.piepro/.runtime/user_config.json`
- Docs are part of operational memory and must be kept updated.
- Design system docs are part of self-knowledge and must be preserved during UI changes.
- Root knowledge files: `AGENT.md`, `SOULD.md`, and `HEARTBEAT.md`.
- Frontend routes must render quickly; operational pages should fetch data client-side after navigation.
- Tools, providers, and channels can be enabled, disabled, and edited from the frontend, then saved to YAML config files.
- Task, subagent, memory, tool, provider, channel, and self-update actions are available from the frontend and call real backend APIs.
- Pause/retry cancel existing task runners and active subagents before restarting work.

## Invariants

- Orchestrator must not block on heavy work.
- Subagents are scoped, temporary workers.
- Tool permissions must be checked before execution.
- Shell tool stays disabled by default.
- Secrets must not be logged or stored in memory.
- Telegram bot tokens and provider API keys must remain environment variables, not checked into config.
- Self-update must use candidate copies.
- TencentDB memory failure must fall back to local memory.

## Current Known Limitations

- Default provider is `LocalProvider`.
- Persistent database adapters are future work.
- Self-update candidate start is a simulation.
- Frontend is an operational MVP, not a full enterprise console yet.
