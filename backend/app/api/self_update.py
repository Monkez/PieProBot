from __future__ import annotations

from fastapi import APIRouter, Request
from pydantic import BaseModel

router = APIRouter(prefix="/api/self-update", tags=["self-update"])


class PlanRequest(BaseModel):
    goal: str
    files_to_change: list[str] = []


class CandidateRequest(BaseModel):
    plan_id: str


class CandidateIdRequest(BaseModel):
    candidate_id: str


class PatchRequest(CandidateIdRequest):
    patch_text: str


@router.post("/plan")
async def create_plan(request: Request, payload: PlanRequest):
    return (await request.app.state.self_update.create_update_plan(payload.goal, payload.files_to_change)).model_dump(mode="json")


@router.get("/detect")
async def detect_update_need(request: Request):
    return await request.app.state.self_update.detect_update_need()


@router.post("/create-candidate")
async def create_candidate(request: Request, payload: CandidateRequest):
    return (await request.app.state.self_update.create_candidate_copy(payload.plan_id)).model_dump(mode="json")


@router.post("/apply")
async def apply_patch(request: Request, payload: PatchRequest):
    return (await request.app.state.self_update.apply_patch_to_candidate(payload.candidate_id, payload.patch_text)).model_dump(mode="json")


@router.post("/test")
async def test_candidate(request: Request, payload: CandidateIdRequest):
    return await request.app.state.self_update.run_candidate_tests(payload.candidate_id)


@router.post("/start-candidate")
async def start_candidate(request: Request, payload: CandidateIdRequest):
    return await request.app.state.self_update.start_candidate(payload.candidate_id)


@router.post("/healthcheck")
async def healthcheck_candidate(request: Request, payload: CandidateIdRequest):
    return await request.app.state.self_update.run_candidate_healthcheck(payload.candidate_id)


@router.post("/promote")
async def promote_candidate(request: Request, payload: CandidateIdRequest):
    return await request.app.state.self_update.promote_candidate(payload.candidate_id)


@router.post("/rollback")
async def rollback_candidate(request: Request, payload: CandidateIdRequest):
    return await request.app.state.self_update.rollback_candidate(payload.candidate_id)


@router.post("/destroy")
async def destroy_candidate(request: Request, payload: CandidateIdRequest):
    return await request.app.state.self_update.destroy_failed_candidate(payload.candidate_id)


@router.post("/report")
async def write_report(request: Request, payload: CandidateIdRequest):
    return await request.app.state.self_update.write_update_report(payload.candidate_id)


@router.get("/status")
async def update_status(request: Request):
    return request.app.state.self_update.status()


@router.get("/history")
async def update_history(request: Request):
    return request.app.state.self_update.history
