import os
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from core.database import get_db
from core.config import settings
from models.models import (
    Dataset, DatasetVersion, DatasetColumn, DataTransformation, Role
)
from schemas.schemas import (
    TransformationPreviewRequest, TransformationApplyRequest,
    TransformationResponse, DatasetVersionResponse, DataPreviewResponse
)
from api.deps import get_current_user, require_role
from data_processing.transformations import execute_pipeline
from data_processing.profiling import profile_dataframe
from data_processing.ingestion import save_dataframe_as_parquet, compute_sha256
import pandas as pd

router = APIRouter(prefix="/datasets", tags=["Transformations"])

@router.post("/{dataset_id}/transform/preview", response_model=DataPreviewResponse)
async def preview_transformation(
    dataset_id: str,
    request: TransformationPreviewRequest,
    db: AsyncSession = Depends(get_db)
):
    v_stmt = select(DatasetVersion).where(
        DatasetVersion.dataset_id == dataset_id,
        DatasetVersion.is_active == True
    ).order_by(desc(DatasetVersion.version_number))
    version = (await db.execute(v_stmt)).scalars().first()
    if not version or not os.path.exists(version.file_path):
        raise HTTPException(status_code=404, detail="Dataset version not found")

    try:
        df_sample = pd.read_parquet(version.file_path).head(request.sample_size)
        steps_dict = [s.model_dump() for s in request.steps]
        transformed_df = execute_pipeline(df_sample, steps_dict)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Transformation preview failed: {str(e)}")

    clean_df = transformed_df.replace({float('nan'): None, float('inf'): None, float('-inf'): None})
    return DataPreviewResponse(
        columns=list(clean_df.columns),
        rows=clean_df.to_dict(orient="records"),
        total_rows=len(clean_df),
        page=1,
        page_size=request.sample_size
    )

@router.post("/{dataset_id}/transform/apply", response_model=TransformationResponse)
async def apply_transformation(
    dataset_id: str,
    request: TransformationApplyRequest,
    user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    v_stmt = select(DatasetVersion).where(
        DatasetVersion.dataset_id == dataset_id,
        DatasetVersion.is_active == True
    ).order_by(desc(DatasetVersion.version_number))
    source_ver = (await db.execute(v_stmt)).scalars().first()
    if not source_ver or not os.path.exists(source_ver.file_path):
        raise HTTPException(status_code=404, detail="Source dataset version not found")

    try:
        df = pd.read_parquet(source_ver.file_path)
        steps_dict = [s.model_dump() for s in request.steps]
        transformed_df = execute_pipeline(df, steps_dict)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Transformation execution failed: {str(e)}")

    if transformed_df.empty:
        raise HTTPException(status_code=400, detail="Transformation resulted in 0 rows.")

    new_version_num = source_ver.version_number + 1
    new_version_id = f"ds_{dataset_id[:8]}_v{new_version_num}"
    
    # Save transformed dataframe as new Parquet file (original remains untouched!)
    parquet_path, file_size = save_dataframe_as_parquet(transformed_df, settings.STORAGE_LOCAL_PATH, new_version_id)
    with open(parquet_path, "rb") as f:
        checksum = compute_sha256(f.read())

    # Profile new dataset
    columns_profile, quality_report, quality_score = profile_dataframe(transformed_df)

    new_version = DatasetVersion(
        id=new_version_id,
        dataset_id=dataset_id,
        version_number=new_version_num,
        file_path=parquet_path,
        original_filename=f"{source_ver.original_filename}_v{new_version_num}.parquet",
        file_format="parquet",
        file_size_bytes=file_size,
        row_count=len(transformed_df),
        column_count=len(transformed_df.columns),
        checksum_sha256=checksum,
        quality_score=quality_score,
        quality_report=quality_report,
        created_by_id=user.id
    )
    db.add(new_version)
    await db.flush()

    for cp in columns_profile:
        col = DatasetColumn(
            dataset_version_id=new_version.id,
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

    # Record transformation lineage
    transform_record = DataTransformation(
        dataset_id=dataset_id,
        source_version_id=source_ver.id,
        target_version_id=new_version.id,
        pipeline_spec=steps_dict,
        created_by_id=user.id
    )
    db.add(transform_record)

    await db.commit()
    await db.refresh(new_version)

    return TransformationResponse(
        transformation_id=transform_record.id,
        new_version=DatasetVersionResponse.model_validate(new_version),
        steps_applied=len(steps_dict)
    )
