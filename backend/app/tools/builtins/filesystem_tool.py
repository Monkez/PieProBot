from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Any


BLOCKED_NAMES = {".env", "id_rsa", "id_dsa", "private.key"}


def _resolve_safe(workspace: Path, raw_path: str) -> Path:
    candidate = (workspace / raw_path).resolve()
    workspace_resolved = workspace.resolve()
    if workspace_resolved not in [candidate, *candidate.parents]:
        raise PermissionError("Path traversal blocked")
    if candidate.name in BLOCKED_NAMES or ".ssh" in candidate.parts:
        raise PermissionError("Secret-like file access blocked")
    return candidate


async def execute(payload: dict[str, Any]) -> dict[str, Any]:
    workspace = Path(payload.get("workspace", ".")).resolve()
    path = _resolve_safe(workspace, str(payload["path"]))
    operation = payload.get("operation", "read")
    if operation == "read":
        text = await asyncio.to_thread(path.read_text, encoding="utf-8")
        return {"path": str(path), "content": text}
    if operation == "write":
        content = str(payload.get("content", ""))
        await asyncio.to_thread(path.parent.mkdir, parents=True, exist_ok=True)
        await asyncio.to_thread(path.write_text, content, encoding="utf-8")
        return {"path": str(path), "bytes": len(content.encode("utf-8"))}
    raise ValueError(f"Unsupported filesystem operation: {operation}")

