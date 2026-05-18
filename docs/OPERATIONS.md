# Operations

## Install With uv Tool

```powershell
uv tool install git+https://github.com/Monkez/PieProBot.git
piepro init PieProBot
piepro start
```

`piepro init` saves the cloned path as the default PiePro root in the user config file at `~/.piepro/config.json`. After initialization, `piepro start`, `piepro status`, `piepro restart`, and `piepro stop` can be run from any directory.

## Local Editable Install

```powershell
uv venv .venv --python 3.12
uv pip install --python .\.venv\Scripts\python.exe -e ".[test]"
cd frontend
npm install
cd ..
.\.venv\Scripts\piepro.exe start
```

## Process Commands

```bash
piepro start
piepro status
piepro restart
piepro stop
piepro use E:\SideProjects\PiePro
```

`piepro start` uses the current terminal only and launches backend/frontend as background child processes. It opens the frontend when ready unless `--no-open` is used.

Use `piepro use <path>` to change the default project root without setting `PIEPRO_HOME` or passing `--root`.

## Ports

- Backend: `127.0.0.1:8000`
- Frontend: `127.0.0.1:3000`
- Optional TencentDB Agent Memory Gateway: `127.0.0.1:8420`

## Logs

- Backend process log: `logs/backend.cli.log`
- Frontend process log: `logs/frontend.cli.log`
- API log buffer: `GET /logs`
- Task logs: `GET /logs/tasks/{task_id}`
- Subagent logs: `GET /logs/subagents/{subagent_id}`

## Troubleshooting

On Windows, a dev server can occasionally outlive or replace the wrapper PID stored in `runtime/piepro.pid.json`. `piepro status` treats a healthy HTTP endpoint as running even if the original PID is stale. Use `piepro restart --force` to refresh PID state.

If `piepro status` shows a stale process, run:

```bash
piepro restart --force
```

If frontend fails, verify:

```bash
cd frontend
npm install
npm run build
```

If backend fails, verify:

```bash
cd backend
../.venv/Scripts/python.exe -m pytest
```
