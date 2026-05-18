from __future__ import annotations

from typing import Any


async def execute(payload: dict[str, Any]) -> dict[str, Any]:
    return {"echo": payload.get("text") or payload.get("message") or payload}

