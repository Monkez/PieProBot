from __future__ import annotations

from typing import Any

from app.learning.applier import LearningApplier
from app.learning.policy import LearningPolicy
from app.learning.reviewer import LearningReviewer


class BackgroundReview:
    """Post-turn learning pass with proactive proposals and safe application."""

    def __init__(self, memory, skills, state_store=None) -> None:
        self.state_store = state_store
        self.reviewer = LearningReviewer()
        self.policy = LearningPolicy()
        self.applier = LearningApplier(memory=memory, skills=skills)

    async def review_task(self, task) -> dict[str, Any]:
        proposal = self.reviewer.propose(task)
        if not proposal.items:
            return {"actions": [], "proposal_id": proposal.id, "status": proposal.status}

        proposal = self.policy.classify(proposal)
        proposal = await self.applier.apply_safe(proposal)
        if self.state_store:
            self.state_store.save_learning_proposal(proposal)

        applied = [f"{item.kind}:{item.target}" for item in proposal.items if item.applied]
        review = [
            f"{item.kind}:{item.target}"
            for item in proposal.items
            if item.decision == "review" and not item.applied
        ]
        blocked = [f"{item.kind}:{item.target}" for item in proposal.items if item.decision == "blocked"]
        return {
            "actions": applied,
            "review": review,
            "blocked": blocked,
            "proposal_id": proposal.id,
            "status": proposal.status,
        }
