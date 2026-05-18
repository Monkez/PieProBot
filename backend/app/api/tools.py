from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

router = APIRouter(prefix="/api/tools", tags=["tools"])


class ToolExecuteRequest(BaseModel):
    payload: dict[str, object] = {}
    permissions: dict[str, bool] = {}


@router.get("")
async def list_tools(request: Request):
    return [tool.model_dump() for tool in request.app.state.tools.list()]


@router.get("/{tool_name:path}")
async def get_tool(request: Request, tool_name: str):
    try:
        return request.app.state.tools.get(tool_name).model_dump()
    except KeyError:
        raise HTTPException(status_code=404, detail="Tool not found") from None


@router.post("/{tool_name:path}/execute")
async def execute_tool(request: Request, tool_name: str, payload: ToolExecuteRequest):
    result = await request.app.state.tools.execute(tool_name, dict(payload.payload), payload.permissions)
    return result.model_dump()


@router.post("/{tool_name:path}/enable")
async def enable_tool(request: Request, tool_name: str):
    request.app.state.tools.get(tool_name).enabled = True
    return {"ok": True}


@router.post("/{tool_name:path}/disable")
async def disable_tool(request: Request, tool_name: str):
    request.app.state.tools.get(tool_name).enabled = False
    return {"ok": True}


@router.post("/reload")
async def reload_tools(request: Request):
    request.app.state.tools.load()
    request.app.state.register_runtime_tools()
    return {"ok": True, "count": len(request.app.state.tools.definitions)}

