import os
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from core.database import get_db
from models.models import (
    Chart, Dataset, DatasetVersion, DatasetColumn, WorkspaceMember, Role
)
from schemas.schemas import (
    ChartCreate, ChartUpdate, ChartResponse, ChartQueryRequest, ChartDataResponse
)
from api.deps import get_current_user, get_current_workspace_member, require_role
from visualization.chart_compiler import ChartCompiler
import duckdb

router = APIRouter(tags=["Charts"])

@router.get("/workspaces/{workspace_id}/charts", response_model=List[ChartResponse])
async def list_charts(
    workspace_id: str,
    member: WorkspaceMember = Depends(get_current_workspace_member),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(Chart).where(Chart.workspace_id == workspace_id).order_by(desc(Chart.created_at))
    charts = (await db.execute(stmt)).scalars().all()
    return [ChartResponse.model_validate(c) for c in charts]

@router.post("/workspaces/{workspace_id}/charts", response_model=ChartResponse, status_code=status.HTTP_201_CREATED)
async def create_chart(
    workspace_id: str,
    chart_in: ChartCreate,
    member: WorkspaceMember = Depends(require_role([Role.OWNER, Role.ADMIN, Role.EDITOR])),
    db: AsyncSession = Depends(get_db)
):
    # Verify dataset exists in workspace
    ds_stmt = select(Dataset).where(Dataset.id == chart_in.dataset_id, Dataset.workspace_id == workspace_id)
    dataset = (await db.execute(ds_stmt)).scalar_one_or_none()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found in workspace")

    # Pick version
    version_id = chart_in.dataset_version_id
    if not version_id:
        v_stmt = select(DatasetVersion.id).where(
            DatasetVersion.dataset_id == dataset.id,
            DatasetVersion.is_active == True
        ).order_by(desc(DatasetVersion.version_number))
        version_id = (await db.execute(v_stmt)).scalars().first()

    chart = Chart(
        workspace_id=workspace_id,
        dataset_id=chart_in.dataset_id,
        dataset_version_id=version_id,
        created_by_id=member.user_id,
        name=chart_in.name,
        description=chart_in.description,
        chart_type=chart_in.chart_type,
        config=chart_in.config.model_dump()
    )
    db.add(chart)
    await db.commit()
    await db.refresh(chart)
    return ChartResponse.model_validate(chart)

@router.get("/charts/{chart_id}", response_model=ChartResponse)
async def get_chart(chart_id: str, db: AsyncSession = Depends(get_db)):
    chart = (await db.execute(select(Chart).where(Chart.id == chart_id))).scalar_one_or_none()
    if not chart:
        raise HTTPException(status_code=404, detail="Chart not found")
    return ChartResponse.model_validate(chart)

@router.put("/charts/{chart_id}", response_model=ChartResponse)
async def update_chart(
    chart_id: str,
    chart_in: ChartUpdate,
    db: AsyncSession = Depends(get_db)
):
    chart = (await db.execute(select(Chart).where(Chart.id == chart_id))).scalar_one_or_none()
    if not chart:
        raise HTTPException(status_code=404, detail="Chart not found")

    if chart_in.name is not None:
        chart.name = chart_in.name
    if chart_in.description is not None:
        chart.description = chart_in.description
    if chart_in.chart_type is not None:
        chart.chart_type = chart_in.chart_type
    if chart_in.config is not None:
        chart.config = chart_in.config.model_dump()

    await db.commit()
    await db.refresh(chart)
    return ChartResponse.model_validate(chart)

@router.post("/charts/{chart_id}/query", response_model=ChartDataResponse)
async def execute_chart_query(
    chart_id: str,
    query_req: Optional[ChartQueryRequest] = None,
    db: AsyncSession = Depends(get_db)
):
    chart = (await db.execute(select(Chart).where(Chart.id == chart_id))).scalar_one_or_none()
    if not chart:
        raise HTTPException(status_code=404, detail="Chart not found")

    # Fetch dataset version
    v_stmt = select(DatasetVersion).where(
        DatasetVersion.dataset_id == chart.dataset_id,
        DatasetVersion.is_active == True
    ).order_by(desc(DatasetVersion.version_number))
    version = (await db.execute(v_stmt)).scalars().first()
    if not version or not os.path.exists(version.file_path):
        raise HTTPException(status_code=404, detail="Dataset version file not found")

    # Fetch authorized columns
    c_stmt = select(DatasetColumn.name).where(DatasetColumn.dataset_version_id == version.id)
    allowed_cols = [c for c in (await db.execute(c_stmt)).scalars().all()]

    conn = duckdb.connect()
    try:
        clean_path = version.file_path.replace("\\", "/")
        view_name = "dataset_view"
        conn.execute(f"CREATE VIEW {view_name} AS SELECT * FROM parquet_scan('{clean_path}');")
        
        compiler = ChartCompiler(conn)
        global_filters = query_req.global_filters if query_req else None
        
        result = compiler.execute_chart_query(
            table_name=view_name,
            chart_type=chart.chart_type.value,
            config=chart.config,
            allowed_columns=allowed_cols,
            global_filters=global_filters
        )
    finally:
        conn.close()

    return ChartDataResponse(
        chart_id=chart.id,
        dataset_version_id=version.id,
        chart_type=chart.chart_type,
        data=result["data"],
        metadata=result["metadata"]
    )

@router.delete("/charts/{chart_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_chart(chart_id: str, db: AsyncSession = Depends(get_db)):
    chart = (await db.execute(select(Chart).where(Chart.id == chart_id))).scalar_one_or_none()
    if not chart:
        raise HTTPException(status_code=404, detail="Chart not found")
    await db.delete(chart)
    await db.commit()
    return None
