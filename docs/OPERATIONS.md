# Operations

## Install With uv Tool

```powershell
uv tool install git+https://github.com/Monkez/PieProBot.git
piepro start
```

On the first `piepro start`, PiePro installs the full source tree into the default PiePro home directory if it is missing. On Windows this is `C:\Users\tiend\.piepro`; on other systems it is `~/.piepro`. The runtime config directory lives at `C:\Users\tiend\.piepro\config` on Windows.

You can run `piepro init` explicitly if you want to bootstrap the source before starting services.

CLI metadata is stored under `.runtime/user_config.json` inside the PiePro home directory. After initialization, `piepro start`, `piepro status`, `piepro restart`, and `piepro stop` can be run from any directory without passing `--root`.

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

`piepro start` uses the current terminal only and launches backend/frontend as background child processes without opening extra terminal windows. It opens the frontend browser when ready unless `--no-open` is used.

Use `piepro use <path>` to change the default project root without setting `PIEPRO_HOME` or passing `--root`.

Root resolution order is `--root`, `PIEPRO_HOME`, saved CLI metadata, the default PiePro home directory, current directory/parents, then installed package parents.

## Ports

- Backend: `127.0.0.1:8000`
- Frontend: `127.0.0.1:3000`
- Optional TencentDB Agent Memory Gateway: `127.0.0.1:8420`

## Config From Frontend

Open `http://127.0.0.1:3000/config` to edit config files. The editor loads YAML files as JSON, validates writes on save, rolls back invalid writes, and can hot reload tools, providers, and channels.

The Tools, Providers, and Channels pages expose direct controls for common fields such as enabled state, model, base URL, timeout, token env name, and Telegram chat ID. Saving from these pages writes back to the corresponding file under `config/`.

## Custom Providers

Add or edit `config/providers/custom.yaml`:

```yaml
version: 1
name: custom
provider_type: custom
enabled: true
api_key_env: CUSTOM_PROVIDER_API_KEY
base_url: http://127.0.0.1:8080/v1
default_model: custom-model
```

Set `$env:CUSTOM_PROVIDER_API_KEY` before starting PiePro if the provider requires a bearer token.

## Telegram Channel

Edit `config/channels/telegram.yaml`, set `enabled: true`, and provide `TELEGRAM_BOT_TOKEN` through the environment. Use the Channels page to send a test message. Incoming Telegram webhook payloads can be posted to `POST /api/channels/telegram/webhook`; PiePro turns text messages into orchestrator tasks.

## Logs

- Backend process log: `logs/backend.cli.log`
- Frontend process log: `logs/frontend.cli.log`
- API log buffer: `GET /logs`
- Task logs: `GET /logs/tasks/{task_id}`
- Subagent logs: `GET /logs/subagents/{subagent_id}`

## Troubleshooting

On Windows, PiePro starts child processes with `CREATE_NO_WINDOW` to avoid extra terminal windows. A dev server can occasionally outlive or replace the wrapper PID stored in `runtime/piepro.pid.json`. `piepro status` treats a healthy HTTP endpoint as running even if the original PID is stale. Frontend status uses a longer HTTP timeout because Next.js dev pages may take a few seconds to respond after rebuilds. Use `piepro restart --force` to refresh PID state.

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
