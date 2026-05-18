from __future__ import annotations

from fastapi import APIRouter, Request
from pydantic import BaseModel

from app.memory.manager import MemoryItem

router = APIRouter(prefix="/api/memory", tags=["memory"])


class MemoryCreateRequest(BaseModel):
    content: str
    type: str = "note"
    metadata: dict[str, object] = {}
    importance: float = 0.5
    privacy_level: str = "internal"


@router.get("/search")
async def search_memory(request: Request, q: str = "", limit: int = 20):
    items = await request.app.state.memory.search(q, limit)
    return [item.model_dump(mode="json") for item in items]


@router.post("")
async def create_memory(request: Request, payload: MemoryCreateRequest):
    item = MemoryItem(
        type=payload.type,
        content=payload.content,
        metadata=payload.metadata,
        importance=payload.importance,
        privacy_level=payload.privacy_level,
        source="api",
    )
    return (await request.app.state.memory.save(item)).model_dump(mode="json")


@router.delete("/{memory_id}")
async def delete_memory(request: Request, memory_id: str):
    return {"ok": await request.app.state.memory.delete(memory_id)}


@router.post("/compact")
async def compact_memory(request: Request):
    return await request.app.state.memory.compact()


@router.get("/status")
async def memory_status(request: Request):
    return await request.app.state.memory.status()
