from __future__ import annotations

import asyncio
from collections import defaultdict
from typing import Any


class EventBus:
    """In-process pub/sub for realtime UI and tests."""

    def __init__(self) -> None:
        self._queues: dict[str, list[asyncio.Queue[dict[str, Any]]]] = defaultdict(list)

    async def publish(self, topic: str, event: dict[str, Any]) -> None:
        for queue in list(self._queues[topic]):
            await queue.put(event)

    async def subscribe(self, topic: str) -> asyncio.Queue[dict[str, Any]]:
        queue: asyncio.Queue[dict[str, Any]] = asyncio.Queue()
        self._queues[topic].append(queue)
        return queue

    def unsubscribe(self, topic: str, queue: asyncio.Queue[dict[str, Any]]) -> None:
        if queue in self._queues[topic]:
            self._queues[topic].remove(queue)

