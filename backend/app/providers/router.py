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
    def from_config_dir(cls, config_dir: Path) -> "ProviderRouter":
        providers: list[BaseLLMProvider] = []
        configured: list[dict[str, object]] = []
        for path in sorted(config_dir.glob("*.yaml")):
            data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
            name = str(data.get("name") or path.stem)
            enabled = bool(data.get("enabled", False))
            configured.append({"name": name, "enabled": enabled, "default_model": data.get("default_model")})
            if not enabled:
                continue
            if name == "local":
                providers.append(LocalProvider())
            elif name == "openai":
                providers.append(OpenAIProvider())
            elif name == "openai_compatible":
                providers.append(
                    OpenAICompatibleProvider(
                        name=name,
                        base_url=str(data.get("base_url", "http://localhost:1234/v1")),
                        api_key_env=str(data.get("api_key_env", "OPENAI_COMPATIBLE_API_KEY")),
                        default_model=str(data.get("default_model", "local-model")),
                    )
                )
        if not providers:
            providers.append(LocalProvider())
            configured.append({"name": "local", "enabled": True, "default_model": "local-mock", "fallback_injected": True})
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
