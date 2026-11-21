import enum
import uuid
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from sqlalchemy import (
    Column, String, Integer, Float, Boolean, DateTime, ForeignKey, 
    Text, Enum, JSON, UniqueConstraint, Index
)
from sqlalchemy.orm import relationship
from core.database import Base

def generate_uuid() -> str:
    return str(uuid.uuid4())

class Role(str, enum.Enum):
    OWNER = "OWNER"
    ADMIN = "ADMIN"
    EDITOR = "EDITOR"
    VIEWER = "VIEWER"

class SourceType(str, enum.Enum):
    FILE = "FILE"
    SQL = "SQL"
    API = "API"

class ChartType(str, enum.Enum):
    BAR = "BAR"
    LINE = "LINE"
    AREA = "AREA"
    PIE = "PIE"
    DONUT = "DONUT"
    SCATTER = "SCATTER"
    HISTOGRAM = "HISTOGRAM"
    BOX_PLOT = "BOX_PLOT"
    HEATMAP = "HEATMAP"
    TIME_SERIES = "TIME_SERIES"
    MAP = "MAP"

class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_superuser = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    workspaces = relationship("WorkspaceMember", back_populates="user", cascade="all, delete-orphan")
    created_datasets = relationship("Dataset", back_populates="creator")
    created_charts = relationship("Chart", back_populates="creator")
    created_dashboards = relationship("Dashboard", back_populates="creator")

class Workspace(Base):
    __tablename__ = "workspaces"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(255), nullable=False)
    slug = Column(String(255), unique=True, index=True, nullable=False)
    description = Column(Text, nullable=True)
    owner_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    members = relationship("WorkspaceMember", back_populates="workspace", cascade="all, delete-orphan")
    datasets = relationship("Dataset", back_populates="workspace", cascade="all, delete-orphan")
    charts = relationship("Chart", back_populates="workspace", cascade="all, delete-orphan")
    dashboards = relationship("Dashboard", back_populates="workspace", cascade="all, delete-orphan")
    saved_queries = relationship("SavedQuery", back_populates="workspace", cascade="all, delete-orphan")
    ml_experiments = relationship("MLExperiment", back_populates="workspace", cascade="all, delete-orphan")

