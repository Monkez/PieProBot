# Memory

PiePro memory has two layers:

- Local SQLite-backed fallback managed by `MemoryManager`.
- Optional TencentDB Agent Memory external backend through TDAI Gateway.

## Local Memory

Local memory stores:

- User messages.
- Task summaries.
- Conversation turns.

Local memory is restored from `runtime/piepro.sqlite3` on backend startup and indexed with FTS5. In-memory state remains the hot working set, while SQLite is the durable local store.

Background review may add explicit user preferences after completed tasks, but it now goes through the learning policy first. Durable preferences can be auto-applied; transient task progress, likely secrets, and one-off facts are blocked or sent to review. Procedural lessons should go to skills instead of memory; memory remains for durable facts about the user, project, or environment.

It supports:

- `save`
- `retrieve`
- `search`
- `update`
- `delete`
- `summarize`
- `compact`

## TencentDB Agent Memory

Adapter path: `backend/app/memory/tencentdb_agent_memory.py`

Config path: `config/memory/tencentdb_agent_memory.yaml`

The adapter calls:

- `GET /health`
- `POST /capture`
- `POST /search/memories`
- `POST /search/conversations`

The gateway is not embedded in PiePro. It is started separately from `Tencent/TencentDB-Agent-Memory`.

## Fallback Rule

If external memory is enabled but unavailable, PiePro must continue using local memory. External memory failure must not break chat, task finalization, or search.

## Status

Use:

```bash
GET /api/memory/status
```

Fields:

- `local_items`
- `external_enabled`
- `external_healthy`
- `external_base_url`
- `external_error`
