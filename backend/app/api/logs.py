from __future__ import annotations

from fastapi import APIRouter

from app.observability.logging import query_logs

router = APIRouter(prefix="/logs", tags=["logs"])


@router.get("")
async def logs(
    limit: int = 200,
    level: str | None = None,
    logger: str | None = None,
    correlation_id: str | None = None,
):
    return {
        "logs": query_logs(limit=limit, level=level, logger=logger, correlation_id=correlation_id),
        "message": "Structured logs are emitted to stdout and retained in an in-memory ring buffer.",
    }


@router.get("/tasks/{task_id}")
async def task_logs(task_id: str, limit: int = 200):
    return {"task_id": task_id, "logs": query_logs(task_id=task_id, limit=limit)}


@router.get("/subagents/{subagent_id}")
async def subagent_logs(subagent_id: str, limit: int = 200):
    return {"subagent_id": subagent_id, "logs": query_logs(subagent_id=subagent_id, limit=limit)}
