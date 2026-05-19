from __future__ import annotations

import base64
import time
from pathlib import Path
from uuid import uuid4


class CheckpointManager:
    """File-level checkpoint store for mutating tools.

    It snapshots target files before writes and can restore them later. Shell
    commands can opt into a workspace snapshot with `workspace` and
    `checkpoint_paths`; PiePro avoids trying to snapshot arbitrary trees by
    default.
    """

    def __init__(self, root: Path, state_store=None) -> None:
        self.root = root
        self.state_store = state_store
        self.dir = root / "runtime" / "checkpoints"
        self.dir.mkdir(parents=True, exist_ok=True)

    def snapshot_files(self, label: str, workspace: Path, paths: list[Path]) -> str | None:
        files = []
        workspace = workspace.resolve()
        for path in paths:
            resolved = path.resolve()
            try:
                rel = str(resolved.relative_to(workspace))
            except ValueError:
                continue
            if resolved.exists() and resolved.is_file():
                data = base64.b64encode(resolved.read_bytes()).decode("ascii")
                files.append({"path": rel, "exists": True, "content_b64": data})
            else:
                files.append({"path": rel, "exists": False, "content_b64": ""})
        if not files:
            return None

        checkpoint_id = f"chk_{uuid4().hex[:12]}"
        payload = {"id": checkpoint_id, "label": label, "workspace": str(workspace), "files": files}
        checkpoint_path = self.dir / f"{checkpoint_id}.json"
        checkpoint_path.write_text(__import__("json").dumps(payload, indent=2), encoding="utf-8")
        if self.state_store:
            self.state_store.execute(
                """
                INSERT INTO checkpoints(id, label, workspace, data_json, created_at)
                VALUES(?, ?, ?, ?, ?)
                """,
                (checkpoint_id, label, str(workspace), __import__("json").dumps(payload), time.time()),
            )
        return checkpoint_id

    def rollback(self, checkpoint_id: str) -> dict[str, object]:
        import json

        path = self.dir / f"{checkpoint_id}.json"
        if not path.exists():
            raise FileNotFoundError(f"Checkpoint not found: {checkpoint_id}")
        payload = json.loads(path.read_text(encoding="utf-8"))
        workspace = Path(payload["workspace"]).resolve()
        restored: list[str] = []
        removed: list[str] = []
        for item in payload.get("files", []):
            target = (workspace / item["path"]).resolve()
            try:
                target.relative_to(workspace)
            except ValueError:
                continue
            if item.get("exists"):
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(base64.b64decode(item.get("content_b64", "")))
                restored.append(str(target))
            elif target.exists():
                target.unlink()
                removed.append(str(target))
        return {"checkpoint_id": checkpoint_id, "restored": restored, "removed": removed}
