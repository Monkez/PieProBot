from __future__ import annotations

from pathlib import Path


class Sandbox:
    def __init__(self, workspace: Path) -> None:
        self.workspace = workspace.resolve()

    def assert_inside(self, path: Path) -> None:
        resolved = path.resolve()
        if self.workspace not in [resolved, *resolved.parents]:
            raise PermissionError("Access outside sandbox blocked")

