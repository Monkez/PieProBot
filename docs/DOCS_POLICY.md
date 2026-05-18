# Documentation Policy

PiePro documentation is part of the system contract and bot self-knowledge.

## Mandatory Updates

Update docs in the same change when modifying:

- CLI commands or install flow.
- API endpoints.
- Config file shape.
- Memory behavior.
- Tool permissions.
- Provider routing.
- Self-update behavior.
- Security controls.
- Frontend workflows.
- Operational troubleshooting.

## Source of Truth

- `README.md`: user-facing overview and quick start.
- `docs/ARCHITECTURE.md`: module boundaries and flow.
- `docs/OPERATIONS.md`: local operations.
- `docs/MEMORY.md`: memory behavior.
- `docs/SELF_UPDATE.md`: update safety model.
- `docs/DEVELOPMENT.md`: engineering workflow.
- `docs/SELF_KNOWLEDGE.md`: concise bot self-model.

## Rule for Agents

When PiePro or a developer changes behavior, the same task is incomplete until the relevant documentation is updated.

