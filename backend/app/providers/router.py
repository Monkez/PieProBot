from __future__ import annotations

from pathlib import Path

import yaml

from app.observability.logging import get_logger
from app.providers.base import BaseLLMProvider, ProviderResponse
from app.providers.local_provider import LocalProvider
from app.providers.openai_compatible_provider import OpenAICompatibleProvider


class ProviderRouter:
    def __init__(self, providers: list[BaseLLMProvider] | None = None, configured: list[dict[str, object]] | None = None) -> None:
        self.providers = providers or [LocalProvider()]
        self.configured = configured or [{"name": provider.name, "enabled": True} for provider in self.providers]
        self.cost_total = 0.0
        self.logger = get_logger("providers")

    @classmethod
    def from_config_dir(cls, config_dir: Path, plugin_factories: list | None = None) -> "ProviderRouter":
        providers: list[BaseLLMProvider] = []
        local_providers: list[BaseLLMProvider] = []
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
                    "model_profiles": cls._model_profiles(data),
                    "base_url": data.get("base_url"),
                    "timeout_seconds": data.get("timeout_seconds", 120),
                }
            )
            if not enabled:
                continue
            if provider_type == "local" or name == "local":
                local_providers.append(LocalProvider())
            elif provider_type == "openai" or name == "openai":
                providers.append(
                    OpenAICompatibleProvider(
                        name=name,
                        base_url=str(data.get("base_url", "https://api.openai.com/v1")),
                        api_key_env=str(data.get("api_key_env", "OPENAI_API_KEY")),
                        default_model=str(data.get("default_model", "gpt-4.1-mini")),
                        timeout_seconds=float(data.get("timeout_seconds", 120)),
                    )
                )
            elif provider_type in {"openai_compatible", "custom"} or name in {"openai_compatible", "custom"}:
                providers.append(
                    OpenAICompatibleProvider(
                        name=name,
                        base_url=str(data.get("base_url", "http://localhost:1234/v1")),
                        api_key_env=str(data.get("api_key_env", "CUSTOM_PROVIDER_API_KEY" if name == "custom" else "OPENAI_COMPATIBLE_API_KEY")),
                        default_model=str(data.get("default_model", "local-model")),
                        timeout_seconds=float(data.get("timeout_seconds", 120)),
                    )
                )
        providers.extend(local_providers)
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
        failures: list[str] = []
        for provider in self.providers:
            try:
                response = await provider.chat(messages, self._model_for(provider.name, route))
                self.cost_total += response.cost_estimate
                return response
            except Exception as exc:
                last_error = exc
                failures.append(f"{provider.name}: {exc!r}")
                self.logger.warning("provider failed: %s", failures[-1])
        raise RuntimeError(f"All providers failed: {'; '.join(failures) or repr(last_error)}")

    async def chat_with_provider(self, name: str, messages: list[dict[str, str]], route: str = "default") -> ProviderResponse:
        for provider in self.providers:
            if provider.name == name:
                response = await provider.chat(messages, self._model_for(name, route))
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

    def _model_for(self, provider_name: str, route: str) -> str | None:
        normalized = "normal" if route in {"default", ""} else route
        for item in self.configured:
            if item.get("name") != provider_name:
                continue
            profiles = item.get("model_profiles")
            if isinstance(profiles, dict):
                model = profiles.get(normalized) or profiles.get("normal")
                if model:
                    return str(model)
            default_model = item.get("default_model")
            return str(default_model) if default_model else None
        return None

    @staticmethod
    def _model_profiles(data: dict[str, object]) -> dict[str, str]:
        raw = data.get("model_profiles")
        profiles = raw if isinstance(raw, dict) else {}
        default_model = data.get("default_model")
        normal = profiles.get("normal") or default_model
        return {
            "fast": str(profiles.get("fast") or normal or ""),
            "normal": str(normal or ""),
            "power": str(profiles.get("power") or normal or ""),
        }
