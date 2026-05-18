from __future__ import annotations

from pathlib import Path

import yaml

from app.config.schema import ConfigValidationResult


class ConfigValidator:
    def validate_file(self, path: Path) -> ConfigValidationResult:
        try:
            data = yaml.safe_load(path.read_text(encoding="utf-8"))
            if not isinstance(data, dict):
                return ConfigValidationResult(ok=False, path=str(path), errors=["Config must be a YAML object"])
            if "version" not in data:
                return ConfigValidationResult(ok=False, path=str(path), errors=["Missing config version"])
            return ConfigValidationResult(ok=True, path=str(path))
        except Exception as exc:
            return ConfigValidationResult(ok=False, path=str(path), errors=[str(exc)])

