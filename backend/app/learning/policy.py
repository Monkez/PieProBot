from __future__ import annotations

import re

from app.learning.models import LearningItem, LearningProposal


SECRET_PATTERNS = (
    "api_key",
    "apikey",
    "password",
    "secret",
    "token",
    "private key",
)

TRANSIENT_PATTERNS = (
    "today",
    "temporary",
    "network failed",
    "command not found",
    "missing api key",
    "gateway down",
    "phase ",
    "pr #",
    "commit ",
)


class LearningPolicy:
    """Classifies proactive learning proposals before durable writes."""

    def classify(self, proposal: LearningProposal) -> LearningProposal:
        for item in proposal.items:
            item.decision, item.reason = self._classify_item(item)
        if proposal.items and all(item.decision == "blocked" for item in proposal.items):
            proposal.status = "blocked"
        proposal.touch()
        return proposal

    def _classify_item(self, item: LearningItem) -> tuple[str, str]:
        content_lower = item.content.lower()
        target_lower = item.target.lower()
        if any(pattern in content_lower for pattern in SECRET_PATTERNS):
            return "blocked", "may contain secret material"
        if any(pattern in content_lower for pattern in TRANSIENT_PATTERNS):
            return "blocked", "looks transient or task-progress-like"
        if item.kind == "memory":
            if item.target in {"user_preference", "project_fact", "environment_fact"}:
                return "safe", "durable declarative memory"
            return "review", "memory target needs review"
        if item.kind == "skill_create":
            if self._is_class_level_skill(target_lower):
                return "safe", "class-level skill name"
            return "review", "skill name may be too narrow"
        if item.kind == "skill_reference":
            if self._is_class_level_skill(target_lower):
                return "safe", "session detail under class-level skill"
            return "review", "reference target needs review"
        if item.kind == "skill_patch":
            if len(item.content) <= 2000 and self._is_class_level_skill(target_lower):
                return "review", "patches require review unless explicitly approved"
            return "blocked", "patch too broad or unsafe"
        if item.kind == "skill_archive":
            return "review", "archive/delete actions require human review"
        return "review", "unknown item kind"

    @staticmethod
    def _is_class_level_skill(name: str) -> bool:
        if not re.match(r"^[a-z0-9][a-z0-9._-]{0,63}$", name):
            return False
        narrow_markers = ("task_", "sub_", "pr-", "issue-", "bug-", "fix-", "today", "tmp")
        if any(marker in name for marker in narrow_markers):
            return False
        return name.endswith("-workflows") or name in {"frontend-implementation", "agent-learning-workflows"}
