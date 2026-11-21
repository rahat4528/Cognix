import os
import io
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from core.database import get_db
from core.config import settings
from models.models import (
    Workspace, WorkspaceMember, Dataset, DatasetVersion, DatasetColumn, Role, SourceType
)
from schemas.schemas import (
    DatasetResponse, DatasetVersionResponse, DatasetColumnResponse, DataPreviewResponse
)
from api.deps import get_current_user, get_current_workspace_member, require_role
from data_processing.ingestion import read_file_to_dataframe, save_dataframe_as_parquet, compute_sha256
from data_processing.profiling import profile_dataframe
import pandas as pd
import duckdb

router = APIRouter(tags=["Datasets"])

@router.get("/workspaces/{workspace_id}/datasets", response_model=List[DatasetResponse])
async def list_datasets(
    workspace_id: str,
    member: WorkspaceMember = Depends(get_current_workspace_member),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(Dataset).where(Dataset.workspace_id == workspace_id).order_by(desc(Dataset.created_at))
    result = await db.execute(stmt)
    datasets = result.scalars().all()

    response_list = []
    for ds in datasets:
        # Get latest active version
        v_stmt = select(DatasetVersion).where(
            DatasetVersion.dataset_id == ds.id,
            DatasetVersion.is_active == True
        ).order_by(desc(DatasetVersion.version_number))
        latest_ver = (await db.execute(v_stmt)).scalars().first()
        
        ds_resp = DatasetResponse.model_validate(ds)
        if latest_ver:
            ds_resp.latest_version = DatasetVersionResponse.model_validate(latest_ver)
        response_list.append(ds_resp)

    return response_list

@router.post("/workspaces/{workspace_id}/datasets/upload", response_model=DatasetResponse, status_code=status.HTTP_201_CREATED)
async def upload_dataset(
    workspace_id: str,
    file: UploadFile = File(...),
    name: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    member: WorkspaceMember = Depends(require_role([Role.OWNER, Role.ADMIN, Role.EDITOR])),
    db: AsyncSession = Depends(get_db)
):
    contents = await file.read()
    if len(contents) > settings.MAX_UPLOAD_SIZE_BYTES:
        raise HTTPException(status_code=413, detail=f"File exceeds maximum upload size of {settings.MAX_UPLOAD_SIZE_BYTES // (1024*1024)}MB")

    try:
        df, detected_format = read_file_to_dataframe(contents, file.filename)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to parse uploaded dataset: {str(e)}")

    if df.empty:
        raise HTTPException(status_code=400, detail="Uploaded dataset contains zero rows.")

    dataset_name = name or os.path.splitext(file.filename)[0]
    checksum = compute_sha256(contents)

    # Create Dataset record
    dataset = Dataset(
        workspace_id=workspace_id,
        created_by_id=member.user_id,
        name=dataset_name,
        description=description,
        source_type=SourceType.FILE
    )
    db.add(dataset)
    await db.flush()

    # Profile DataFrame
    columns_profile, quality_report, quality_score = profile_dataframe(df)

    # Save to Parquet
    version_id = f"ds_{dataset.id[:8]}_v1"
    parquet_path, file_size = save_dataframe_as_parquet(df, settings.STORAGE_LOCAL_PATH, version_id)

    # Create DatasetVersion record
    version = DatasetVersion(
        id=version_id,
        dataset_id=dataset.id,
        version_number=1,
        file_path=parquet_path,
        original_filename=file.filename,
        file_format=detected_format,
        file_size_bytes=file_size,
        row_count=len(df),
        column_count=len(df.columns),
        checksum_sha256=checksum,
        quality_score=quality_score,
        quality_report=quality_report,
        created_by_id=member.user_id
    )
    db.add(version)
    await db.flush()

    # Create DatasetColumn records
    for cp in columns_profile:
        col = DatasetColumn(
            dataset_version_id=version.id,
            name=cp["name"],
            data_type=cp["data_type"],
            is_nullable=cp["is_nullable"],
            null_count=cp["null_count"],
            null_percentage=cp["null_percentage"],
            unique_count=cp["unique_count"],
            sample_values=cp["sample_values"],
            statistics=cp["statistics"]
        )
        db.add(col)

    await db.commit()
    await db.refresh(dataset)
    await db.refresh(version)

    resp = DatasetResponse.model_validate(dataset)
    resp.latest_version = DatasetVersionResponse.model_validate(version)
    return resp

@router.get("/datasets/{dataset_id}", response_model=DatasetResponse)
async def get_dataset(dataset_id: str, db: AsyncSession = Depends(get_db)):
    dataset = (await db.execute(select(Dataset).where(Dataset.id == dataset_id))).scalar_one_or_none()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")

    v_stmt = select(DatasetVersion).where(
        DatasetVersion.dataset_id == dataset.id,
        DatasetVersion.is_active == True
    ).order_by(desc(DatasetVersion.version_number))
    latest_ver = (await db.execute(v_stmt)).scalars().first()

    columns = []
    if latest_ver:
        c_stmt = select(DatasetColumn).where(DatasetColumn.dataset_version_id == latest_ver.id)
        columns = (await db.execute(c_stmt)).scalars().all()

    resp = DatasetResponse.model_validate(dataset)
    if latest_ver:
        resp.latest_version = DatasetVersionResponse.model_validate(latest_ver)
        resp.columns = [DatasetColumnResponse.model_validate(c) for c in columns]
    return resp

@router.get("/datasets/{dataset_id}/preview", response_model=DataPreviewResponse)
async def preview_dataset(
    dataset_id: str,
    version_id: Optional[str] = None,
    page: int = 1,
    page_size: int = 50,
    db: AsyncSession = Depends(get_db)
):
    if version_id:
        v_stmt = select(DatasetVersion).where(DatasetVersion.id == version_id)
    else:
        v_stmt = select(DatasetVersion).where(
            DatasetVersion.dataset_id == dataset_id,
            DatasetVersion.is_active == True
        ).order_by(desc(DatasetVersion.version_number))
    
    version = (await db.execute(v_stmt)).scalars().first()
    if not version or not os.path.exists(version.file_path):
        raise HTTPException(status_code=404, detail="Dataset version or file not found")

    conn = duckdb.connect()
    try:
        offset = (page - 1) * page_size
        clean_path = version.file_path.replace("\\", "/")
        query = f"SELECT * FROM parquet_scan('{clean_path}') LIMIT {page_size} OFFSET {offset}"
        df = conn.execute(query).df()
        
        # Replace NaNs for JSON safety
        clean_df = df.replace({float('nan'): None, float('inf'): None, float('-inf'): None})
        rows = clean_df.to_dict(orient="records")
        columns = list(df.columns)
    finally:
        conn.close()

    return DataPreviewResponse(
        columns=columns,
        rows=rows,
        total_rows=version.row_count,
        page=page,
        page_size=page_size
    )

@router.delete("/datasets/{dataset_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_dataset(dataset_id: str, db: AsyncSession = Depends(get_db)):
    dataset = (await db.execute(select(Dataset).where(Dataset.id == dataset_id))).scalar_one_or_none()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    
    # Remove files
    v_stmt = select(DatasetVersion).where(DatasetVersion.dataset_id == dataset_id)
    versions = (await db.execute(v_stmt)).scalars().all()
    for v in versions:
        if os.path.exists(v.file_path):
            try:
                os.remove(v.file_path)
            except OSError:
                pass

    await db.delete(dataset)
    await db.commit()
    return None
