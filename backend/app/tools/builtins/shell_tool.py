from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Any


async def execute(payload: dict[str, Any]) -> dict[str, Any]:
    command = str(payload.get("command", ""))
    allowlist = set(payload.get("allowlist", []))
    executable = command.split()[0] if command.split() else ""
    if executable not in allowlist:
        raise PermissionError(f"Command '{executable}' is not allowlisted")
    workspace = Path(payload.get("workspace", ".")).resolve()
    proc = await asyncio.create_subprocess_shell(
        command,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        cwd=str(workspace),
    )
    stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=float(payload.get("timeout", 5)))
    return {
        "returncode": proc.returncode,
        "stdout": stdout.decode(errors="replace")[:20_000],
        "stderr": stderr.decode(errors="replace")[:20_000],
    }
