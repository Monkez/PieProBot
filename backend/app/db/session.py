from __future__ import annotations

import json
import sqlite3
import threading
import time
from pathlib import Path
from typing import Any

from app.core.task_model import SubagentRecord, TaskRecord
from app.memory.manager import MemoryItem


class SQLiteStateStore:
    """Small SQLite persistence layer for PiePro runtime state.

    The store intentionally avoids an ORM. PiePro's runtime models are already
    Pydantic objects, and JSON columns keep schema changes cheap while FTS gives
    useful local search across messages, tasks, and memory.
    """

    def __init__(self, path: Path) -> None:
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.RLock()
        self._conn = sqlite3.connect(self.path, check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        self._init_schema()

    def close(self) -> None:
        with self._lock:
            self._conn.close()

    def _init_schema(self) -> None:
        with self._lock:
            self._conn.execute("PRAGMA journal_mode=WAL")
            self._conn.execute("PRAGMA foreign_keys=ON")
            self._conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS tasks (
                    id TEXT PRIMARY KEY,
                    status TEXT NOT NULL,
                    message TEXT NOT NULL,
                    priority INTEGER NOT NULL,
                    owner TEXT NOT NULL,
                    data_json TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS subagents (
                    id TEXT PRIMARY KEY,
                    task_id TEXT NOT NULL,
                    type TEXT NOT NULL,
                    status TEXT NOT NULL,
                    data_json TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS messages (
                    id TEXT PRIMARY KEY,
                    task_id TEXT,
                    session_id TEXT,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    metadata_json TEXT NOT NULL,
                    created_at REAL NOT NULL
                );

                CREATE TABLE IF NOT EXISTS tool_calls (
                    id TEXT PRIMARY KEY,
                    task_id TEXT,
                    subagent_id TEXT,
                    tool_name TEXT NOT NULL,
                    payload_json TEXT NOT NULL,
                    result_json TEXT,
                    ok INTEGER NOT NULL,
                    error TEXT,
                    checkpoint_id TEXT,
                    created_at REAL NOT NULL,
                    finished_at REAL
                );

                CREATE TABLE IF NOT EXISTS memory_items (
                    id TEXT PRIMARY KEY,
                    type TEXT NOT NULL,
                    content TEXT NOT NULL,
                    source TEXT NOT NULL,
                    importance REAL NOT NULL,
                    data_json TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS scheduled_tasks (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    prompt TEXT NOT NULL,
                    schedule_json TEXT NOT NULL,
                    enabled INTEGER NOT NULL,
                    next_run_at REAL,
                    last_run_at REAL,
                    last_status TEXT,
                    last_error TEXT,
                    created_at REAL NOT NULL,
                    updated_at REAL NOT NULL
                );

                CREATE TABLE IF NOT EXISTS checkpoints (
                    id TEXT PRIMARY KEY,
                    label TEXT NOT NULL,
                    workspace TEXT NOT NULL,
                    data_json TEXT NOT NULL,
                    created_at REAL NOT NULL
                );

                CREATE TABLE IF NOT EXISTS learning_proposals (
                    id TEXT PRIMARY KEY,
                    task_id TEXT NOT NULL,
                    status TEXT NOT NULL,
                    data_json TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );

                CREATE VIRTUAL TABLE IF NOT EXISTS messages_fts
                USING fts5(id UNINDEXED, task_id UNINDEXED, role UNINDEXED, content);
                CREATE VIRTUAL TABLE IF NOT EXISTS memory_fts
                USING fts5(id UNINDEXED, type UNINDEXED, content);
                CREATE VIRTUAL TABLE IF NOT EXISTS tasks_fts
                USING fts5(id UNINDEXED, status UNINDEXED, message);
                """
            )
            self._conn.commit()

    @staticmethod
    def _json(data: Any) -> str:
        return json.dumps(data, ensure_ascii=False, default=str)

    def save_task(self, task: TaskRecord) -> None:
        data = task.model_dump(mode="json")
        with self._lock:
            self._conn.execute(
                """
                INSERT INTO tasks(id, status, message, priority, owner, data_json, created_at, updated_at)
                VALUES(?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    status=excluded.status,
                    message=excluded.message,
                    priority=excluded.priority,
                    owner=excluded.owner,
                    data_json=excluded.data_json,
                    updated_at=excluded.updated_at
                """,
                (
                    task.id,
                    str(task.status),
                    task.message,
                    task.priority,
                    task.owner,
                    self._json(data),
                    data["created_at"],
                    data["updated_at"],
                ),
            )
            self._conn.execute("DELETE FROM tasks_fts WHERE id = ?", (task.id,))
            self._conn.execute(
                "INSERT INTO tasks_fts(id, status, message) VALUES(?, ?, ?)",
                (task.id, str(task.status), task.message),
            )
            self._conn.commit()

    def load_tasks(self) -> list[TaskRecord]:
        with self._lock:
            rows = self._conn.execute("SELECT data_json FROM tasks ORDER BY created_at").fetchall()
        return [TaskRecord.model_validate_json(row["data_json"]) for row in rows]

    def save_subagent(self, record: SubagentRecord) -> None:
        data = record.model_dump(mode="json")
        with self._lock:
            self._conn.execute(
                """
                INSERT INTO subagents(id, task_id, type, status, data_json, created_at, updated_at)
                VALUES(?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    task_id=excluded.task_id,
                    type=excluded.type,
                    status=excluded.status,
                    data_json=excluded.data_json,
                    updated_at=excluded.updated_at
                """,
                (
                    record.id,
                    record.task_id,
                    record.type,
                    str(record.status),
                    self._json(data),
                    data["created_at"],
                    data["updated_at"],
                ),
            )
            self._conn.commit()

    def load_subagents(self) -> list[SubagentRecord]:
        with self._lock:
            rows = self._conn.execute("SELECT data_json FROM subagents ORDER BY created_at").fetchall()
        return [SubagentRecord.model_validate_json(row["data_json"]) for row in rows]

    def save_message(
        self,
        *,
        message_id: str,
        role: str,
        content: str,
        task_id: str | None = None,
        session_id: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        created_at = time.time()
        with self._lock:
            self._conn.execute(
                """
                INSERT INTO messages(id, task_id, session_id, role, content, metadata_json, created_at)
                VALUES(?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    task_id=excluded.task_id,
                    session_id=excluded.session_id,
                    role=excluded.role,
                    content=excluded.content,
                    metadata_json=excluded.metadata_json
                """,
                (message_id, task_id, session_id, role, content, self._json(metadata or {}), created_at),
            )
            self._conn.execute("DELETE FROM messages_fts WHERE id = ?", (message_id,))
            self._conn.execute(
                "INSERT INTO messages_fts(id, task_id, role, content) VALUES(?, ?, ?, ?)",
                (message_id, task_id, role, content),
            )
            self._conn.commit()

    def save_tool_call(
        self,
        *,
        call_id: str,
        tool_name: str,
        payload: dict[str, Any],
        ok: bool,
        result: Any = None,
        error: str | None = None,
        task_id: str | None = None,
        subagent_id: str | None = None,
        checkpoint_id: str | None = None,
    ) -> None:
        now = time.time()
        with self._lock:
            self._conn.execute(
                """
                INSERT INTO tool_calls(
                    id, task_id, subagent_id, tool_name, payload_json, result_json,
                    ok, error, checkpoint_id, created_at, finished_at
                )
                VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    result_json=excluded.result_json,
                    ok=excluded.ok,
                    error=excluded.error,
                    checkpoint_id=excluded.checkpoint_id,
                    finished_at=excluded.finished_at
                """,
                (
                    call_id,
                    task_id,
                    subagent_id,
                    tool_name,
                    self._json(payload),
                    self._json(result),
                    1 if ok else 0,
                    error,
                    checkpoint_id,
                    now,
                    now,
                ),
            )
            self._conn.commit()

    def save_memory(self, item: MemoryItem) -> None:
        data = item.model_dump(mode="json")
        with self._lock:
            self._conn.execute(
                """
                INSERT INTO memory_items(id, type, content, source, importance, data_json, created_at, updated_at)
                VALUES(?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    type=excluded.type,
                    content=excluded.content,
                    source=excluded.source,
                    importance=excluded.importance,
                    data_json=excluded.data_json,
                    updated_at=excluded.updated_at
                """,
                (
                    item.id,
                    item.type,
                    item.content,
                    item.source,
                    item.importance,
                    self._json(data),
                    data["created_at"],
                    data["updated_at"],
                ),
            )
            self._conn.execute("DELETE FROM memory_fts WHERE id = ?", (item.id,))
            self._conn.execute(
                "INSERT INTO memory_fts(id, type, content) VALUES(?, ?, ?)",
                (item.id, item.type, item.content),
            )
            self._conn.commit()

    def delete_memory(self, memory_id: str) -> None:
        with self._lock:
            self._conn.execute("DELETE FROM memory_items WHERE id = ?", (memory_id,))
            self._conn.execute("DELETE FROM memory_fts WHERE id = ?", (memory_id,))
            self._conn.commit()

    def load_memory(self) -> list[MemoryItem]:
        with self._lock:
            rows = self._conn.execute("SELECT data_json FROM memory_items ORDER BY created_at").fetchall()
        return [MemoryItem.model_validate_json(row["data_json"]) for row in rows]

    def search_all(self, query: str, limit: int = 20) -> dict[str, list[dict[str, Any]]]:
        pattern = query.strip()
        if not pattern:
            return {"tasks": [], "messages": [], "memory": []}
        with self._lock:
            tasks = self._conn.execute(
                "SELECT id, status, message FROM tasks_fts WHERE tasks_fts MATCH ? LIMIT ?",
                (pattern, limit),
            ).fetchall()
            messages = self._conn.execute(
                "SELECT id, task_id, role, content FROM messages_fts WHERE messages_fts MATCH ? LIMIT ?",
                (pattern, limit),
            ).fetchall()
            memory = self._conn.execute(
                "SELECT id, type, content FROM memory_fts WHERE memory_fts MATCH ? LIMIT ?",
                (pattern, limit),
            ).fetchall()
        return {
            "tasks": [dict(row) for row in tasks],
            "messages": [dict(row) for row in messages],
            "memory": [dict(row) for row in memory],
        }

    def save_learning_proposal(self, proposal: Any) -> None:
        data = proposal.model_dump(mode="json") if hasattr(proposal, "model_dump") else proposal
        with self._lock:
            self._conn.execute(
                """
                INSERT INTO learning_proposals(id, task_id, status, data_json, created_at, updated_at)
                VALUES(?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    task_id=excluded.task_id,
                    status=excluded.status,
                    data_json=excluded.data_json,
                    updated_at=excluded.updated_at
                """,
                (
                    data["id"],
                    data["task_id"],
                    data["status"],
                    self._json(data),
                    data["created_at"],
                    data["updated_at"],
                ),
            )
            self._conn.commit()

    def get_learning_proposal(self, proposal_id: str) -> dict[str, Any] | None:
        with self._lock:
            row = self._conn.execute(
                "SELECT data_json FROM learning_proposals WHERE id = ?",
                (proposal_id,),
            ).fetchone()
        return json.loads(row["data_json"]) if row else None

    def list_learning_proposals(self, status: str | None = None) -> list[dict[str, Any]]:
        with self._lock:
            if status:
                rows = self._conn.execute(
                    "SELECT data_json FROM learning_proposals WHERE status = ? ORDER BY updated_at DESC",
                    (status,),
                ).fetchall()
            else:
                rows = self._conn.execute(
                    "SELECT data_json FROM learning_proposals ORDER BY updated_at DESC",
                ).fetchall()
        return [json.loads(row["data_json"]) for row in rows]

    def execute(self, sql: str, params: tuple[Any, ...] = ()) -> list[sqlite3.Row]:
        with self._lock:
            rows = self._conn.execute(sql, params).fetchall()
            self._conn.commit()
        return rows
