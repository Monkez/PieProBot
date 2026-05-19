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


def role_permissions(role: str | None) -> RolePermissions:
    return DEFAULT_ROLES.get(role or "viewer", DEFAULT_ROLES["viewer"])


def tool_permissions_for_role(role: str | None) -> dict[str, bool]:
    permissions = role_permissions(role)
    if permissions.role == "admin":
        return {
            "filesystem": True,
            "memory": True,
            "network": True,
            "self_update": True,
            "shell": permissions.can_execute_shell,
            "skills": True,
        }
    if permissions.role == "operator":
        return {
            "filesystem": permissions.can_edit_config,
            "memory": True,
            "network": True,
            "self_update": False,
            "shell": False,
            "skills": True,
        }
    return {
        "filesystem": False,
        "memory": True,
        "network": False,
        "self_update": False,
        "shell": False,
        "skills": False,
    }
