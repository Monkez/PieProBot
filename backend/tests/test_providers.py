from __future__ import annotations

from pathlib import Path

from app.providers.router import ProviderRouter


async def test_provider_router_loads_configured_providers() -> None:
    router = ProviderRouter.from_config_dir(Path(__file__).resolve().parents[2] / "config" / "providers")
    status = await router.status()
    names = {item["name"] for item in status}
    assert {"local", "openai", "openai_compatible", "anthropic", "custom"}.issubset(names)
    assert any(item["name"] == "custom" and item["base_url"] for item in status)
    assert any(item["name"] == "local" and item["active"] and item["healthy"] for item in status)
