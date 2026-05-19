from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

from app.security.permissions import role_permissions

router = APIRouter(prefix="/api/config", tags=["config"])


class ConfigWriteRequest(BaseModel):
    data: dict[str, object]
    reload: bool = False


class ConfigValidateRequest(BaseModel):
    path: str | None = None


class ConfigRollbackRequest(BaseModel):
    path: str | None = None


class ConfigReloadRequest(BaseModel):
    scope: str = "all"


@router.get("")
async def list_config(request: Request):
    return {"files": request.app.state.config_loader.list_files()}


@router.get("/{path:path}")
async def get_config(request: Request, path: str):
    return request.app.state.config_loader.read(path)


@router.put("/{path:path}")
async def put_config(request: Request, path: str, payload: ConfigWriteRequest):
    _require_config_editor(request)
    try:
        request.app.state.config_loader.write(path, payload.data)
    except (PermissionError, ValueError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    result: dict[str, object] = {"ok": True, "path": path}
    if payload.reload:
        result["reload"] = _reload_scope(request, path, validate=False)
    return result


@router.post("/validate")
async def validate_config(request: Request, payload: ConfigValidateRequest):
    if payload.path:
        path = request.app.state.config_loader.safe_path(payload.path)
        return request.app.state.config_loader.validator.validate_file(path).model_dump()
    return request.app.state.config_loader.validate_all()


@router.post("/reload")
async def reload_config(request: Request, payload: ConfigReloadRequest | None = None):
    _require_config_editor(request)
    scope = payload.scope if payload else "all"
    result = request.app.state.hot_reload.reload(scope)
    if result["ok"]:
        _apply_runtime_reload(request, scope)
    return result


@router.post("/rollback")
async def rollback_config(request: Request, payload: ConfigRollbackRequest | None = None):
    _require_config_editor(request)
    result = request.app.state.config_loader.rollback(payload.path if payload else None)
    if result["ok"]:
        request.app.state.tools.load()
        request.app.state.providers = request.app.state.provider_router_factory()
        request.app.state.channels = request.app.state.channel_manager_factory()
        request.app.state.subagents.factory.provider_router = request.app.state.providers
        request.app.state.register_runtime_tools()
    return result


def _reload_scope(request: Request, scope: str, validate: bool = True) -> dict[str, object]:
    result = request.app.state.hot_reload.reload(scope) if validate else {"ok": True, "scope": scope}
    if result["ok"]:
        _apply_runtime_reload(request, scope)
    return result


def _apply_runtime_reload(request: Request, scope: str) -> None:
    if scope == "all" or scope.startswith("tools/"):
        request.app.state.tools.load()
    if scope == "all" or scope.startswith("providers/"):
        request.app.state.providers = request.app.state.provider_router_factory()
        request.app.state.subagents.factory.provider_router = request.app.state.providers
    if scope == "all" or scope.startswith("channels/"):
        request.app.state.channels = request.app.state.channel_manager_factory()
    request.app.state.register_runtime_tools()


def _require_config_editor(request: Request) -> None:
    role = role_permissions(getattr(request.state, "role", "viewer"))
    if not role.can_edit_config:
        raise HTTPException(status_code=403, detail="Config editing is not allowed for this role")
