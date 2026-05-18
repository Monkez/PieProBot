from __future__ import annotations

import asyncio
import json

from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse

from app.core.task_model import ChatRequest, ChatResponse

router = APIRouter(prefix="/api/chat", tags=["chat"])


@router.post("", response_model=ChatResponse)
async def chat(request: Request, payload: ChatRequest) -> ChatResponse:
    return await request.app.state.orchestrator.submit_user_message(payload.message, payload.priority)


@router.post("/wait", response_model=ChatResponse)
async def chat_wait(request: Request, payload: ChatRequest) -> ChatResponse:
    return await request.app.state.orchestrator.submit_user_message_and_wait(payload.message, payload.priority)


@router.post("/stream")
async def chat_stream(request: Request, payload: ChatRequest) -> StreamingResponse:
    response = await request.app.state.orchestrator.submit_user_message(payload.message, payload.priority)

    async def events():
        yield f"data: {json.dumps(response.model_dump(mode='json'))}\n\n"
        for _ in range(20):
            task = request.app.state.orchestrator.tasks.get(response.task_id)
            if task and task.status in {"completed", "failed", "cancelled"}:
                yield f"data: {json.dumps(task.model_dump(mode='json'))}\n\n"
                return
            await asyncio.sleep(0.1)
        yield f"data: {json.dumps({'task_id': response.task_id, 'status': 'running'})}\n\n"

    return StreamingResponse(events(), media_type="text/event-stream")

