from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

router = APIRouter(prefix="/api/schedules", tags=["schedules"])


class ScheduleCreateRequest(BaseModel):
    name: str
    prompt: str
    every_seconds: int | None = None
    run_at: float | None = None


@router.get("")
async def list_schedules(request: Request):
    return [item.__dict__ for item in request.app.state.scheduler.list()]


@router.post("")
async def create_schedule(request: Request, payload: ScheduleCreateRequest):
    item = request.app.state.scheduler.create(
        name=payload.name,
        prompt=payload.prompt,
        every_seconds=payload.every_seconds,
        run_at=payload.run_at,
    )
    return item.__dict__


@router.post("/{schedule_id}/pause")
async def pause_schedule(request: Request, schedule_id: str):
    item = request.app.state.scheduler.pause(schedule_id)
    if not item:
        raise HTTPException(status_code=404, detail="Schedule not found")
    return item.__dict__


@router.post("/{schedule_id}/resume")
async def resume_schedule(request: Request, schedule_id: str):
    item = request.app.state.scheduler.resume(schedule_id)
    if not item:
        raise HTTPException(status_code=404, detail="Schedule not found")
    return item.__dict__


@router.post("/tick")
async def tick_schedules(request: Request):
    return {"ran": await request.app.state.scheduler.tick()}
