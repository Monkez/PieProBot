from __future__ import annotations

from app.config.loader import ConfigLoader


class HotReloadManager:
    def __init__(self, loader: ConfigLoader) -> None:
        self.loader = loader
        self.reload_count = 0

    def reload(self, scope: str = "all") -> dict[str, object]:
        if scope and scope != "all":
            try:
                result = self.loader.validator.validate_file(self.loader.safe_path(scope)).model_dump()
                results = [result]
            except Exception as exc:
                results = [{"ok": False, "path": scope, "errors": [str(exc)]}]
        else:
            results = self.loader.validate_all()
        ok = all(item["ok"] for item in results)
        if ok:
            self.reload_count += 1
        return {"ok": ok, "scope": scope, "reload_count": self.reload_count, "validation": results}
