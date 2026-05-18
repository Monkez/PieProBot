from __future__ import annotations

from app.tools.schemas import ToolDefinition


class ToolPermissionError(PermissionError):
    pass


class ToolPermissionManager:
    def assert_allowed(self, definition: ToolDefinition, granted: dict[str, bool] | None = None) -> None:
        if not definition.enabled:
            raise ToolPermissionError(f"Tool {definition.name} is disabled")
        granted = granted or {}
        for permission, required in definition.permissions.items():
            if required and not granted.get(permission, False):
                raise ToolPermissionError(f"Tool {definition.name} requires permission '{permission}'")

