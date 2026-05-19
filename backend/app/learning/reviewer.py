from __future__ import annotations

import re
import unicodedata

from app.learning.models import LearningItem, LearningProposal


class LearningReviewer:
    """Creates learning proposals from completed tasks.

    The reviewer is intentionally allowed to be proactive, but it only emits
    proposals. Policy + applier decide what becomes durable state.
    """

    def propose(self, task) -> LearningProposal:
        text = task.message
        lower = self._normalize(text).lower()
        items: list[LearningItem] = []

        preference = self._extract_preference(text)
        if preference:
            items.append(
                LearningItem(
                    kind="memory",
                    target="user_preference",
                    content=preference,
                    metadata={"importance": 0.8},
                    reason="explicit user preference",
                )
            )

        if task.result and self._has_reusable_workflow_signal(lower):
            skill_name = self._skill_name(lower)
            items.append(
                LearningItem(
                    kind="skill_create",
                    target=skill_name,
                    content=f"Reusable workflow for {skill_name.replace('-', ' ')} tasks in PiePro.",
                    reason="task contains reusable workflow signal",
                )
            )
            items.append(
                LearningItem(
                    kind="skill_reference",
                    target=skill_name,
                    content=(
                        f"# Session reference\n\n"
                        f"Task: {task.message}\n\n"
                        f"Result summary:\n{(task.result or '')[:4000]}\n"
                    ),
                    metadata={"file_path": f"references/{task.id}.md"},
                    reason="preserve session detail under class-level skill",
                )
            )

        confidence = 0.85 if items else 0.0
        return LearningProposal(
            task_id=task.id,
            confidence=confidence,
            summary=f"{len(items)} learning candidate(s) generated",
            items=items,
            status="pending" if items else "blocked",
        )

    @staticmethod
    def _extract_preference(text: str) -> str | None:
        patterns = [
            r"(?:remember|ghi nho)\s+(?:that\s+)?(.+)",
            r"(?:i prefer|toi thich|toi muon)\s+(.+)",
            r"(?:don't|do not|dung)\s+(.+)",
        ]
        normalized = LearningReviewer._normalize(text)
        for pattern in patterns:
            match = re.search(pattern, normalized, re.IGNORECASE)
            if match:
                return match.group(1).strip()[:500]
        return None

    @staticmethod
    def _has_reusable_workflow_signal(lower: str) -> bool:
        signals = [
            "fix",
            "bug",
            "implement",
            "debug",
            "workflow",
            "error",
            "improve",
            "complete",
            "analyze",
            "skill",
            "prompt",
            "cai tien",
            "hoan thien",
            "phan tich",
            "thuc hien",
            "them",
        ]
        return any(signal in lower for signal in signals)

    @staticmethod
    def _skill_name(lower: str) -> str:
        if any(word in lower for word in ["deploy", "release", "rollback"]):
            return "deployment-workflows"
        if any(word in lower for word in ["memory", "skill", "prompt", "learning"]):
            return "agent-learning-workflows"
        if any(word in lower for word in ["frontend", "ui", "dashboard"]):
            return "frontend-implementation"
        if any(word in lower for word in ["test", "bug", "fix", "implement", "code"]):
            return "coding-workflows"
        return "research-analysis-workflows"

    @staticmethod
    def _normalize(text: str) -> str:
        normalized = unicodedata.normalize("NFKD", text.replace("đ", "d").replace("Đ", "D"))
        return normalized.encode("ascii", "ignore").decode("ascii")
