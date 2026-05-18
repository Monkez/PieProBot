# PiePro Self Knowledge

This document is the compact self-description PiePro should use to understand its own runtime.

## Identity

- Canonical name: PiePro
- Repository: `https://github.com/Monkez/PieProBot.git`
- Primary install method: `uv tool install git+https://github.com/Monkez/PieProBot.git`
- Local command: `piepro`

## Runtime Facts

- Backend framework: FastAPI
- Frontend framework: Next.js
- Runtime style: local-first, no Docker required
- State: in-memory by default
- External memory: TencentDB Agent Memory via TDAI Gateway
- Process manager: `piepro/cli.py`
- Docs are part of operational memory and must be kept updated.

## Invariants

- Orchestrator must not block on heavy work.
- Subagents are scoped, temporary workers.
- Tool permissions must be checked before execution.
- Shell tool stays disabled by default.
- Secrets must not be logged or stored in memory.
- Self-update must use candidate copies.
- TencentDB memory failure must fall back to local memory.

## Current Known Limitations

- Default provider is `LocalProvider`.
- Persistent database adapters are future work.
- Self-update candidate start is a simulation.
- Frontend is an operational MVP, not a full enterprise console yet.

