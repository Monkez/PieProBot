from __future__ import annotations

import os

from fastapi import Header, HTTPException


async def require_api_key(x_api_key: str | None = Header(default=None)) -> str:
    expected = os.getenv("ADMIN_API_KEY")
    if not expected:
        return "admin"
    if x_api_key != expected:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return "admin"

