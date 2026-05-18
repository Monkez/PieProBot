from __future__ import annotations

import os


class SecretManager:
    def get_ref(self, env_name: str) -> str | None:
        return os.getenv(env_name)

    def redact(self, value: str) -> str:
        return "***" if value else ""

