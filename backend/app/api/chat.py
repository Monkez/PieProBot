from __future__ import annotations

import asyncio
import json
import re
from pathlib import Path
from typing import Any
from uuid import uuid4

from fastapi import APIRouter, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import StreamingResponse

from app.core.task_model import ChatRequest, ChatResponse

router = APIRouter(prefix="/api/chat", tags=["chat"])


@router.post("", response_model=ChatResponse)
async def chat(request: Request, payload: ChatRequest) -> ChatResponse:
    return await request.app.state.orchestrator.submit_user_message(
        payload.message,
        payload.priority,
        payload.attachments,
    )


@router.post("/wait", response_model=ChatResponse)
async def chat_wait(request: Request, payload: ChatRequest) -> ChatResponse:
    return await request.app.state.orchestrator.submit_user_message_and_wait(
        payload.message,
        payload.priority,
        payload.attachments,
    )


@router.post("/upload", response_model=ChatResponse)
async def chat_upload(
    request: Request,
    message: str = Form(""),
    priority: int = Form(5),
    wait: bool = Form(True),
    files: list[UploadFile] = File(default=[]),
) -> ChatResponse:
    attachments = await _save_uploads(request, files)
    prepared = _message_with_attachments(message, attachments)
    if wait:
        return await request.app.state.orchestrator.submit_user_message_and_wait(prepared, priority, attachments)
    return await request.app.state.orchestrator.submit_user_message(prepared, priority, attachments)


@router.post("/stream")
async def chat_stream(request: Request, payload: ChatRequest) -> StreamingResponse:
    timeout_seconds = 120.0
    response = await request.app.state.orchestrator.submit_user_message(
        payload.message,
        payload.priority,
        payload.attachments,
    )

    async def events():
        yield _sse("accepted", {"type": "accepted", **response.model_dump(mode="json")})
        deadline = asyncio.get_running_loop().time() + timeout_seconds
        last_status: str | None = None
        while asyncio.get_running_loop().time() < deadline:
            task = request.app.state.orchestrator.tasks.get(response.task_id)
            if task:
                status = str(task.status)
                if status != last_status:
                    yield _sse(
                        "status",
                        {
                            "type": "status",
                            "task_id": task.id,
                            "status": status,
                            "response": task.result or task.error or "",
                        },
                    )
                    last_status = status
                if status in {"completed", "failed", "cancelled"}:
                    yield _sse(
                        "final",
                        {
                            "type": "final",
                            "task_id": task.id,
                            "status": status,
                            "response": task.result or task.error or "",
                            "attachments": _task_attachments(task.artifacts),
                        },
                    )
                    return
            else:
                yield _sse("status", {"type": "status", "task_id": response.task_id, "status": "pending", "response": ""})
                last_status = "pending"
            yield ": keep-alive\n\n"
            await asyncio.sleep(0.5)
        yield _sse(
            "timeout",
            {
                "type": "timeout",
                "task_id": response.task_id,
                "status": "running",
                "response": f"Task is still running after {timeout_seconds:g}s.",
            },
        )

    return StreamingResponse(events(), media_type="text/event-stream")


def _sse(event: str, payload: dict[str, Any]) -> str:
    return f"event: {event}\ndata: {json.dumps(payload, ensure_ascii=False)}\n\n"


def _task_attachments(artifacts: list[dict[str, Any]]) -> list[dict[str, Any]]:
    attachments: list[dict[str, Any]] = []
    for item in artifacts:
        if item.get("type") == "chat_attachments" and isinstance(item.get("items"), list):
            attachments.extend(entry for entry in item["items"] if isinstance(entry, dict))
        elif item.get("type") == "attachment" and isinstance(item.get("attachment"), dict):
            attachments.append(item["attachment"])
        elif "original_name" in item:
            attachments.append(item)
    return attachments


async def _save_uploads(request: Request, files: list[UploadFile]) -> list[dict[str, Any]]:
    if len(files) > 8:
        raise HTTPException(status_code=400, detail="At most 8 attachments are allowed")
    upload_root = Path(request.app.state.root) / "runtime" / "uploads" / uuid4().hex[:12]
    upload_root.mkdir(parents=True, exist_ok=True)
    attachments: list[dict[str, Any]] = []
    for upload in files:
        if not upload.filename:
            continue
        content = await upload.read()
        if len(content) > 25 * 1024 * 1024:
            raise HTTPException(status_code=400, detail=f"Attachment too large: {upload.filename}")
        original_name = Path(upload.filename).name
        safe_name = _safe_filename(original_name)
        stored_name = f"{uuid4().hex[:8]}-{safe_name}"
        target = upload_root / stored_name
        target.write_bytes(content)
        content_type = upload.content_type or "application/octet-stream"
        attachments.append(
            {
                "id": f"att_{uuid4().hex[:12]}",
                "original_name": original_name,
                "stored_name": stored_name,
                "path": str(target),
                "content_type": content_type,
                "size": len(content),
                "kind": _attachment_kind(content_type, original_name),
            }
        )
    return attachments


def _safe_filename(name: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9._-]+", "-", name).strip(".-")
    return cleaned[:80] or "attachment"


def _attachment_kind(content_type: str, name: str) -> str:
    lowered = content_type.lower()
    suffix = Path(name).suffix.lower()
    if lowered.startswith("image/") or suffix in {".png", ".jpg", ".jpeg", ".gif", ".webp"}:
        return "image"
    if lowered.startswith("audio/") or suffix in {".wav", ".mp3", ".m4a", ".webm", ".ogg"}:
        return "voice"
    return "file"


def _message_with_attachments(message: str, attachments: list[dict[str, Any]]) -> str:
    base = message.strip() or "Analyze the attached files."
    if not attachments:
        return base
    lines = ["", "Attached files:"]
    for item in attachments:
        lines.append(
            f"- {item['original_name']} ({item['kind']}, {item['content_type']}, {item['size']} bytes) at {item['path']}"
        )
    return base + "\n" + "\n".join(lines)
