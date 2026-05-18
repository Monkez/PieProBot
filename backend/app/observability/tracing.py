from __future__ import annotations

from contextlib import asynccontextmanager
from time import perf_counter
from typing import AsyncIterator


@asynccontextmanager
async def span(name: str) -> AsyncIterator[dict[str, float | str]]:
    start = perf_counter()
    data: dict[str, float | str] = {"name": name}
    try:
        yield data
    finally:
        data["duration_ms"] = (perf_counter() - start) * 1000

