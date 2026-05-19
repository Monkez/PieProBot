from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Any, Awaitable, Callable
from uuid import uuid4

from app.observability.logging import get_logger
from app.tools.checkpoint import CheckpointManager
from app.tools.permissions import ToolPermissionManager
from app.tools.schemas import ToolDefinition, ToolResult

Handler = Callable[[dict[str, Any]], Awaitable[Any]]


class ToolExecutor:
    def __init__(
        self,
        permission_manager: ToolPermissionManager | None = None,
        state_store=None,
        checkpoint_manager: CheckpointManager | None = None,
    ) -> None:
        self._handlers: dict[str, Handler] = {}
        self._permissions = permission_manager or ToolPermissionManager()
        self._logger = get_logger("tools")
        self._state_store = state_store
        self._checkpoint_manager = checkpoint_manager

    def register_handler(self, name: str, handler: Handler) -> None:
        self._handlers[name] = handler

    async def execute(
        self,
        definition: ToolDefinition,
        payload: dict[str, Any],
        granted_permissions: dict[str, bool] | None = None,
        task_id: str | None = None,
        subagent_id: str | None = None,
    ) -> ToolResult:
        call_id = f"tool_{uuid4().hex[:12]}"
        checkpoint_id: str | None = None
        try:
            self._permissions.assert_allowed(definition, granted_permissions)
            checkpoint_id = self._checkpoint_before_mutation(definition, payload)
            handler = self._handlers[definition.name]
            output = await asyncio.wait_for(handler(payload), timeout=definition.timeout_seconds)
            result = ToolResult(ok=True, output=output, checkpoint_id=checkpoint_id)
            self._save_tool_call(call_id, definition.name, payload, result, task_id, subagent_id)
            return result
        except Exception as exc:
            self._logger.warning("tool execution failed: %s", exc, extra={"tool_call_id": definition.name})
            result = ToolResult(ok=False, error=str(exc), checkpoint_id=checkpoint_id)
            self._save_tool_call(call_id, definition.name, payload, result, task_id, subagent_id)
            return result

    def _checkpoint_before_mutation(self, definition: ToolDefinition, payload: dict[str, Any]) -> str | None:
        if not self._checkpoint_manager:
            return None
        if definition.name == "filesystem" and payload.get("operation") == "write":
            workspace = Path(payload.get("workspace", ".")).resolve()
            return self._checkpoint_manager.snapshot_files(
                "filesystem.write",
                workspace,
                [(workspace / str(payload["path"])).resolve()],
            )
        if definition.name == "shell":
            raw_paths = payload.get("checkpoint_paths") or []
            if not raw_paths:
                return None
            workspace = Path(payload.get("workspace", ".")).resolve()
            paths = [(workspace / str(item)).resolve() for item in raw_paths]
            return self._checkpoint_manager.snapshot_files("shell", workspace, paths)
        return None

    def _save_tool_call(
        self,
        call_id: str,
        tool_name: str,
        payload: dict[str, Any],
        result: ToolResult,
        task_id: str | None,
        subagent_id: str | None,
    ) -> None:
        if not self._state_store:
            return
        try:
            self._state_store.save_tool_call(
                call_id=call_id,
                tool_name=tool_name,
                payload=payload,
                ok=result.ok,
                result=result.output,
                error=result.error,
                task_id=task_id,
                subagent_id=subagent_id,
                checkpoint_id=result.checkpoint_id,
            )
        except Exception as exc:
            self._logger.warning("tool call persistence failed: %s", exc)
