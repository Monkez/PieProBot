from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field

from app.memory.policy import MemoryPolicy
from app.observability.logging import get_logger


class MemoryItem(BaseModel):
    id: str = Field(default_factory=lambda: f"mem_{uuid4().hex[:12]}")
    type: str = "note"
    content: str
    metadata: dict[str, Any] = Field(default_factory=dict)
    source: str = "system"
    importance: float = 0.5
    privacy_level: str = "internal"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    expires_at: datetime | None = None
    embedding_id: str | None = None


class MemoryManager:
    def __init__(self, policy: MemoryPolicy | None = None, external_backend: Any | None = None, state_store: Any | None = None) -> None:
        self.policy = policy or MemoryPolicy()
        self.external_backend = external_backend
        self.state_store = state_store
        self._items: dict[str, MemoryItem] = {}
        self.logger = get_logger("memory")
        if self.state_store:
            try:
                self._items = {item.id: item for item in self.state_store.load_memory()}
            except Exception as exc:
                self.logger.warning("memory restore failed: %s", exc)

    async def save(self, item: MemoryItem) -> MemoryItem:
        if "secret" in item.privacy_level.lower():
            raise ValueError("Secret memory is not allowed")
        if self.policy.deduplicate:
            for existing in self._items.values():
                if existing.content == item.content and existing.type == item.type:
                    return existing
        self._items[item.id] = item
        self._persist(item)
        return item

    async def retrieve(self, memory_id: str) -> MemoryItem | None:
        return self._items.get(memory_id)

    async def search(self, query: str, limit: int = 20) -> list[MemoryItem]:
        q = query.lower()
        results = [item for item in self._items.values() if q in item.content.lower() or q in str(item.metadata).lower()]
        local_results = sorted(results, key=lambda item: item.importance, reverse=True)[:limit]
        if not self.external_backend:
            return local_results
        try:
            external = await self.external_backend.search_memories(query, limit)
            if not external:
                external = await self.external_backend.search_conversations(query, limit)
            return [*external, *local_results][:limit]
        except Exception as exc:
            self.logger.warning("external memory search failed, using local fallback: %s", exc)
            return local_results

    async def update(self, memory_id: str, patch: dict[str, Any]) -> MemoryItem:
        item = self._items[memory_id].model_copy(update=patch)
        item.updated_at = datetime.now(timezone.utc)
        self._items[memory_id] = item
        self._persist(item)
        return item

    async def delete(self, memory_id: str) -> bool:
        deleted = self._items.pop(memory_id, None) is not None
        if deleted and self.state_store:
            try:
                self.state_store.delete_memory(memory_id)
            except Exception as exc:
                self.logger.warning("memory delete persistence failed: %s", exc)
        return deleted

    async def summarize(self, scope: str = "all") -> str:
        items = list(self._items.values())
        return f"{len(items)} memory items stored for scope={scope}."

    async def compact(self, scope: str = "all") -> dict[str, int]:
        before = len(self._items)
        seen: set[tuple[str, str]] = set()
        compacted: dict[str, MemoryItem] = {}
        for item in self._items.values():
            key = (item.type, item.content)
            if key not in seen:
                seen.add(key)
                compacted[item.id] = item
        self._items = compacted
        for item in self._items.values():
            self._persist(item)
        return {"before": before, "after": len(self._items)}

    async def capture_turn(
        self,
        *,
        user_content: str,
        assistant_content: str,
        session_key: str | None = None,
        session_id: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        await self.save(
            MemoryItem(
                type="conversation_turn",
                content=f"User: {user_content}\nAssistant: {assistant_content}",
                source=session_id or "conversation",
                importance=0.6,
                metadata=metadata or {},
            )
        )
        if not self.external_backend:
            return {"external": False, "captured": "local"}
        try:
            result = await self.external_backend.capture_turn(
                user_content=user_content,
                assistant_content=assistant_content,
                session_key=session_key,
                session_id=session_id,
                metadata=metadata,
            )
            return {"external": True, "captured": "tencentdb-agent-memory", "result": result}
        except Exception as exc:
            self.logger.warning("external memory capture failed, local capture kept: %s", exc)
            return {"external": False, "captured": "local", "error": str(exc)}

    async def status(self) -> dict[str, Any]:
        status: dict[str, Any] = {
            "local_items": len(self._items),
            "external_enabled": self.external_backend is not None,
            "external_healthy": False,
        }
        if self.external_backend:
            status["external_base_url"] = self.external_backend.base_url
            try:
                status["external_health"] = await self.external_backend.health()
                status["external_healthy"] = True
            except Exception as exc:
                status["external_error"] = str(exc)
        return status

    def _persist(self, item: MemoryItem) -> None:
        if not self.state_store:
            return
        try:
            self.state_store.save_memory(item)
        except Exception as exc:
            self.logger.warning("memory persistence failed: %s", exc)
