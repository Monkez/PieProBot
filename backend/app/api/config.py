from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

router = APIRouter(prefix="/api/config", tags=["config"])


class ConfigWriteRequest(BaseModel):
    data: dict[str, object]


class ConfigValidateRequest(BaseModel):
    path: str | None = None


class ConfigRollbackRequest(BaseModel):
    path: str | None = None


@router.get("")
async def list_config(request: Request):
    return {"files": request.app.state.config_loader.list_files()}


@router.get("/{path:path}")
async def get_config(request: Request, path: str):
    return request.app.state.config_loader.read(path)


@router.put("/{path:path}")
async def put_config(request: Request, path: str, payload: ConfigWriteRequest):
    try:
        request.app.state.config_loader.write(path, payload.data)
    except (PermissionError, ValueError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"ok": True, "path": path}


@router.post("/validate")
async def validate_config(request: Request, payload: ConfigValidateRequest):
    if payload.path:
        path = request.app.state.config_loader.safe_path(payload.path)
        return request.app.state.config_loader.validator.validate_file(path).model_dump()
    return request.app.state.config_loader.validate_all()


@router.post("/reload")
async def reload_config(request: Request):
    result = request.app.state.hot_reload.reload()
    if result["ok"]:
        request.app.state.tools.load()
        request.app.state.providers = request.app.state.provider_router_factory()
        request.app.state.channels = request.app.state.channel_manager_factory()
        request.app.state.subagents.factory.provider_router = request.app.state.providers
        request.app.state.register_runtime_tools()
    return result


@router.post("/rollback")
async def rollback_config(request: Request, payload: ConfigRollbackRequest | None = None):
    result = request.app.state.config_loader.rollback(payload.path if payload else None)
    if result["ok"]:
        request.app.state.tools.load()
        request.app.state.providers = request.app.state.provider_router_factory()
        request.app.state.channels = request.app.state.channel_manager_factory()
        request.app.state.subagents.factory.provider_router = request.app.state.providers
        request.app.state.register_runtime_tools()
    return result
