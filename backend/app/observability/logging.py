from __future__ import annotations

import json
import logging
import re
from collections import deque
from contextvars import ContextVar
from datetime import datetime, timezone
from typing import Any

SECRET_PATTERNS = [
    re.compile(r"(api[_-]?key|token|secret|password)=([^&\s]+)", re.IGNORECASE),
    re.compile(r"(sk-[A-Za-z0-9_\-]{12,})"),
]

LOG_RECORDS: deque[dict[str, Any]] = deque(maxlen=5_000)
CORRELATION_ID: ContextVar[str | None] = ContextVar("correlation_id", default=None)
TASK_ID: ContextVar[str | None] = ContextVar("task_id", default=None)
SUBAGENT_ID: ContextVar[str | None] = ContextVar("subagent_id", default=None)


def sanitize(value: Any) -> Any:
    text = str(value)
    for pattern in SECRET_PATTERNS:
        text = pattern.sub(lambda m: f"{m.group(1)}=***" if len(m.groups()) > 1 else "***", text)
    return text


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        return json.dumps(build_log_payload(record, self), ensure_ascii=False)


def build_log_payload(record: logging.LogRecord, formatter: logging.Formatter | None = None) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "level": record.levelname,
        "logger": record.name,
        "message": sanitize(record.getMessage()),
    }
    context_defaults = {
        "correlation_id": CORRELATION_ID.get(),
        "task_id": TASK_ID.get(),
        "subagent_id": SUBAGENT_ID.get(),
    }
    for field in ["correlation_id", "task_id", "subagent_id", "tool_call_id", "provider_call_id", "trace_id"]:
        value = getattr(record, field, context_defaults.get(field))
        if value:
            payload[field] = sanitize(value)
    if record.exc_info:
        fmt = formatter or logging.Formatter()
        payload["error"] = sanitize(fmt.formatException(record.exc_info))
    return payload


class LogCaptureHandler(logging.Handler):
    def emit(self, record: logging.LogRecord) -> None:
        LOG_RECORDS.append(build_log_payload(record))


def configure_logging(level: str = "INFO") -> None:
    handler = logging.StreamHandler()
    handler.setFormatter(JsonFormatter())
    capture = LogCaptureHandler()
    logging.basicConfig(level=getattr(logging, level.upper(), logging.INFO), handlers=[handler, capture], force=True)


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)


def set_request_context(correlation_id: str, task_id: str | None = None, subagent_id: str | None = None) -> None:
    CORRELATION_ID.set(correlation_id)
    TASK_ID.set(task_id)
    SUBAGENT_ID.set(subagent_id)


def query_logs(
    *,
    limit: int = 200,
    level: str | None = None,
    logger: str | None = None,
    correlation_id: str | None = None,
    task_id: str | None = None,
    subagent_id: str | None = None,
) -> list[dict[str, Any]]:
    rows = list(LOG_RECORDS)
    if level:
        rows = [row for row in rows if row.get("level") == level.upper()]
    if logger:
        rows = [row for row in rows if str(row.get("logger", "")).startswith(logger)]
    if correlation_id:
        rows = [row for row in rows if row.get("correlation_id") == correlation_id]
    if task_id:
        rows = [row for row in rows if row.get("task_id") == task_id]
    if subagent_id:
        rows = [row for row in rows if row.get("subagent_id") == subagent_id]
    return rows[-limit:]
