from __future__ import annotations

import os

from fastapi import Header, HTTPException, Request


PUBLIC_PATHS = {"/health"}
PROTECTED_PREFIXES = ("/api", "/ready", "/metrics", "/logs")


def is_protected_path(path: str) -> bool:
    if path in PUBLIC_PATHS:
        return False
    return path.startswith(PROTECTED_PREFIXES)


async def authenticate_request(request: Request) -> str:
    if request.method == "OPTIONS":
        return "public"
    if not is_protected_path(request.url.path):
        return "public"
    expected = os.getenv("ADMIN_API_KEY")
    if not expected:
        return "admin"
    supplied = request.headers.get("x-api-key")
    if supplied != expected:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return "admin"


async def require_api_key(x_api_key: str | None = Header(default=None)) -> str:
    expected = os.getenv("ADMIN_API_KEY")
    if not expected:
        return "admin"
    if x_api_key != expected:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return "admin"
