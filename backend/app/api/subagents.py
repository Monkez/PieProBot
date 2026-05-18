from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request

router = APIRouter(prefix="/api/subagents", tags=["subagents"])


@router.get("")
async def list_subagents(request: Request):
    return [record.model_dump(mode="json") for record in request.app.state.subagents.list()]


@router.get("/{subagent_id}")
async def get_subagent(request: Request, subagent_id: str):
    try:
        return request.app.state.subagents.get(subagent_id).model_dump(mode="json")
    except KeyError:
        raise HTTPException(status_code=404, detail="Subagent not found") from None


@router.post("/{subagent_id}/kill")
async def kill_subagent(request: Request, subagent_id: str):
    return (await request.app.state.subagents.kill(subagent_id)).model_dump(mode="json")

