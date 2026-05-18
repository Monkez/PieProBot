from __future__ import annotations

from app.observability.logging import get_logger


class AuditLogger:
    def __init__(self) -> None:
        self.logger = get_logger("security")

    def record(self, action: str, actor: str = "system", **fields: object) -> None:
        self.logger.info("audit action=%s actor=%s fields=%s", action, actor, fields)

