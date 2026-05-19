from __future__ import annotations

from app.learning.models import LearningItem, LearningProposal
from app.memory.manager import MemoryItem


class LearningApplier:
    def __init__(self, *, memory, skills) -> None:
        self.memory = memory
        self.skills = skills

    async def apply_safe(self, proposal: LearningProposal) -> LearningProposal:
        for item in proposal.items:
            if item.decision == "safe" and not item.applied:
                await self._apply_item(item, proposal.task_id)
        self._refresh_status(proposal)
        return proposal

    async def apply_all_review_items(self, proposal: LearningProposal) -> LearningProposal:
        for item in proposal.items:
            if item.decision in {"safe", "review"} and not item.applied:
                await self._apply_item(item, proposal.task_id)
        self._refresh_status(proposal)
        return proposal

    async def _apply_item(self, item: LearningItem, task_id: str) -> None:
        if item.kind == "memory":
            await self.memory.save(
                MemoryItem(
                    type=item.target,
                    content=item.content,
                    source=task_id,
                    importance=float(item.metadata.get("importance", 0.7)),
                )
            )
            item.applied = True
            return
        if item.kind == "skill_create":
            if not any(skill["name"] == item.target for skill in self.skills.list()):
                self.skills.create(item.target, item.content or f"Reusable workflow for {item.target}.")
            item.applied = True
            return
        if item.kind == "skill_reference":
            if not any(skill["name"] == item.target for skill in self.skills.list()):
                self.skills.create(item.target, f"Reusable workflow for {item.target}.")
            self.skills.write_file(
                item.target,
                str(item.metadata.get("file_path", f"references/{task_id}.md")),
                item.content,
            )
            item.applied = True
            return
        if item.kind == "skill_patch":
            self.skills.patch(
                item.target,
                str(item.metadata["old"]),
                item.content,
                str(item.metadata.get("file_path", "SKILL.md")),
            )
            item.applied = True
            return
        if item.kind == "skill_archive":
            self.skills.archive(item.target, item.content)
            item.applied = True

    @staticmethod
    def _refresh_status(proposal: LearningProposal) -> None:
        if not proposal.items:
            proposal.status = "blocked"
        elif all(item.applied or item.decision == "blocked" for item in proposal.items):
            proposal.status = "applied"
        elif any(item.applied for item in proposal.items):
            proposal.status = "partially_applied"
        elif all(item.decision == "blocked" for item in proposal.items):
            proposal.status = "blocked"
        else:
            proposal.status = "pending"
        proposal.touch()
