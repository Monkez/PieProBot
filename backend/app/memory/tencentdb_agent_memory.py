from __future__ import annotations

from typing import Any

import httpx

from app.memory.manager import MemoryItem


class TencentDBAgentMemoryBackend:
    """HTTP adapter for Tencent/TencentDB-Agent-Memory standalone gateway.

    The upstream project exposes a host-neutral TDAI Gateway with:
    - GET /health
    - POST /capture
    - POST /search/memories
    - POST /search/conversations
    """

    def __init__(
        self,
        base_url: str = "http://127.0.0.1:8420",
        session_key: str = "piepro-default",
        timeout_seconds: float = 3.0,
        max_results: int = 5,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.session_key = session_key
        self.timeout_seconds = timeout_seconds
        self.max_results = max_results

    async def health(self) -> dict[str, Any]:
        async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
            response = await client.get(f"{self.base_url}/health")
            response.raise_for_status()
            return response.json()

    async def capture_turn(
        self,
        *,
        user_content: str,
        assistant_content: str,
        session_key: str | None = None,
        session_id: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        payload = {
            "user_content": user_content,
            "assistant_content": assistant_content,
            "session_key": session_key or self.session_key,
            "session_id": session_id,
            "messages": [
                {"role": "user", "content": user_content, "metadata": metadata or {}},
                {"role": "assistant", "content": assistant_content, "metadata": metadata or {}},
            ],
        }
        async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
            response = await client.post(f"{self.base_url}/capture", json=payload)
            response.raise_for_status()
            return response.json()

    async def search_memories(self, query: str, limit: int | None = None) -> list[MemoryItem]:
        payload = {"query": query, "limit": limit or self.max_results}
        async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
            response = await client.post(f"{self.base_url}/search/memories", json=payload)
            response.raise_for_status()
            data = response.json()
        text = str(data.get("results", ""))
        if not text:
            return []
        return [
            MemoryItem(
                type="tencentdb_memory",
                content=text,
                source="tencentdb-agent-memory",
                importance=0.8,
                metadata={
                    "backend": "tencentdb-agent-memory",
                    "total": data.get("total", 0),
                    "strategy": data.get("strategy"),
                    "base_url": self.base_url,
                },
            )
        ]

    async def search_conversations(self, query: str, limit: int | None = None) -> list[MemoryItem]:
        payload = {"query": query, "limit": limit or self.max_results, "session_key": self.session_key}
        async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
            response = await client.post(f"{self.base_url}/search/conversations", json=payload)
            response.raise_for_status()
            data = response.json()
        text = str(data.get("results", ""))
        if not text:
            return []
        return [
            MemoryItem(
                type="tencentdb_conversation",
                content=text,
                source="tencentdb-agent-memory",
                importance=0.7,
                metadata={
                    "backend": "tencentdb-agent-memory",
                    "total": data.get("total", 0),
                    "base_url": self.base_url,
                },
            )
        ]

