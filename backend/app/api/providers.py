from __future__ import annotations

import json
import os
import re

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

from app.security.permissions import role_permissions

router = APIRouter(prefix="/api/providers", tags=["providers"])


class ProviderTestRequest(BaseModel):
    message: str = "health check"
    provider: str | None = None
    route: str = "normal"


class ProviderCreateRequest(BaseModel):
    name: str
    provider_type: str = "custom"
    enabled: bool = True
    base_url: str = ""
    api_key_env: str = "CUSTOM_PROVIDER_API_KEY"
    default_model: str = ""
    fast_model: str = ""
    normal_model: str = ""
    power_model: str = ""


class ProviderUpdateRequest(BaseModel):
    version: int = 1
    name: str
    provider_type: str = "custom"
    enabled: bool = True
    base_url: str = ""
    api_key_env: str = "CUSTOM_PROVIDER_API_KEY"
    default_model: str = ""
    model_profiles: dict[str, str] = {}


def load_provider_secrets(root) -> None:
    path = root / "runtime" / "provider_secrets.json"
    if not path.exists():
        return
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return
    if not isinstance(data, dict):
        return
    for key, value in data.items():
        if isinstance(key, str) and isinstance(value, str):
            os.environ.setdefault(key, value)


@router.get("")
async def list_providers(request: Request):
    return await request.app.state.providers.status()


@router.get("/status")
async def provider_status(request: Request):
    return await request.app.state.providers.status()


@router.post("/test")
async def test_provider(request: Request, payload: ProviderTestRequest):
    messages = [{"role": "user", "content": payload.message}]
    response = (
        await request.app.state.providers.chat_with_provider(payload.provider, messages, payload.route)
        if payload.provider
        else await request.app.state.providers.chat(messages, payload.route)
    )
    return response.model_dump()


@router.post("")
async def create_provider(request: Request, payload: ProviderCreateRequest):
    _require_provider_editor(request)
    name = _provider_name(payload.name)
    provider_type = _provider_type(payload.provider_type)

    normal_model = payload.normal_model or payload.default_model
    api_key_env = _api_key_env(request, name, payload.api_key_env)
    data = {
        "version": 1,
        "name": name,
        "provider_type": provider_type,
        "enabled": payload.enabled,
        "api_key_env": api_key_env,
        "base_url": payload.base_url,
        "default_model": payload.default_model or normal_model,
        "model_profiles": {
            "fast": payload.fast_model or normal_model,
            "normal": normal_model,
            "power": payload.power_model or normal_model,
        },
    }
    path = f"providers/{name}.yaml"
    _write_provider_config(request, path, data)

    _reload_providers(request)
    return {"ok": True, "path": path, "provider": data}


@router.put("/{name}")
async def update_provider(request: Request, name: str, payload: ProviderUpdateRequest):
    _require_provider_editor(request)
    provider_name = _provider_name(name)
    body_name = _provider_name(payload.name)
    if body_name != provider_name:
        raise HTTPException(status_code=400, detail="Provider name cannot be changed from this endpoint")
    normal_model = payload.model_profiles.get("normal") or payload.default_model
    api_key_env = _api_key_env(request, provider_name, payload.api_key_env)
    data = {
        "version": payload.version,
        "name": provider_name,
        "provider_type": _provider_type(payload.provider_type),
        "enabled": payload.enabled,
        "api_key_env": api_key_env,
        "base_url": payload.base_url,
        "default_model": payload.default_model or normal_model,
        "model_profiles": {
            "fast": payload.model_profiles.get("fast") or normal_model,
            "normal": normal_model,
            "power": payload.model_profiles.get("power") or normal_model,
        },
    }
    path = f"providers/{provider_name}.yaml"
    _write_provider_config(request, path, data)
    _reload_providers(request)
    return {"ok": True, "path": path, "provider": data}


@router.post("/reload")
async def reload_providers(request: Request):
    _require_provider_editor(request)
    _reload_providers(request)
    return {"ok": True}


def _provider_name(name: str) -> str:
    normalized = re.sub(r"[^a-z0-9_-]+", "-", name.strip().lower()).strip("-_")
    if not re.match(r"^[a-z0-9][a-z0-9_-]{0,63}$", normalized):
        raise HTTPException(status_code=400, detail="Provider name must contain letters or numbers")
    return normalized


def _provider_type(provider_type: str) -> str:
    value = provider_type.strip().lower() or "custom"
    if value not in {"custom", "openai_compatible", "openai", "local"}:
        raise HTTPException(status_code=400, detail="Unsupported provider_type")
    return value


def _write_provider_config(request: Request, path: str, data: dict[str, object]) -> None:
    try:
        request.app.state.config_loader.write(path, data)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


def _reload_providers(request: Request) -> None:
    request.app.state.providers = request.app.state.provider_router_factory()
    request.app.state.subagents.factory.provider_router = request.app.state.providers


def _api_key_env(request: Request, provider_name: str, value: str) -> str:
    candidate = value.strip()
    if not candidate:
        return f"{provider_name.upper().replace('-', '_')}_API_KEY"
    if re.match(r"^[A-Z_][A-Z0-9_]*$", candidate):
        return candidate
    env_name = f"{provider_name.upper().replace('-', '_')}_API_KEY"
    os.environ[env_name] = candidate
    _persist_provider_secret(request, env_name, candidate)
    return env_name


def _persist_provider_secret(request: Request, env_name: str, value: str) -> None:
    path = request.app.state.root / "runtime" / "provider_secrets.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    data: dict[str, str] = {}
    if path.exists():
        try:
            loaded = json.loads(path.read_text(encoding="utf-8"))
            if isinstance(loaded, dict):
                data = {str(key): str(secret) for key, secret in loaded.items() if isinstance(secret, str)}
        except Exception:
            data = {}
    data[env_name] = value
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")


def _require_provider_editor(request: Request) -> None:
    role = role_permissions(getattr(request.state, "role", "viewer"))
    if not role.can_edit_config:
        raise HTTPException(status_code=403, detail="Provider editing is not allowed for this role")
