from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from app.config.validator import ConfigValidator


class ConfigLoader:
    def __init__(self, root: Path) -> None:
        self.root = root
        self.validator = ConfigValidator()
        self._rollback_stack: list[tuple[str, str | None]] = []

    def list_files(self) -> list[str]:
        return [str(path.relative_to(self.root)).replace("\\", "/") for path in sorted(self.root.rglob("*.yaml"))]

    def safe_path(self, relative_path: str) -> Path:
        candidate = (self.root / relative_path).resolve()
        root = self.root.resolve()
        if root not in [candidate, *candidate.parents]:
            raise PermissionError("Config path traversal blocked")
        if candidate.suffix != ".yaml":
            raise ValueError("Only YAML config files are supported")
        return candidate

    def read(self, relative_path: str) -> dict[str, Any]:
        path = self.safe_path(relative_path)
        return yaml.safe_load(path.read_text(encoding="utf-8")) or {}

    def write(self, relative_path: str, data: dict[str, Any]) -> None:
        path = self.safe_path(relative_path)
        previous = path.read_text(encoding="utf-8") if path.exists() else None
        rendered = yaml.safe_dump(data, sort_keys=False)
        path.write_text(rendered, encoding="utf-8")
        new_result = self.validator.validate_file(path)
        if not new_result.ok:
            if previous is not None:
                path.write_text(previous, encoding="utf-8")
            raise ValueError("; ".join(new_result.errors))
        self._rollback_stack.append((relative_path, previous))

    def rollback(self, relative_path: str | None = None) -> dict[str, object]:
        for index in range(len(self._rollback_stack) - 1, -1, -1):
            path_text, previous = self._rollback_stack[index]
            if relative_path and path_text != relative_path:
                continue
            path = self.safe_path(path_text)
            if previous is None:
                path.unlink(missing_ok=True)
            else:
                path.write_text(previous, encoding="utf-8")
            self._rollback_stack.pop(index)
            return {"ok": True, "path": path_text}
        return {"ok": False, "message": "No rollback entry found"}

    def validate_all(self) -> list[dict[str, object]]:
        return [self.validator.validate_file(self.root / path).model_dump() for path in self.list_files()]
