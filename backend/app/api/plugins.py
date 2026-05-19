from __future__ import annotations

from fastapi import APIRouter, Request

router = APIRouter(prefix="/api/plugins", tags=["plugins"])


@router.get("")
async def list_plugins(request: Request):
    return request.app.state.plugins.loaded
