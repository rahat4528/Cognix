from datetime import datetime
from typing import Optional, List, Dict, Any, Union
from pydantic import BaseModel, ConfigDict, Field
from models.models import Role, SourceType, ChartType

# ----------------- User & Auth Schemas -----------------
class UserBase(BaseModel):
    email: str = Field(..., pattern=r"^[^@]+@[^@]+\.[^@]+$")
    full_name: str

class UserCreate(UserBase):
    password: str = Field(..., min_length=8)

class UserLogin(BaseModel):
    email: str = Field(..., pattern=r"^[^@]+@[^@]+\.[^@]+$")
    password: str

class UserResponse(UserBase):
    model_config = ConfigDict(from_attributes=True)
    id: str
    is_active: bool
    is_superuser: bool
    created_at: datetime

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserResponse

# ----------------- Workspace Schemas -----------------
class WorkspaceBase(BaseModel):
    name: str
    description: Optional[str] = None

class WorkspaceCreate(WorkspaceBase):
    slug: Optional[str] = None

class WorkspaceUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None

class WorkspaceMemberAdd(BaseModel):
    email: str = Field(..., pattern=r"^[^@]+@[^@]+\.[^@]+$")
    role: Role = Role.EDITOR

class WorkspaceMemberResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    workspace_id: str
    user_id: str
    role: Role
    user_name: Optional[str] = None
    user_email: Optional[str] = None
    created_at: datetime

class WorkspaceResponse(WorkspaceBase):
    model_config = ConfigDict(from_attributes=True)
    id: str
    slug: str
    owner_id: str
    created_at: datetime
    role: Optional[Role] = None

# ----------------- Dataset & Profiling Schemas -----------------
class DatasetColumnResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    name: str
    data_type: str
    is_nullable: bool
    null_count: int
    null_percentage: float
    unique_count: int
    sample_values: Optional[List[Any]] = None
    statistics: Optional[Dict[str, Any]] = None

class DatasetVersionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    version_number: int
    original_filename: str
    file_format: str
    file_size_bytes: int
    row_count: int
    column_count: int
    checksum_sha256: str
    quality_score: Optional[float] = None
    quality_report: Optional[Dict[str, Any]] = None
    created_at: datetime

class DatasetResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    workspace_id: str
    name: str
    description: Optional[str] = None
    source_type: SourceType
    created_at: datetime
    updated_at: datetime
    latest_version: Optional[DatasetVersionResponse] = None
    columns: Optional[List[DatasetColumnResponse]] = None

class DataPreviewResponse(BaseModel):
    columns: List[str]
    rows: List[Dict[str, Any]]
    total_rows: int
    page: int
    page_size: int

# ----------------- Transformation Schemas -----------------
class TransformationStep(BaseModel):
    op: str
    params: Dict[str, Any]

class TransformationPreviewRequest(BaseModel):
    steps: List[TransformationStep]
    sample_size: int = 100

class TransformationApplyRequest(BaseModel):
    steps: List[TransformationStep]
    description: Optional[str] = None

class TransformationResponse(BaseModel):
    transformation_id: str
    new_version: DatasetVersionResponse
    steps_applied: int

# ----------------- Chart Schemas -----------------
class ChartConfig(BaseModel):
    x_axis: Optional[str] = None
    y_axis: Optional[str] = None
    series: Optional[str] = None
    aggregation: Optional[str] = "sum"
    group_by: Optional[List[str]] = None
    filters: Optional[List[Dict[str, Any]]] = None
    sort_by: Optional[str] = None
    sort_order: Optional[str] = "asc"
    limit: Optional[int] = 1000
    color_palette: Optional[str] = "default"
    display_options: Optional[Dict[str, Any]] = None

class ChartCreate(BaseModel):
    name: str
    description: Optional[str] = None
    dataset_id: str
    dataset_version_id: Optional[str] = None
    chart_type: ChartType
    config: ChartConfig

class ChartUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    chart_type: Optional[ChartType] = None
    config: Optional[ChartConfig] = None

class ChartResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    workspace_id: str
    dataset_id: str
    dataset_version_id: Optional[str] = None
    name: str
    description: Optional[str] = None
    chart_type: ChartType
    config: Dict[str, Any]
    created_at: datetime
    updated_at: datetime

class ChartQueryRequest(BaseModel):
    global_filters: Optional[List[Dict[str, Any]]] = None

class ChartDataResponse(BaseModel):
    chart_id: Optional[str] = None
    dataset_version_id: str
    chart_type: ChartType
    data: Any
    metadata: Dict[str, Any]

# ----------------- Dashboard Schemas -----------------
class DashboardChartLayout(BaseModel):
    chart_id: str
    position_x: int = 0
    position_y: int = 0
    width: int = 6
    height: int = 4
    overrides: Optional[Dict[str, Any]] = None

class DashboardCreate(BaseModel):
    title: str
    description: Optional[str] = None
    charts: Optional[List[DashboardChartLayout]] = None
    global_filters: Optional[List[Dict[str, Any]]] = None

class DashboardUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    charts: Optional[List[DashboardChartLayout]] = None
    global_filters: Optional[List[Dict[str, Any]]] = None
    version: int

class DashboardResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    workspace_id: str
    title: str
    description: Optional[str] = None
    version: int
    is_public: bool
    global_filters: List[Dict[str, Any]]
    charts: List[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime

class ShareLinkCreate(BaseModel):
    password: Optional[str] = None
    expires_in_days: Optional[int] = 30
    allow_export: bool = True

class ShareLinkResponse(BaseModel):
    token: str
    share_url: str
    expires_at: Optional[datetime] = None
    allow_export: bool
    is_active: bool

# ----------------- SQL Studio Schemas -----------------
class SQLExecuteRequest(BaseModel):
    sql_text: str
    dataset_ids: Optional[List[str]] = None

class SQLExecuteResponse(BaseModel):
    columns: List[str]
    rows: List[Dict[str, Any]]
    row_count: int
    duration_ms: float
    error: Optional[str] = None

class SavedQueryCreate(BaseModel):
    name: str
    description: Optional[str] = None
    sql_text: str

class SavedQueryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    workspace_id: str
    name: str
    description: Optional[str] = None
    sql_text: str
    created_at: datetime

# ----------------- ML Analytics Schemas -----------------
class MetricImportRow(BaseModel):
    run_id: str
    metric_name: str
    step: int
    epoch: Optional[int] = None
    value: float

class MetricsImportRequest(BaseModel):
    experiment_name: str
    framework: Optional[str] = "PyTorch"
    metrics: List[MetricImportRow]

class PredictionsImportRequest(BaseModel):
    experiment_name: str
    run_id: str
    split_name: str = "test"
    true_labels: List[Any]
    predicted_labels: List[Any]
    predicted_scores: Optional[List[Any]] = None

class MLExperimentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    workspace_id: str
    name: str
    description: Optional[str] = None
    framework: str
    created_at: datetime
    runs_count: int = 0

class EvaluationMetricsResponse(BaseModel):
    experiment_id: str
    run_id: str
    split_name: str
    accuracy: float
    precision_macro: float
    recall_macro: float
    f1_macro: float
    confusion_matrix: Dict[str, Any]
    roc_curve: Optional[Dict[str, Any]] = None
    pr_curve: Optional[Dict[str, Any]] = None
    provenance_note: str = "computed from imported predictions via scikit-learn"
