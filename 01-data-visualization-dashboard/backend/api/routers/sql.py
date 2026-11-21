import os
import re
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from core.database import get_db
from core.config import settings
from models.models import (
    SavedQuery, QueryExecution, Dataset, DatasetVersion, WorkspaceMember, Role
)
from schemas.schemas import (
    SQLExecuteRequest, SQLExecuteResponse, SavedQueryCreate, SavedQueryResponse
)
from api.deps import get_current_user, get_current_workspace_member, require_role
from sql_sandbox.engine import (
    create_sandboxed_duckdb_connection, execute_sandboxed_query, SQLSandboxSecurityError
)

router = APIRouter(tags=["SQL Studio"])

@router.post("/workspaces/{workspace_id}/sql/execute", response_model=SQLExecuteResponse)
async def execute_sql(
    workspace_id: str,
    req: SQLExecuteRequest,
    member: WorkspaceMember = Depends(get_current_workspace_member),
    db: AsyncSession = Depends(get_db)
):
    # Fetch active datasets in this workspace
    ds_stmt = select(Dataset).where(Dataset.workspace_id == workspace_id)
    datasets = (await db.execute(ds_stmt)).scalars().all()
    
    conn = create_sandboxed_duckdb_connection()
    registered_views = []
    
    try:
        # Register each authorized dataset's latest version as a view
        for ds in datasets:
            v_stmt = select(DatasetVersion).where(
                DatasetVersion.dataset_id == ds.id,
                DatasetVersion.is_active == True
            ).order_by(desc(DatasetVersion.version_number))
            version = (await db.execute(v_stmt)).scalars().first()
            if version and os.path.exists(version.file_path):
                clean_path = version.file_path.replace("\\", "/")
                # Sanitize view name: e.g. "ds_sales_data"
                san_name = "ds_" + re.sub(r'[^a-zA-Z0-9_]', '_', ds.name.lower()).strip('_')
                conn.execute(f"CREATE VIEW {san_name} AS SELECT * FROM parquet_scan('{clean_path}');")
                registered_views.append(san_name)

        columns, rows, duration_ms = execute_sandboxed_query(
            conn=conn,
            sql_text=req.sql_text,
            timeout_seconds=settings.SQL_QUERY_TIMEOUT_SECONDS,
            max_rows=settings.SQL_MAX_RESULT_ROWS
        )

        # Log execution
        exec_log = QueryExecution(
            workspace_id=workspace_id,
            user_id=member.user_id,
            sql_text=req.sql_text,
            duration_ms=duration_ms,
            row_count=len(rows),
            status="SUCCESS"
        )
        db.add(exec_log)
        await db.commit()

        return SQLExecuteResponse(
            columns=columns,
            rows=rows,
            row_count=len(rows),
            duration_ms=duration_ms
        )

    except SQLSandboxSecurityError as sec_err:
        raise HTTPException(status_code=400, detail=f"SQL Security Violation: {str(sec_err)}")
    except Exception as e:
        # Log failed execution
        exec_log = QueryExecution(
            workspace_id=workspace_id,
            user_id=member.user_id,
            sql_text=req.sql_text,
            duration_ms=0.0,
            row_count=0,
            status="FAILED",
            error_message=str(e)
        )
        db.add(exec_log)
        await db.commit()
        raise HTTPException(status_code=400, detail=f"Query Execution Error: {str(e)}")
    finally:
        conn.close()

@router.get("/workspaces/{workspace_id}/sql/saved", response_model=List[SavedQueryResponse])
async def list_saved_queries(
    workspace_id: str,
    member: WorkspaceMember = Depends(get_current_workspace_member),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(SavedQuery).where(SavedQuery.workspace_id == workspace_id).order_by(desc(SavedQuery.created_at))
    queries = (await db.execute(stmt)).scalars().all()
    return [SavedQueryResponse.model_validate(q) for q in queries]

@router.post("/workspaces/{workspace_id}/sql/saved", response_model=SavedQueryResponse, status_code=status.HTTP_201_CREATED)
async def create_saved_query(
    workspace_id: str,
    query_in: SavedQueryCreate,
    member: WorkspaceMember = Depends(require_role([Role.OWNER, Role.ADMIN, Role.EDITOR])),
    db: AsyncSession = Depends(get_db)
):
    saved = SavedQuery(
        workspace_id=workspace_id,
        created_by_id=member.user_id,
        name=query_in.name,
        description=query_in.description,
        sql_text=query_in.sql_text
    )
    db.add(saved)
    await db.commit()
    await db.refresh(saved)
    return SavedQueryResponse.model_validate(saved)
