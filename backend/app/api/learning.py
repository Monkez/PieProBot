from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request

from app.learning.applier import LearningApplier
from app.learning.models import LearningProposal

router = APIRouter(prefix="/api/learning", tags=["learning"])


@router.get("/proposals")
async def list_learning_proposals(request: Request, status: str | None = None):
    return request.app.state.state_store.list_learning_proposals(status=status)


@router.get("/proposals/{proposal_id}")
async def get_learning_proposal(request: Request, proposal_id: str):
    proposal = request.app.state.state_store.get_learning_proposal(proposal_id)
    if not proposal:
        raise HTTPException(status_code=404, detail="Learning proposal not found")
    return proposal


@router.post("/proposals/{proposal_id}/approve")
async def approve_learning_proposal(request: Request, proposal_id: str):
    data = request.app.state.state_store.get_learning_proposal(proposal_id)
    if not data:
        raise HTTPException(status_code=404, detail="Learning proposal not found")
    proposal = LearningProposal.model_validate(data)
    if proposal.status == "rejected":
        raise HTTPException(status_code=409, detail="Rejected proposals cannot be approved")

    applier = LearningApplier(memory=request.app.state.memory, skills=request.app.state.skills)
    proposal = await applier.apply_all_review_items(proposal)
    request.app.state.state_store.save_learning_proposal(proposal)
    return proposal.model_dump(mode="json")


@router.post("/proposals/{proposal_id}/reject")
async def reject_learning_proposal(request: Request, proposal_id: str):
    data = request.app.state.state_store.get_learning_proposal(proposal_id)
    if not data:
        raise HTTPException(status_code=404, detail="Learning proposal not found")
    proposal = LearningProposal.model_validate(data)
    for item in proposal.items:
        if item.decision == "review" and not item.applied:
            item.reason = item.reason or "rejected by operator"
    proposal.status = "rejected"
    proposal.touch()
    request.app.state.state_store.save_learning_proposal(proposal)
    return proposal.model_dump(mode="json")
