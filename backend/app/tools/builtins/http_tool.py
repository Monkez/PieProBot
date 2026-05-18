from __future__ import annotations

from typing import Any

import httpx


async def execute(payload: dict[str, Any]) -> dict[str, Any]:
    method = str(payload.get("method", "GET")).upper()
    url = str(payload["url"])
    async with httpx.AsyncClient(timeout=payload.get("timeout", 10)) as client:
        response = await client.request(method, url, json=payload.get("json"))
    return {"status_code": response.status_code, "text": response.text[:20_000]}

