from __future__ import annotations

from fastapi import APIRouter, Request
from pydantic import BaseModel

router = APIRouter(prefix="/api/config", tags=["config"])


class ConfigWriteRequest(BaseModel):
    data: dict[str, object]


class ConfigValidateRequest(BaseModel):
    path: str | None = None


@router.get("")
async def list_config(request: Request):
    return {"files": request.app.state.config_loader.list_files()}


@router.get("/{path:path}")
async def get_config(request: Request, path: str):
    return request.app.state.config_loader.read(path)


@router.put("/{path:path}")
async def put_config(request: Request, path: str, payload: ConfigWriteRequest):
    request.app.state.config_loader.write(path, payload.data)
    return {"ok": True}


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
        request.app.state.register_runtime_tools()
    return result


@router.post("/rollback")
async def rollback_config():
    return {"ok": True, "message": "Config rollback hook is available; no persisted rollback stack in MVP."}

