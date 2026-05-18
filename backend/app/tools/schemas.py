from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class RetryPolicy(BaseModel):
    max_retries: int = 0
    backoff: str = "none"


class ToolDefinition(BaseModel):
    name: str
    version: str | int = "1.0.0"
    description: str = ""
    category: str = "general"
    enabled: bool = True
    input_schema: dict[str, Any] = Field(default_factory=lambda: {"type": "object"})
    output_schema: dict[str, Any] = Field(default_factory=lambda: {"type": "object"})
    handler: str | None = None
    timeout_seconds: float = 10
    retry_policy: RetryPolicy = Field(default_factory=RetryPolicy)
    permissions: dict[str, bool] = Field(default_factory=dict)
    sandbox_policy: dict[str, Any] = Field(default_factory=dict)
    rate_limit: dict[str, Any] = Field(default_factory=dict)
    audit_level: str = "standard"


class ToolResult(BaseModel):
    ok: bool
    output: Any = None
    error: str | None = None
