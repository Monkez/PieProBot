from __future__ import annotations


class VectorMemory:
    """Placeholder vector API ready for Qdrant/pgvector adapters."""

    async def upsert(self, key: str, vector: list[float], payload: dict[str, object]) -> None:
        return None

    async def search(self, vector: list[float], limit: int = 10) -> list[dict[str, object]]:
        return []

