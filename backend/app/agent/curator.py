from __future__ import annotations

from collections import defaultdict


class SkillCurator:
    """Keeps the skill library biased toward class-level umbrella skills."""

    def __init__(self, skills) -> None:
        self.skills = skills

    def run_once(self, dry_run: bool = True) -> dict[str, object]:
        clusters = defaultdict(list)
        for item in self.skills.list():
            prefix = item["name"].split("-", 1)[0]
            clusters[prefix].append(item)

        proposals = []
        for prefix, items in clusters.items():
            if len(items) < 2:
                continue
            umbrella = f"{prefix}-workflows"
            proposals.append(
                {
                    "cluster": prefix,
                    "umbrella": umbrella,
                    "members": [item["name"] for item in items],
                    "action": "consolidate",
                }
            )
            if not dry_run and not any(item["name"] == umbrella for item in self.skills.list()):
                self.skills.create(umbrella, f"Umbrella workflow skill for {prefix} tasks.")
        return {"dry_run": dry_run, "proposals": proposals}
