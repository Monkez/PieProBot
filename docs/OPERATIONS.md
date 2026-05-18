# Operations

## Install With uv Tool

```powershell
uv tool install git+https://github.com/Monkez/PieProBot.git
piepro init PieProBot
cd PieProBot
piepro start
```

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
```

`piepro start` uses the current terminal only and launches backend/frontend as background child processes. It opens the frontend when ready unless `--no-open` is used.

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

