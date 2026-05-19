from __future__ import annotations

from fastapi import APIRouter, Request

router = APIRouter(prefix="/api/checkpoints", tags=["checkpoints"])


@router.post("/{checkpoint_id}/rollback")
async def rollback_checkpoint(request: Request, checkpoint_id: str):
    return request.app.state.checkpoints.rollback(checkpoint_id)
