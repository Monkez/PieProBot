from __future__ import annotations

from fastapi import APIRouter, Request
from pydantic import BaseModel

router = APIRouter(prefix="/api/providers", tags=["providers"])


class ProviderTestRequest(BaseModel):
    message: str = "health check"
    provider: str | None = None


@router.get("")
async def list_providers(request: Request):
    return await request.app.state.providers.status()


@router.get("/status")
async def provider_status(request: Request):
    return await request.app.state.providers.status()


@router.post("/test")
async def test_provider(request: Request, payload: ProviderTestRequest):
    messages = [{"role": "user", "content": payload.message}]
    response = await request.app.state.providers.chat_with_provider(payload.provider, messages) if payload.provider else await request.app.state.providers.chat(messages)
    return response.model_dump()
