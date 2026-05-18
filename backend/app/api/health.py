from __future__ import annotations

from fastapi import APIRouter, Request

router = APIRouter(tags=["health"])


@router.get("/health")
async def health():
    return {"status": "ok", "service": "PiePro"}


@router.get("/ready")
async def ready(request: Request):
    return {
        "status": "ready",
        "tools": len(request.app.state.tools.definitions),
        "providers": await request.app.state.providers.status(),
    }


@router.get("/metrics")
async def metrics(request: Request):
    return request.app.state.metrics.collect()
