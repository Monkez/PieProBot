from __future__ import annotations

from pathlib import Path

from app.providers.router import ProviderRouter
from types import SimpleNamespace

from app.api.providers import _api_key_env, load_provider_secrets


async def test_provider_router_loads_configured_providers() -> None:
    router = ProviderRouter.from_config_dir(Path(__file__).resolve().parents[2] / "config" / "providers")
    status = await router.status()
    names = {item["name"] for item in status}
    assert {"local", "openai", "openai_compatible", "anthropic", "custom"}.issubset(names)
    assert any(item["name"] == "custom" and item["base_url"] for item in status)
    assert any(item["name"] == "local" and item["active"] and item["healthy"] for item in status)
    assert any(item["name"] == "local" and item["model_profiles"]["fast"] == "local-mock" for item in status)


async def test_provider_router_uses_model_profiles(tmp_path: Path) -> None:
    providers_dir = tmp_path / "providers"
    providers_dir.mkdir()
    (providers_dir / "local.yaml").write_text(
        """
version: 1
name: local
enabled: true
default_model: normal-model
model_profiles:
  fast: fast-model
  normal: normal-model
  power: power-model
""",
        encoding="utf-8",
    )
    router = ProviderRouter.from_config_dir(providers_dir)

    fast = await router.chat([{"role": "user", "content": "hi"}], route="fast")
    power = await router.chat([{"role": "user", "content": "hi"}], route="power")

    assert fast.model == "fast-model"
    assert power.model == "power-model"


def test_provider_api_key_value_becomes_runtime_env(tmp_path: Path) -> None:
    request = SimpleNamespace(app=SimpleNamespace(state=SimpleNamespace(root=tmp_path)))
    env_name = _api_key_env(request, "chiasegpu", "sk-test-value")

    assert env_name == "CHIASEGPU_API_KEY"
    assert __import__("os").environ[env_name] == "sk-test-value"
    assert "sk-test-value" in (tmp_path / "runtime" / "provider_secrets.json").read_text(encoding="utf-8")


def test_provider_secrets_load_on_boot(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.delenv("CHIASEGPU_API_KEY", raising=False)
    secrets = tmp_path / "runtime" / "provider_secrets.json"
    secrets.parent.mkdir()
    secrets.write_text('{"CHIASEGPU_API_KEY": "persisted-key"}', encoding="utf-8")

    load_provider_secrets(tmp_path)

    assert __import__("os").environ["CHIASEGPU_API_KEY"] == "persisted-key"
