from __future__ import annotations

from pydantic import BaseModel


class MemoryPolicy(BaseModel):
    save_user_messages: bool = True
    ttl_seconds: int | None = None
    min_importance: float = 0.0
    privacy_default: str = "internal"
    deduplicate: bool = True

