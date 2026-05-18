from __future__ import annotations

from app.memory.manager import MemoryManager


class MemoryCompactor:
    def __init__(self, manager: MemoryManager) -> None:
        self.manager = manager

    async def run(self) -> dict[str, int]:
        return await self.manager.compact()

