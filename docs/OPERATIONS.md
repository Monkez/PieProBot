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
piepro autostart enable
piepro autostart status
piepro autostart disable
piepro use E:\SideProjects\PiePro
```

`piepro start` uses the current terminal only and launches backend/frontend as background child processes without opening extra terminal windows. It opens the frontend browser when ready unless `--no-open` is used.

Use `piepro use <path>` to change the default project root without setting `PIEPRO_HOME` or passing `--root`.

Root resolution order is `--root`, `PIEPRO_HOME`, saved CLI metadata, the default PiePro home directory, current directory/parents, then installed package parents.

## Windows Autostart

```powershell
piepro autostart enable
piepro autostart status
piepro autostart disable
```

`piepro autostart enable` creates `%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\PieProAutostart.vbs`. The script runs PiePro through `pythonw` with `--no-open`, so Windows sign-in starts backend/frontend without opening an extra terminal window. Use `piepro autostart enable --open` if the browser should open on sign-in.

## Ports

- Backend: `127.0.0.1:8000`
- Frontend: `127.0.0.1:3000`
- Optional TencentDB Agent Memory Gateway: `127.0.0.1:8420`

## Config From Frontend

Open `http://127.0.0.1:3000/config` to edit config files. The editor loads YAML files as JSON, validates writes on save, rolls back invalid writes automatically, supports explicit rollback of the last saved version, and can hot reload tools, providers, and channels.

For trusted localhost development, the backend allows admin control-plane access when `ADMIN_API_KEY` is not set. Before exposing PiePro outside the local machine, set an API key:

```powershell
$env:ADMIN_API_KEY = "<local-admin-key>"
$env:NEXT_PUBLIC_ADMIN_API_KEY = "<local-admin-key>"
```

The backend protects `/api/*`, `/ready`, `/metrics`, and `/logs` with `x-api-key` when `ADMIN_API_KEY` is set. The frontend sends the key from `NEXT_PUBLIC_ADMIN_API_KEY`, or from browser local storage key `piepro_api_key` if you prefer not to bake it into the frontend environment.

The Tools, Providers, and Channels pages expose direct controls for common fields such as enabled state, model, base URL, timeout, token env name, and Telegram chat ID. Saving from these pages writes back to the corresponding file under `config/`.

Operational pages now perform the common runtime actions directly:

- Chat: send text, images, files, and browser-recorded voice notes into agent tasks.
- Tasks: create, pause, resume, cancel, and retry.
- Subagents: inspect status and kill active workers.
- Tools: edit config and execute test calls.
- Providers: edit config and test a provider or fallback chain.
- Memory: search, create, delete, and compact.
- Self-Update: detect, plan, create candidate, test, start, healthcheck, promote, rollback, report, and destroy failed candidates.

## Runtime State

PiePro persists operational state in:

```text
runtime/piepro.sqlite3
```

The database stores tasks, subagents, messages, tool calls, local memory items, schedules, learning proposals, and checkpoint metadata. Search persisted state with:

```bash
GET /api/state/search?q=memory
```

## Scheduled Tasks

Create simple local schedules through the API:

```bash
POST /api/schedules
```

Payloads support either:

- `every_seconds`: recurring interval.
- `run_at`: Unix timestamp for a one-shot task.

The scheduler submits due prompts into the normal orchestrator path. Use `POST /api/schedules/tick` for a manual tick during development.

## Checkpoints

Filesystem writes automatically create a file-level checkpoint. Shell commands can opt into checkpointing by passing `workspace` and `checkpoint_paths` in the tool payload. Roll back with:

```bash
POST /api/checkpoints/{checkpoint_id}/rollback
```

Checkpoints are stored under `runtime/checkpoints/`.

## Skills

Skills are stored under:

```text
skills/<name>/SKILL.md
```

Use the API to inspect or manage them:

```bash
GET /api/skills
GET /api/skills/{name}
POST /api/skills
POST /api/skills/{name}/patch
POST /api/skills/curator/run
```

The curator endpoint defaults to dry-run mode. Pass `dry_run=false` only when you want it to create umbrella skills.

## Hybrid Learning

Completed tasks can produce learning proposals. Safe items are auto-applied; review items wait for operator approval; blocked items are retained with a reason.

```bash
GET /api/learning/proposals
GET /api/learning/proposals?status=pending
GET /api/learning/proposals/{proposal_id}
POST /api/learning/proposals/{proposal_id}/approve
POST /api/learning/proposals/{proposal_id}/reject
```

Use approval for skill patches, archives, or other higher-impact learning. Explicit durable preferences and class-level skill references are normally safe enough to apply automatically.

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
model_profiles:
  fast: cheap-or-low-latency-model
  normal: balanced-model
  power: strongest-model
```

Set `$env:CUSTOM_PROVIDER_API_KEY` before starting PiePro if the provider requires a bearer token.

The Providers page can create new provider YAML files under `config/providers/`. PiePro routes Bot calls through three model profiles:

- `fast`: low-latency/background utility work.
- `normal`: default chat and research work.
- `power`: coding, deployment, and high-complexity subagents.

If a provider key is entered directly into the Providers page instead of an environment variable name, PiePro stores it under `runtime/provider_secrets.json` and loads it on startup. That file is ignored by git, but it is plaintext local storage; prefer environment variables or an OS secret manager for shared machines.

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