class WorkspaceMember(Base):
    __tablename__ = "workspace_members"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    workspace_id = Column(String(36), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    role = Column(Enum(Role), default=Role.VIEWER, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    workspace = relationship("Workspace", back_populates="members")
    user = relationship("User", back_populates="workspaces")

    __table_args__ = (
        UniqueConstraint("workspace_id", "user_id", name="uq_workspace_user"),
    )

class Dataset(Base):
    __tablename__ = "datasets"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    workspace_id = Column(String(36), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False)
    created_by_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    source_type = Column(Enum(SourceType), default=SourceType.FILE, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    workspace = relationship("Workspace", back_populates="datasets")
    creator = relationship("User", back_populates="created_datasets")
    versions = relationship("DatasetVersion", back_populates="dataset", cascade="all, delete-orphan")
    charts = relationship("Chart", back_populates="dataset", cascade="all, delete-orphan")

class DatasetVersion(Base):
    __tablename__ = "dataset_versions"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    dataset_id = Column(String(36), ForeignKey("datasets.id", ondelete="CASCADE"), nullable=False)
    version_number = Column(Integer, nullable=False)
    file_path = Column(String(512), nullable=False)  # Path to stored Parquet file
    original_filename = Column(String(255), nullable=False)
    file_format = Column(String(32), nullable=False)  # 'csv', 'parquet', 'json', 'xlsx'
    file_size_bytes = Column(Integer, nullable=False)
    row_count = Column(Integer, nullable=False)
    column_count = Column(Integer, nullable=False)
    checksum_sha256 = Column(String(64), nullable=False)
    quality_score = Column(Float, nullable=True)  # Overall quality score 0.0 - 100.0
    quality_report = Column(JSON, nullable=True)   # Profiling and quality summary
    is_active = Column(Boolean, default=True, nullable=False)
    created_by_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    dataset = relationship("Dataset", back_populates="versions")
    columns = relationship("DatasetColumn", back_populates="version", cascade="all, delete-orphan")

    __table_args__ = (
        UniqueConstraint("dataset_id", "version_number", name="uq_dataset_version"),
    )

class DatasetColumn(Base):
    __tablename__ = "dataset_columns"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    dataset_version_id = Column(String(36), ForeignKey("dataset_versions.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255), nullable=False)
    data_type = Column(String(64), nullable=False)  # integer, float, string, boolean, date, datetime, categorical
    is_nullable = Column(Boolean, default=True, nullable=False)
    null_count = Column(Integer, default=0, nullable=False)
    null_percentage = Column(Float, default=0.0, nullable=False)
    unique_count = Column(Integer, default=0, nullable=False)
    sample_values = Column(JSON, nullable=True)
    statistics = Column(JSON, nullable=True)  # min, max, mean, stddev, quantiles

    version = relationship("DatasetVersion", back_populates="columns")

class DataTransformation(Base):
    __tablename__ = "data_transformations"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    dataset_id = Column(String(36), ForeignKey("datasets.id", ondelete="CASCADE"), nullable=False)
    source_version_id = Column(String(36), ForeignKey("dataset_versions.id", ondelete="CASCADE"), nullable=False)
    target_version_id = Column(String(36), ForeignKey("dataset_versions.id", ondelete="CASCADE"), nullable=False)
    pipeline_spec = Column(JSON, nullable=False)  # List of transformation steps
    created_by_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

class Chart(Base):
    __tablename__ = "charts"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    workspace_id = Column(String(36), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False)
    dataset_id = Column(String(36), ForeignKey("datasets.id", ondelete="CASCADE"), nullable=False)
    dataset_version_id = Column(String(36), ForeignKey("dataset_versions.id", ondelete="SET NULL"), nullable=True)
    created_by_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    chart_type = Column(Enum(ChartType), nullable=False)
    config = Column(JSON, nullable=False)  # x_axis, y_axis, series, aggregation, filters, colors, etc.
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    workspace = relationship("Workspace", back_populates="charts")
    dataset = relationship("Dataset", back_populates="charts")
    creator = relationship("User", back_populates="created_charts")

class Dashboard(Base):
    __tablename__ = "dashboards"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    workspace_id = Column(String(36), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False)
    created_by_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    version = Column(Integer, default=1, nullable=False)
    is_public = Column(Boolean, default=False, nullable=False)
    global_filters = Column(JSON, default=list, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    workspace = relationship("Workspace", back_populates="dashboards")
    creator = relationship("User", back_populates="created_dashboards")
    charts = relationship("DashboardChart", back_populates="dashboard", cascade="all, delete-orphan")
    share_links = relationship("ShareLink", back_populates="dashboard", cascade="all, delete-orphan")

class DashboardChart(Base):
    __tablename__ = "dashboard_charts"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    dashboard_id = Column(String(36), ForeignKey("dashboards.id", ondelete="CASCADE"), nullable=False)
    chart_id = Column(String(36), ForeignKey("charts.id", ondelete="CASCADE"), nullable=False)
    position_x = Column(Integer, default=0, nullable=False)
    position_y = Column(Integer, default=0, nullable=False)
    width = Column(Integer, default=6, nullable=False)   # Grid width (1-12)
    height = Column(Integer, default=4, nullable=False)  # Grid height
    overrides = Column(JSON, nullable=True)

    dashboard = relationship("Dashboard", back_populates="charts")
    chart = relationship("Chart")

class ShareLink(Base):
    __tablename__ = "share_links"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    dashboard_id = Column(String(36), ForeignKey("dashboards.id", ondelete="CASCADE"), nullable=False)
    token = Column(String(64), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=True)
    expires_at = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    allow_export = Column(Boolean, default=True, nullable=False)
    access_count = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    dashboard = relationship("Dashboard", back_populates="share_links")

class SavedQuery(Base):
    __tablename__ = "saved_queries"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    workspace_id = Column(String(36), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False)
    created_by_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    sql_text = Column(Text, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    workspace = relationship("Workspace", back_populates="saved_queries")

class QueryExecution(Base):
    __tablename__ = "query_executions"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    workspace_id = Column(String(36), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    sql_text = Column(Text, nullable=False)
    duration_ms = Column(Float, nullable=False)
    row_count = Column(Integer, default=0, nullable=False)
    status = Column(String(32), default="SUCCESS", nullable=False)
    error_message = Column(Text, nullable=True)
    executed_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

class MLExperiment(Base):
    __tablename__ = "ml_experiments"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    workspace_id = Column(String(36), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False)
    created_by_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    framework = Column(String(64), default="PyTorch", nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    workspace = relationship("Workspace", back_populates="ml_experiments")
    metrics = relationship("ModelMetric", back_populates="experiment", cascade="all, delete-orphan")
    predictions = relationship("MLPrediction", back_populates="experiment", cascade="all, delete-orphan")

class ModelMetric(Base):
    __tablename__ = "model_metrics"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    experiment_id = Column(String(36), ForeignKey("ml_experiments.id", ondelete="CASCADE"), nullable=False)
    run_id = Column(String(64), nullable=False, index=True)
    metric_name = Column(String(128), nullable=False)  # loss, accuracy, val_loss, val_accuracy, etc.
    step = Column(Integer, nullable=False)
    epoch = Column(Integer, nullable=True)
    value = Column(Float, nullable=False)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    experiment = relationship("MLExperiment", back_populates="metrics")

class MLPrediction(Base):
    __tablename__ = "ml_predictions"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    experiment_id = Column(String(36), ForeignKey("ml_experiments.id", ondelete="CASCADE"), nullable=False)
    run_id = Column(String(64), nullable=False, index=True)
    split_name = Column(String(64), default="test", nullable=False)
    true_labels = Column(JSON, nullable=False)        # List of true classes
    predicted_labels = Column(JSON, nullable=False)   # List of predicted classes
    predicted_scores = Column(JSON, nullable=True)    # List of float probabilities or score matrix
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    experiment = relationship("MLExperiment", back_populates="predictions")

class DataAlert(Base):
    __tablename__ = "data_alerts"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    workspace_id = Column(String(36), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False)
    dataset_id = Column(String(36), ForeignKey("datasets.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255), nullable=False)
    condition = Column(JSON, nullable=False)  # e.g., {"column": "revenue", "operator": "<", "threshold": 1000}
    is_active = Column(Boolean, default=True, nullable=False)
    last_triggered_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    workspace_id = Column(String(36), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    action = Column(String(128), nullable=False)  # CREATE_DATASET, EXPORT_DASHBOARD, etc.
    resource_type = Column(String(64), nullable=False)
    resource_id = Column(String(36), nullable=False)
    details = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
