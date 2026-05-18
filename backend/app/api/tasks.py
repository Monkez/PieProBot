from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

router = APIRouter(prefix="/api/tasks", tags=["tasks"])


class TaskCreateRequest(BaseModel):
    message: str
    priority: int = 5


@router.post("")
async def create_task(request: Request, payload: TaskCreateRequest):
    return await request.app.state.orchestrator.submit_user_message(payload.message, payload.priority)


@router.get("")
async def list_tasks(request: Request):
    return [task.model_dump(mode="json") for task in request.app.state.orchestrator.tasks.values()]


@router.get("/{task_id}")
async def get_task(request: Request, task_id: str):
    task = request.app.state.orchestrator.tasks.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task.model_dump(mode="json")


@router.post("/{task_id}/cancel")
async def cancel_task(request: Request, task_id: str):
    return (await request.app.state.orchestrator.cancel_task(task_id)).model_dump(mode="json")


@router.post("/{task_id}/pause")
async def pause_task(request: Request, task_id: str):
    return (await request.app.state.orchestrator.pause_task(task_id)).model_dump(mode="json")


@router.post("/{task_id}/resume")
async def resume_task(request: Request, task_id: str):
    return (await request.app.state.orchestrator.resume_task(task_id)).model_dump(mode="json")


@router.post("/{task_id}/retry")
async def retry_task(request: Request, task_id: str):
    return (await request.app.state.orchestrator.retry_task(task_id)).model_dump(mode="json")

