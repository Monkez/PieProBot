from __future__ import annotations

import asyncio
import json
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

from app.self_update.candidate import CandidateRecord, UpdatePlan


class SelfUpdateManager:
    """Safe two-body update simulation: stable workspace plus candidate copies."""

    def __init__(self, source_root: Path, runtime_root: Path) -> None:
        self.source_root = source_root.resolve()
        self.runtime_root = runtime_root.resolve()
        self.bodies_root = self.runtime_root / "bodies"
        self.candidates: dict[str, CandidateRecord] = {}
        self.plans: dict[str, UpdatePlan] = {}
        self.history: list[dict[str, object]] = []
        self.bodies_root.mkdir(parents=True, exist_ok=True)

    async def detect_update_need(self) -> dict[str, object]:
        return {"needed": False, "reasons": []}

    async def create_update_plan(self, goal: str, files_to_change: list[str] | None = None) -> UpdatePlan:
        plan = UpdatePlan(goal=goal, files_to_change=files_to_change or [])
        self.plans[plan.id] = plan
        return plan

    async def create_candidate_copy(self, plan_id: str) -> CandidateRecord:
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
        candidate_id = f"candidate-{timestamp}"
        destination = self.bodies_root / candidate_id
        ignore = shutil.ignore_patterns(".git", ".venv", "node_modules", ".next", "runtime", "__pycache__", ".pytest_cache")
        await asyncio.to_thread(shutil.copytree, self.source_root, destination, ignore=ignore)
        record = CandidateRecord(id=candidate_id, path=destination, plan_id=plan_id)
        self.candidates[candidate_id] = record
        return record

    async def apply_patch_to_candidate(self, candidate_id: str, patch_text: str) -> CandidateRecord:
        record = self.candidates[candidate_id]
        report_path = record.path / "UPDATE_PATCH.md"
        await asyncio.to_thread(report_path.write_text, patch_text, "utf-8")
        record.status = "patched"
        return record

    async def validate_candidate_config(self, candidate_id: str) -> dict[str, object]:
        record = self.candidates[candidate_id]
        config_root = record.path / "config"
        ok = config_root.exists() and any(config_root.rglob("*.yaml"))
        return {"ok": ok, "candidate_id": candidate_id}

    async def run_candidate_tests(self, candidate_id: str) -> dict[str, object]:
        record = self.candidates[candidate_id]
        fail_marker = record.path / "FAIL_TESTS"
        if fail_marker.exists():
            record.test_passed = False
            record.status = "test_failed"
            return {"ok": False, "candidate_id": candidate_id, "error": "FAIL_TESTS marker present"}

        command, cwd = self._candidate_test_command(record)
        if command is None:
            record.test_passed = await self._candidate_has_valid_config(record)
            record.status = "tested" if record.test_passed else "test_failed"
            return {"ok": record.test_passed, "candidate_id": candidate_id, "skipped": "no test suite found"}

        result = await asyncio.to_thread(
            subprocess.run,
            command,
            cwd=str(cwd),
            capture_output=True,
            text=True,
            timeout=180,
            check=False,
        )
        record.test_passed = result.returncode == 0
        record.status = "tested" if record.test_passed else "test_failed"
        return {
            "ok": record.test_passed,
            "candidate_id": candidate_id,
            "command": command,
            "returncode": result.returncode,
            "stdout": result.stdout[-20_000:],
            "stderr": result.stderr[-20_000:],
        }

    async def start_candidate(self, candidate_id: str) -> dict[str, object]:
        record = self.candidates[candidate_id]
        config_ok = await self.validate_candidate_config(candidate_id)
        if not config_ok["ok"]:
            record.status = "start_failed"
            return {"ok": False, "candidate_id": candidate_id, "error": "candidate config validation failed"}
        record.status = "started"
        return {"ok": True, "candidate_id": candidate_id, "port": 18080, "mode": "local-health-simulation"}

    async def run_candidate_healthcheck(self, candidate_id: str) -> dict[str, object]:
        record = self.candidates[candidate_id]
        config_ok = await self.validate_candidate_config(candidate_id)
        record.health_passed = bool(config_ok["ok"])
        return {"ok": record.health_passed, "candidate_id": candidate_id}

    async def promote_candidate(self, candidate_id: str) -> dict[str, object]:
        record = self.candidates[candidate_id]
        if not record.test_passed or not record.health_passed:
            raise ValueError("Candidate cannot be promoted until tests and health checks pass")
        pointer = self.bodies_root / "stable_pointer.json"
        payload = {"stable": candidate_id, "path": str(record.path), "promoted_at": datetime.now(timezone.utc).isoformat()}
        await asyncio.to_thread(pointer.write_text, json.dumps(payload, indent=2), "utf-8")
        record.status = "promoted"
        self.history.append({"event": "promoted", **payload})
        return payload

    async def rollback_candidate(self, candidate_id: str) -> dict[str, object]:
        record = self.candidates[candidate_id]
        record.status = "rolled_back"
        self.history.append({"event": "rolled_back", "candidate_id": candidate_id})
        return {"ok": True, "candidate_id": candidate_id}

    async def destroy_failed_candidate(self, candidate_id: str) -> dict[str, object]:
        record = self.candidates[candidate_id]
        if record.status == "promoted":
            raise ValueError("Promoted candidate cannot be destroyed")
        await asyncio.to_thread(shutil.rmtree, record.path, True)
        record.status = "destroyed"
        return {"ok": True, "candidate_id": candidate_id}

    async def write_update_report(self, candidate_id: str) -> dict[str, object]:
        record = self.candidates[candidate_id]
        report = {
            "candidate_id": candidate_id,
            "status": record.status,
            "test_passed": record.test_passed,
            "health_passed": record.health_passed,
        }
        path = self.bodies_root / f"{candidate_id}-report.json"
        await asyncio.to_thread(path.write_text, json.dumps(report, indent=2), "utf-8")
        record.report = str(path)
        return report

    def status(self) -> dict[str, object]:
        return {
            "candidates": [record.model_dump(mode="json") for record in self.candidates.values()],
            "plans": [plan.model_dump(mode="json") for plan in self.plans.values()],
            "history": self.history,
        }

    def _candidate_test_command(self, record: CandidateRecord) -> tuple[list[str], Path] | tuple[None, None]:
        backend_tests = record.path / "backend" / "tests"
        if backend_tests.exists():
            return [sys.executable, "-m", "pytest"], record.path / "backend"
        root_tests = record.path / "tests"
        if root_tests.exists():
            return [sys.executable, "-m", "pytest"], record.path
        return None, None

    async def _candidate_has_valid_config(self, record: CandidateRecord) -> bool:
        result = await self.validate_candidate_config(record.id)
        return bool(result["ok"])
