from __future__ import annotations

from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import yaml

from app.config.schema import ConfigValidationResult


class ConfigValidator:
    def validate_file(self, path: Path) -> ConfigValidationResult:
        try:
            data = yaml.safe_load(path.read_text(encoding="utf-8"))
            if not isinstance(data, dict):
                return ConfigValidationResult(ok=False, path=str(path), errors=["Config must be a YAML object"])
            errors = self._validate_common(data)
            errors.extend(self._validate_by_path(path, data))
            return ConfigValidationResult(ok=not errors, path=str(path), errors=errors)
        except Exception as exc:
            return ConfigValidationResult(ok=False, path=str(path), errors=[str(exc)])

    def _validate_common(self, data: dict[str, Any]) -> list[str]:
        errors: list[str] = []
        if "version" not in data:
            errors.append("Missing config version")
        elif not isinstance(data["version"], int):
            errors.append("Config version must be an integer")
        return errors

    def _validate_by_path(self, path: Path, data: dict[str, Any]) -> list[str]:
        normalized = path.as_posix()
        if "/providers/" in normalized or "\\providers\\" in str(path):
            return self._validate_provider(data)
        if "/tools/" in normalized or "\\tools\\" in str(path):
            return self._validate_tool(data)
        if "/channels/" in normalized or "\\channels\\" in str(path):
            return self._validate_channel(data)
        if "/memory/" in normalized or "\\memory\\" in str(path):
            return self._validate_memory(data)
        if "/agent/" in normalized or "\\agent\\" in str(path):
            return self._validate_agent(data)
        if "/security/" in normalized or "\\security\\" in str(path):
            return self._validate_security(data)
        return []

    def _validate_provider(self, data: dict[str, Any]) -> list[str]:
        errors: list[str] = []
        self._require_str(data, "name", errors)
        provider_type = str(data.get("provider_type") or data.get("type") or data.get("name") or "")
        if provider_type not in {"local", "openai", "openai_compatible", "custom", "anthropic"}:
            errors.append("provider_type must be one of local, openai, openai_compatible, custom, anthropic")
        if not isinstance(data.get("enabled", False), bool):
            errors.append("enabled must be a boolean")
        if provider_type in {"openai", "openai_compatible", "custom", "anthropic"}:
            self._require_str(data, "api_key_env", errors)
            base_url = data.get("base_url")
            if provider_type in {"openai_compatible", "custom"}:
                self._require_url(base_url, "base_url", errors)
            elif base_url is not None and str(base_url).strip():
                self._require_url(base_url, "base_url", errors)
            timeout = data.get("timeout_seconds", 120)
            if not isinstance(timeout, (int, float)) or timeout <= 0:
                errors.append("timeout_seconds must be a positive number")
        profiles = data.get("model_profiles")
        if profiles is not None:
            if not isinstance(profiles, dict):
                errors.append("model_profiles must be an object")
            else:
                for key in ("fast", "normal", "power"):
                    if key in profiles and not isinstance(profiles[key], str):
                        errors.append(f"model_profiles.{key} must be a string")
        return errors

    def _validate_tool(self, data: dict[str, Any]) -> list[str]:
        errors: list[str] = []
        self._require_str(data, "name", errors)
        if not isinstance(data.get("enabled", True), bool):
            errors.append("enabled must be a boolean")
        for key in ("input_schema", "output_schema", "permissions", "sandbox_policy", "rate_limit"):
            value = data.get(key)
            if value is not None and not isinstance(value, dict):
                errors.append(f"{key} must be an object")
        timeout = data.get("timeout_seconds", 10)
        if not isinstance(timeout, (int, float)) or timeout <= 0:
            errors.append("timeout_seconds must be a positive number")
        audit_level = data.get("audit_level", "standard")
        if audit_level not in {"none", "standard", "full"}:
            errors.append("audit_level must be one of none, standard, full")
        return errors

    def _validate_channel(self, data: dict[str, Any]) -> list[str]:
        errors: list[str] = []
        self._require_str(data, "name", errors)
        self._require_str(data, "type", errors)
        if not isinstance(data.get("enabled", False), bool):
            errors.append("enabled must be a boolean")
        if data.get("type") == "telegram":
            self._require_str(data, "bot_token_env", errors)
        return errors

    def _validate_memory(self, data: dict[str, Any]) -> list[str]:
        errors: list[str] = []
        if "enabled" in data and not isinstance(data["enabled"], bool):
            errors.append("enabled must be a boolean")
        if "gateway_url" in data:
            self._require_url(data.get("gateway_url"), "gateway_url", errors)
        if "max_results" in data and (not isinstance(data["max_results"], int) or data["max_results"] <= 0):
            errors.append("max_results must be a positive integer")
        return errors

    def _validate_agent(self, data: dict[str, Any]) -> list[str]:
        errors: list[str] = []
        for key in ("max_subagents", "max_concurrent", "max_spawn_depth", "heartbeat_interval_seconds", "heartbeat_timeout_seconds"):
            if key in data and (not isinstance(data[key], int) or data[key] < 0):
                errors.append(f"{key} must be a non-negative integer")
        for key in ("blocked_tools", "types"):
            if key in data and not self._is_str_list(data[key]):
                errors.append(f"{key} must be a list of strings")
        return errors

    def _validate_security(self, data: dict[str, Any]) -> list[str]:
        errors: list[str] = []
        if "roles" in data and not isinstance(data["roles"], dict):
            errors.append("roles must be an object")
        if "dangerous_actions_require_approval" in data and not self._is_str_list(data["dangerous_actions_require_approval"]):
            errors.append("dangerous_actions_require_approval must be a list of strings")
        return errors

    def _require_str(self, data: dict[str, Any], key: str, errors: list[str]) -> None:
        if not isinstance(data.get(key), str) or not str(data.get(key)).strip():
            errors.append(f"{key} must be a non-empty string")

    def _require_url(self, value: Any, key: str, errors: list[str]) -> None:
        parsed = urlparse(str(value or ""))
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            errors.append(f"{key} must be an http(s) URL")

    def _is_str_list(self, value: Any) -> bool:
        return isinstance(value, list) and all(isinstance(item, str) for item in value)
