from __future__ import annotations

import asyncio
import json
import time
from dataclasses import dataclass
from typing import Any
from uuid import uuid4


@dataclass
class ScheduledTask:
    id: str
    name: str
    prompt: str
    schedule: dict[str, Any]
    enabled: bool
    next_run_at: float | None
    last_run_at: float | None = None
    last_status: str | None = None
    last_error: str | None = None
    created_at: float = 0
    updated_at: float = 0


class ScheduledTaskManager:
    def __init__(self, state_store, orchestrator_getter, tick_seconds: float = 5.0) -> None:
        self.state_store = state_store
        self._orchestrator_getter = orchestrator_getter
        self.tick_seconds = tick_seconds
        self._runner: asyncio.Task[None] | None = None

    def start(self) -> None:
        if self._runner is None or self._runner.done():
            self._runner = asyncio.create_task(self._loop())

    async def stop(self) -> None:
        if self._runner and not self._runner.done():
            self._runner.cancel()
            try:
                await self._runner
            except asyncio.CancelledError:
                pass

    def create(self, *, name: str, prompt: str, every_seconds: int | None = None, run_at: float | None = None) -> ScheduledTask:
        if every_seconds is None and run_at is None:
            raise ValueError("Provide every_seconds or run_at")
        now = time.time()
        schedule = {"kind": "interval", "every_seconds": every_seconds} if every_seconds else {"kind": "once", "run_at": run_at}
        item = ScheduledTask(
            id=f"sched_{uuid4().hex[:12]}",
            name=name,
            prompt=prompt,
            schedule=schedule,
            enabled=True,
            next_run_at=now + every_seconds if every_seconds else run_at,
            created_at=now,
            updated_at=now,
        )
        self._save(item)
        return item

    def list(self) -> list[ScheduledTask]:
        rows = self.state_store.execute("SELECT * FROM scheduled_tasks ORDER BY created_at DESC")
        return [self._from_row(row) for row in rows]

    def pause(self, task_id: str) -> ScheduledTask | None:
        self.state_store.execute(
            "UPDATE scheduled_tasks SET enabled=0, updated_at=? WHERE id=?",
            (time.time(), task_id),
        )
        return self.get(task_id)

    def resume(self, task_id: str) -> ScheduledTask | None:
        item = self.get(task_id)
        if not item:
            return None
        item.enabled = True
        item.next_run_at = self._next_run(item, time.time())
        item.updated_at = time.time()
        self._save(item)
        return item

    def get(self, task_id: str) -> ScheduledTask | None:
        rows = self.state_store.execute("SELECT * FROM scheduled_tasks WHERE id=?", (task_id,))
        return self._from_row(rows[0]) if rows else None

    async def _loop(self) -> None:
        while True:
            await asyncio.sleep(self.tick_seconds)
            await self.tick()

    async def tick(self) -> int:
        now = time.time()
        rows = self.state_store.execute(
            "SELECT * FROM scheduled_tasks WHERE enabled=1 AND next_run_at IS NOT NULL AND next_run_at <= ?",
            (now,),
        )
        count = 0
        for row in rows:
            item = self._from_row(row)
            try:
                await self._orchestrator_getter().submit_user_message(item.prompt)
                item.last_status = "submitted"
                item.last_error = None
            except Exception as exc:
                item.last_status = "error"
                item.last_error = str(exc)
            item.last_run_at = now
            item.next_run_at = self._next_run(item, now)
            if item.schedule.get("kind") == "once":
                item.enabled = False
            item.updated_at = time.time()
            self._save(item)
            count += 1
        return count

    def _next_run(self, item: ScheduledTask, now: float) -> float | None:
        if item.schedule.get("kind") == "interval":
            return now + int(item.schedule.get("every_seconds", 60))
        return None

    def _save(self, item: ScheduledTask) -> None:
        self.state_store.execute(
            """
            INSERT INTO scheduled_tasks(
                id, name, prompt, schedule_json, enabled, next_run_at, last_run_at,
                last_status, last_error, created_at, updated_at
            )
            VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                name=excluded.name,
                prompt=excluded.prompt,
                schedule_json=excluded.schedule_json,
                enabled=excluded.enabled,
                next_run_at=excluded.next_run_at,
                last_run_at=excluded.last_run_at,
                last_status=excluded.last_status,
                last_error=excluded.last_error,
                updated_at=excluded.updated_at
            """,
            (
                item.id,
                item.name,
                item.prompt,
                json.dumps(item.schedule),
                1 if item.enabled else 0,
                item.next_run_at,
                item.last_run_at,
                item.last_status,
                item.last_error,
                item.created_at,
                item.updated_at,
            ),
        )

    @staticmethod
    def _from_row(row) -> ScheduledTask:
        return ScheduledTask(
            id=row["id"],
            name=row["name"],
            prompt=row["prompt"],
            schedule=json.loads(row["schedule_json"]),
            enabled=bool(row["enabled"]),
            next_run_at=row["next_run_at"],
            last_run_at=row["last_run_at"],
            last_status=row["last_status"],
            last_error=row["last_error"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )
