from __future__ import annotations

from fastapi import APIRouter, Request
from pydantic import BaseModel

router = APIRouter(prefix="/api/skills", tags=["skills"])


class SkillCreateRequest(BaseModel):
    name: str
    description: str
    content: str | None = None


class SkillPatchRequest(BaseModel):
    old: str
    new: str
    file_path: str = "SKILL.md"


@router.get("")
async def list_skills(request: Request):
    return request.app.state.skills.list()


@router.get("/{name}")
async def view_skill(request: Request, name: str):
    return request.app.state.skills.view(name)


@router.post("")
async def create_skill(request: Request, payload: SkillCreateRequest):
    return request.app.state.skills.create(payload.name, payload.description, payload.content)


@router.post("/{name}/patch")
async def patch_skill(request: Request, name: str, payload: SkillPatchRequest):
    return request.app.state.skills.patch(name, payload.old, payload.new, payload.file_path)


@router.post("/curator/run")
async def run_curator(request: Request, dry_run: bool = True):
    return request.app.state.curator.run_once(dry_run=dry_run)
