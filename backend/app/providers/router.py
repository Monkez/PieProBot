from __future__ import annotations

from pathlib import Path

import yaml

from app.providers.base import BaseLLMProvider, ProviderResponse
from app.providers.local_provider import LocalProvider
from app.providers.openai_compatible_provider import OpenAICompatibleProvider
from app.providers.openai_provider import OpenAIProvider


class ProviderRouter:
    def __init__(self, providers: list[BaseLLMProvider] | None = None, configured: list[dict[str, object]] | None = None) -> None:
        self.providers = providers or [LocalProvider()]
        self.configured = configured or [{"name": provider.name, "enabled": True} for provider in self.providers]
        self.cost_total = 0.0

    @classmethod
    def from_config_dir(cls, config_dir: Path, plugin_factories: list | None = None) -> "ProviderRouter":
        providers: list[BaseLLMProvider] = []
        configured: list[dict[str, object]] = []
        for path in sorted(config_dir.glob("*.yaml")):
            data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
            name = str(data.get("name") or path.stem)
            provider_type = str(data.get("provider_type") or data.get("type") or name)
            enabled = bool(data.get("enabled", False))
            configured.append(
                {
                    "name": name,
                    "config_path": f"providers/{path.name}",
                    "provider_type": provider_type,
                    "enabled": enabled,
                    "api_key_env": data.get("api_key_env"),
                    "default_model": data.get("default_model"),
                    "base_url": data.get("base_url"),
                }
            )
            if not enabled:
                continue
            if name == "local":
                providers.append(LocalProvider())
            elif name == "openai":
                providers.append(OpenAIProvider())
            elif provider_type in {"openai_compatible", "custom"} or name in {"openai_compatible", "custom"}:
                providers.append(
                    OpenAICompatibleProvider(
                        name=name,
                        base_url=str(data.get("base_url", "http://localhost:1234/v1")),
                        api_key_env=str(data.get("api_key_env", "CUSTOM_PROVIDER_API_KEY" if name == "custom" else "OPENAI_COMPATIBLE_API_KEY")),
                        default_model=str(data.get("default_model", "local-model")),
                    )
                )
        if not providers:
            providers.append(LocalProvider())
            configured.append({"name": "local", "enabled": True, "default_model": "local-mock", "fallback_injected": True})
        for factory in plugin_factories or []:
            provider = factory()
            providers.append(provider)
            configured.append({"name": provider.name, "enabled": True, "provider_type": "plugin", "active": True})
        return cls(providers, configured)

    async def chat(self, messages: list[dict[str, str]], route: str = "default") -> ProviderResponse:
        last_error: Exception | None = None
        for provider in self.providers:
            try:
                response = await provider.chat(messages)
                self.cost_total += response.cost_estimate
                return response
            except Exception as exc:
                last_error = exc
        raise RuntimeError(f"All providers failed: {last_error}")

    async def chat_with_provider(self, name: str, messages: list[dict[str, str]]) -> ProviderResponse:
        for provider in self.providers:
            if provider.name == name:
                response = await provider.chat(messages)
                self.cost_total += response.cost_estimate
                return response
        raise ValueError(f"Provider is not active: {name}")

    async def status(self) -> list[dict[str, object]]:
        active = {provider.name: provider for provider in self.providers}
        status: list[dict[str, object]] = []
        for item in self.configured:
            provider = active.get(str(item["name"]))
            status.append(
                {
                    **item,
                    "active": provider is not None,
                    "healthy": await provider.health() if provider else False,
                }
            )
        return status
