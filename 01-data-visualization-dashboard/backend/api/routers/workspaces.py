import re
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from core.database import get_db
from models.models import Workspace, WorkspaceMember, User, Role
from schemas.schemas import (
    WorkspaceCreate, WorkspaceUpdate, WorkspaceResponse,
    WorkspaceMemberAdd, WorkspaceMemberResponse
)
from api.deps import get_current_user, get_current_workspace_member, require_role

router = APIRouter(prefix="/workspaces", tags=["Workspaces"])

@router.get("", response_model=List[WorkspaceResponse])
async def list_workspaces(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    stmt = select(Workspace, WorkspaceMember.role).join(
        WorkspaceMember, Workspace.id == WorkspaceMember.workspace_id
    ).where(WorkspaceMember.user_id == user.id)
    result = await db.execute(stmt)
    
    workspaces = []
    for ws, role in result.all():
        resp = WorkspaceResponse.model_validate(ws)
        resp.role = role
        workspaces.append(resp)
    return workspaces

@router.post("", response_model=WorkspaceResponse, status_code=status.HTTP_201_CREATED)
async def create_workspace(
    ws_in: WorkspaceCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    slug = ws_in.slug or re.sub(r'[^a-zA-Z0-9-]', '-', ws_in.name.lower()).strip('-')
    
    # Check uniqueness of slug
    existing = (await db.execute(select(Workspace).where(Workspace.slug == slug))).scalar_one_or_none()
    if existing:
        slug = f"{slug}-{user.id[:8]}"

    workspace = Workspace(
        name=ws_in.name,
        slug=slug,
        description=ws_in.description,
        owner_id=user.id
    )
    db.add(workspace)
    await db.flush()

    member = WorkspaceMember(
        workspace_id=workspace.id,
        user_id=user.id,
        role=Role.OWNER
    )
    db.add(member)
    await db.commit()
    await db.refresh(workspace)

    resp = WorkspaceResponse.model_validate(workspace)
    resp.role = Role.OWNER
    return resp

@router.get("/{workspace_id}/members", response_model=List[WorkspaceMemberResponse])
async def list_workspace_members(
    workspace_id: str,
    member: WorkspaceMember = Depends(get_current_workspace_member),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(WorkspaceMember, User.full_name, User.email).join(
        User, WorkspaceMember.user_id == User.id
    ).where(WorkspaceMember.workspace_id == workspace_id)
    result = await db.execute(stmt)
    
    members = []
    for wm, name, email in result.all():
        m_resp = WorkspaceMemberResponse.model_validate(wm)
        m_resp.user_name = name
        m_resp.user_email = email
        members.append(m_resp)
    return members

@router.post("/{workspace_id}/members", response_model=WorkspaceMemberResponse)
async def add_workspace_member(
    workspace_id: str,
    member_in: WorkspaceMemberAdd,
    current_member: WorkspaceMember = Depends(require_role([Role.OWNER, Role.ADMIN])),
    db: AsyncSession = Depends(get_db)
):
    target_user = (await db.execute(select(User).where(User.email == member_in.email))).scalar_one_or_none()
    if not target_user:
        raise HTTPException(status_code=404, detail="User with specified email not found")

    existing = (await db.execute(
        select(WorkspaceMember).where(
            WorkspaceMember.workspace_id == workspace_id,
            WorkspaceMember.user_id == target_user.id
        )
    )).scalar_one_or_none()

    if existing:
        existing.role = member_in.role
        await db.commit()
        await db.refresh(existing)
        resp = WorkspaceMemberResponse.model_validate(existing)
        resp.user_name = target_user.full_name
        resp.user_email = target_user.email
        return resp

    new_member = WorkspaceMember(
        workspace_id=workspace_id,
        user_id=target_user.id,
        role=member_in.role
    )
    db.add(new_member)
    await db.commit()
    await db.refresh(new_member)
    resp = WorkspaceMemberResponse.model_validate(new_member)
    resp.user_name = target_user.full_name
    resp.user_email = target_user.email
    return resp
