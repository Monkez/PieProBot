from __future__ import annotations

from pathlib import Path

import pytest

from app.self_update.manager import SelfUpdateManager


async def test_candidate_failure_does_not_promote(tmp_path: Path) -> None:
    source = tmp_path / "source"
    (source / "config").mkdir(parents=True)
    (source / "config" / "app.yaml").write_text("version: 1\nname: test\n", encoding="utf-8")
    manager = SelfUpdateManager(source, tmp_path / "runtime")
    plan = await manager.create_update_plan("bad update")
    candidate = await manager.create_candidate_copy(plan.id)
    (candidate.path / "FAIL_TESTS").write_text("fail", encoding="utf-8")
    result = await manager.run_candidate_tests(candidate.id)
    assert result["ok"] is False
    with pytest.raises(ValueError):
        await manager.promote_candidate(candidate.id)
    assert not (manager.bodies_root / "stable_pointer.json").exists()


async def test_candidate_success_promotes(tmp_path: Path) -> None:
    source = tmp_path / "source"
    (source / "config").mkdir(parents=True)
    (source / "config" / "app.yaml").write_text("version: 1\nname: test\n", encoding="utf-8")
    manager = SelfUpdateManager(source, tmp_path / "runtime")
    plan = await manager.create_update_plan("good update")
    candidate = await manager.create_candidate_copy(plan.id)
    assert (await manager.run_candidate_tests(candidate.id))["ok"] is True
    assert (await manager.run_candidate_healthcheck(candidate.id))["ok"] is True
    promoted = await manager.promote_candidate(candidate.id)
    assert promoted["stable"] == candidate.id

