from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class ConfigDocument(BaseModel):
    version: int = 1
    data: dict[str, Any] = Field(default_factory=dict)


class ConfigValidationResult(BaseModel):
    ok: bool
    path: str | None = None
    errors: list[str] = Field(default_factory=list)

