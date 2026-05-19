from __future__ import annotations

from fastapi import APIRouter, Request

router = APIRouter(prefix="/api/state", tags=["state"])


@router.get("/search")
async def search_state(request: Request, q: str, limit: int = 20):
    return request.app.state.state_store.search_all(q, limit)
