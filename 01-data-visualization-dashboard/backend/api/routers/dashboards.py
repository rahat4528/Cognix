import secrets
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from core.database import get_db
from models.models import (
    Dashboard, DashboardChart, Chart, ShareLink, WorkspaceMember, Role
)
from schemas.schemas import (
    DashboardCreate, DashboardUpdate, DashboardResponse,
    ShareLinkCreate, ShareLinkResponse
)
from api.deps import get_current_user, get_current_workspace_member, require_role

router = APIRouter(tags=["Dashboards"])

@router.get("/workspaces/{workspace_id}/dashboards", response_model=List[DashboardResponse])
async def list_dashboards(
    workspace_id: str,
    member: WorkspaceMember = Depends(get_current_workspace_member),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(Dashboard).where(Dashboard.workspace_id == workspace_id).order_by(desc(Dashboard.created_at))
    dashboards = (await db.execute(stmt)).scalars().all()

    resp_list = []
    for d in dashboards:
        dc_stmt = select(DashboardChart, Chart).join(Chart, DashboardChart.chart_id == Chart.id).where(DashboardChart.dashboard_id == d.id)
        dc_rows = (await db.execute(dc_stmt)).all()
        
        charts_layout = []
        for dc, ch in dc_rows:
            charts_layout.append({
                "chart_id": ch.id,
                "chart_name": ch.name,
                "chart_type": ch.chart_type.value,
                "config": ch.config,
                "position_x": dc.position_x,
                "position_y": dc.position_y,
                "width": dc.width,
                "height": dc.height
            })
        
        d_resp = DashboardResponse(
            id=d.id,
            workspace_id=d.workspace_id,
            title=d.title,
            description=d.description,
            version=d.version,
            is_public=d.is_public,
            global_filters=d.global_filters or [],
            charts=charts_layout,
            created_at=d.created_at,
            updated_at=d.updated_at
        )
        resp_list.append(d_resp)

    return resp_list

@router.post("/workspaces/{workspace_id}/dashboards", response_model=DashboardResponse, status_code=status.HTTP_201_CREATED)
async def create_dashboard(
    workspace_id: str,
    dash_in: DashboardCreate,
    member: WorkspaceMember = Depends(require_role([Role.OWNER, Role.ADMIN, Role.EDITOR])),
    db: AsyncSession = Depends(get_db)
):
    dashboard = Dashboard(
        workspace_id=workspace_id,
        created_by_id=member.user_id,
        title=dash_in.title,
        description=dash_in.description,
        global_filters=dash_in.global_filters or [],
        version=1
    )
    db.add(dashboard)
    await db.flush()

    if dash_in.charts:
        for idx, item in enumerate(dash_in.charts):
            dc = DashboardChart(
                dashboard_id=dashboard.id,
                chart_id=item.chart_id,
                position_x=item.position_x,
                position_y=item.position_y,
                width=item.width,
                height=item.height,
                overrides=item.overrides
            )
            db.add(dc)

    await db.commit()
    await db.refresh(dashboard)

    return DashboardResponse(
        id=dashboard.id,
        workspace_id=dashboard.workspace_id,
        title=dashboard.title,
        description=dashboard.description,
        version=dashboard.version,
        is_public=dashboard.is_public,
        global_filters=dashboard.global_filters or [],
        charts=[c.model_dump() for c in (dash_in.charts or [])],
        created_at=dashboard.created_at,
        updated_at=dashboard.updated_at
    )

@router.get("/dashboards/{dashboard_id}", response_model=DashboardResponse)
async def get_dashboard(dashboard_id: str, db: AsyncSession = Depends(get_db)):
    dashboard = (await db.execute(select(Dashboard).where(Dashboard.id == dashboard_id))).scalar_one_or_none()
    if not dashboard:
        raise HTTPException(status_code=404, detail="Dashboard not found")

    dc_stmt = select(DashboardChart, Chart).join(Chart, DashboardChart.chart_id == Chart.id).where(DashboardChart.dashboard_id == dashboard.id)
    dc_rows = (await db.execute(dc_stmt)).all()
    
    charts_layout = []
    for dc, ch in dc_rows:
        charts_layout.append({
            "chart_id": ch.id,
            "chart_name": ch.name,
            "chart_type": ch.chart_type.value,
            "config": ch.config,
            "position_x": dc.position_x,
            "position_y": dc.position_y,
            "width": dc.width,
            "height": dc.height
        })

    return DashboardResponse(
        id=dashboard.id,
        workspace_id=dashboard.workspace_id,
        title=dashboard.title,
        description=dashboard.description,
        version=dashboard.version,
        is_public=dashboard.is_public,
        global_filters=dashboard.global_filters or [],
        charts=charts_layout,
        created_at=dashboard.created_at,
        updated_at=dashboard.updated_at
    )

@router.put("/dashboards/{dashboard_id}", response_model=DashboardResponse)
async def update_dashboard(
    dashboard_id: str,
    dash_in: DashboardUpdate,
    db: AsyncSession = Depends(get_db)
):
    dashboard = (await db.execute(select(Dashboard).where(Dashboard.id == dashboard_id))).scalar_one_or_none()
    if not dashboard:
        raise HTTPException(status_code=404, detail="Dashboard not found")

    # Optimistic Concurrency Control
    if dashboard.version != dash_in.version:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Dashboard has been modified by another user (expected version {dashboard.version}, received {dash_in.version}). Please reload."
        )

    if dash_in.title is not None:
        dashboard.title = dash_in.title
    if dash_in.description is not None:
        dashboard.description = dash_in.description
    if dash_in.global_filters is not None:
        dashboard.global_filters = dash_in.global_filters

    dashboard.version += 1

    # Update charts layout if provided
    if dash_in.charts is not None:
        # Clear existing mappings
        del_stmt = select(DashboardChart).where(DashboardChart.dashboard_id == dashboard.id)
        existing_dcs = (await db.execute(del_stmt)).scalars().all()
        for edc in existing_dcs:
            await db.delete(edc)
        await db.flush()

        for item in dash_in.charts:
            dc = DashboardChart(
                dashboard_id=dashboard.id,
                chart_id=item.chart_id,
                position_x=item.position_x,
                position_y=item.position_y,
                width=item.width,
                height=item.height,
                overrides=item.overrides
            )
            db.add(dc)

    await db.commit()
    await db.refresh(dashboard)

    return await get_dashboard(dashboard.id, db)

@router.post("/dashboards/{dashboard_id}/share", response_model=ShareLinkResponse)
async def generate_share_link(
    dashboard_id: str,
    share_in: ShareLinkCreate,
    user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    dashboard = (await db.execute(select(Dashboard).where(Dashboard.id == dashboard_id))).scalar_one_or_none()
    if not dashboard:
        raise HTTPException(status_code=404, detail="Dashboard not found")

    token = secrets.token_urlsafe(32)
    share = ShareLink(
        dashboard_id=dashboard_id,
        token=token,
        allow_export=share_in.allow_export,
        is_active=True
    )
    db.add(share)
    await db.commit()

    return ShareLinkResponse(
        token=token,
        share_url=f"/public/dashboards/{token}",
        allow_export=share.allow_export,
        is_active=True
    )

@router.get("/public/dashboards/{token}")
async def get_public_dashboard(token: str, db: AsyncSession = Depends(get_db)):
    share = (await db.execute(select(ShareLink).where(ShareLink.token == token, ShareLink.is_active == True))).scalar_one_or_none()
    if not share:
        raise HTTPException(status_code=404, detail="Public dashboard link invalid or expired")

    share.access_count += 1
    await db.commit()

    return await get_dashboard(share.dashboard_id, db)
