from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Request

from app.channels.base import ChannelMessage

router = APIRouter(prefix="/api/channels", tags=["channels"])


@router.get("")
async def list_channels(request: Request):
    return await request.app.state.channels.status()


@router.post("/{name}/send")
async def send_channel_message(request: Request, name: str, payload: ChannelMessage):
    return (await request.app.state.channels.send(name, payload)).model_dump()


@router.post("/telegram/webhook")
async def telegram_webhook(request: Request):
    update: dict[str, Any] = await request.json()
    message = update.get("message") or update.get("edited_message") or {}
    text = str(message.get("text") or "").strip()
    chat = message.get("chat") or {}
    if not text:
        return {"ok": True, "ignored": "empty message"}
    response = await request.app.state.orchestrator.submit_user_message(text)
    return {"ok": True, "chat_id": chat.get("id"), "task_id": response.task_id, "status": response.status}
