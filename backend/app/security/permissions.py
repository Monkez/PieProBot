from __future__ import annotations

from pydantic import BaseModel


class RolePermissions(BaseModel):
    role: str
    can_promote: bool = False
    can_execute_shell: bool = False
    can_edit_config: bool = False


DEFAULT_ROLES = {
    "admin": RolePermissions(role="admin", can_promote=True, can_execute_shell=True, can_edit_config=True),
    "operator": RolePermissions(role="operator", can_promote=False, can_execute_shell=False, can_edit_config=True),
    "viewer": RolePermissions(role="viewer"),
}

