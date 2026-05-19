# Development

## Test

```powershell
cd backend
..\.venv\Scripts\python.exe -m pytest
```

## Frontend Build

```powershell
cd frontend
npm run build
npm audit --audit-level=moderate
```

## Package Install

```powershell
uv pip install --python .\.venv\Scripts\python.exe -e ".[test]"
```

## CLI Root Resolution

`piepro` resolves the project root in this order:

1. `--root`.
2. `PIEPRO_HOME`.
3. Saved user config at `~/.piepro/.runtime/user_config.json`.
4. Default project root at `~/.piepro`.
5. Current directory and parents.
6. Installed package parents.

`piepro start` auto-runs the default bootstrap when no root is found, installing the full source tree into `~/.piepro` by default, including `config/`. On Windows for the current user this maps to `C:\Users\tiend\.piepro`. `piepro init` performs the same bootstrap explicitly, and `piepro init`/`piepro use` update the saved user config.

Status checks prefer live HTTP health over PID liveness because Windows dev-server wrappers can exit while the actual server process keeps serving.

## Change Checklist

For every code change:

1. Update tests or explain why tests are not needed.
2. Update docs if behavior/config/install/architecture/security/memory changes.
3. Run backend tests.
4. Run frontend build if frontend or shared install changes.
5. Run `npm audit --audit-level=moderate` if frontend dependencies change.

## Runtime Extension Tests

When changing persistence, plugins, toolsets, scheduler, checkpoints, or subagent limits, update `backend/tests/test_runtime_extensions.py`. These features are intentionally local and dependency-light, so tests should use temporary SQLite files and temporary plugin directories instead of external services.

The same test file also covers the agent cognition layer: model-requested tool calls, tool-call persistence, background review, and skill creation. Add focused tests there when changing `backend/app/agent` or `backend/app/skills`.

## Local Plugin Shape

A plugin directory looks like:

```text
plugins/demo/
  plugin.yaml
  plugin.py
```

`plugin.yaml`:

```yaml
name: demo
module: plugin.py
enabled: true
```

`plugin.py` exposes `register(ctx)` and may call `ctx.register_tool`, `ctx.register_provider`, `ctx.register_channel`, or `ctx.register_memory`.

## Naming

The canonical bot/product name is **PiePro**. Do not introduce new user-facing names unless explicitly approved.
