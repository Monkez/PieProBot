from __future__ import annotations

import asyncio
from typing import Any, Awaitable, Callable

from app.observability.logging import get_logger
from app.tools.permissions import ToolPermissionManager
from app.tools.schemas import ToolDefinition, ToolResult

Handler = Callable[[dict[str, Any]], Awaitable[Any]]


class ToolExecutor:
    def __init__(self, permission_manager: ToolPermissionManager | None = None) -> None:
        self._handlers: dict[str, Handler] = {}
        self._permissions = permission_manager or ToolPermissionManager()
        self._logger = get_logger("tools")

    def register_handler(self, name: str, handler: Handler) -> None:
        self._handlers[name] = handler

    async def execute(
        self,
        definition: ToolDefinition,
        payload: dict[str, Any],
        granted_permissions: dict[str, bool] | None = None,
    ) -> ToolResult:
        try:
            self._permissions.assert_allowed(definition, granted_permissions)
            handler = self._handlers[definition.name]
            output = await asyncio.wait_for(handler(payload), timeout=definition.timeout_seconds)
            return ToolResult(ok=True, output=output)
        except Exception as exc:
            self._logger.warning("tool execution failed: %s", exc, extra={"tool_call_id": definition.name})
            return ToolResult(ok=False, error=str(exc))

