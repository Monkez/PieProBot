from __future__ import annotations

from fastapi import APIRouter, Request
from pydantic import BaseModel

router = APIRouter(prefix="/api/providers", tags=["providers"])


class ProviderTestRequest(BaseModel):
    message: str = "health check"


@router.get("")
async def list_providers(request: Request):
    return await request.app.state.providers.status()


@router.get("/status")
async def provider_status(request: Request):
    return await request.app.state.providers.status()


@router.post("/test")
async def test_provider(request: Request, payload: ProviderTestRequest):
    response = await request.app.state.providers.chat([{"role": "user", "content": payload.message}])
    return response.model_dump()

