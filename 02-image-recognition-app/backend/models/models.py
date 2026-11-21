from datetime import datetime, timezone
import uuid
from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from ..core.database import Base


def generate_uuid() -> str:
    return str(uuid.uuid4())


class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(50), default="researcher", nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    images = relationship("ImageAsset", back_populates="user", cascade="all, delete-orphan")
    analyses = relationship("ImageAnalysis", back_populates="user", cascade="all, delete-orphan")


class ImageAsset(Base):
    __tablename__ = "image_assets"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    filename = Column(String(255), nullable=False)
    original_name = Column(String(255), nullable=False)
    file_path = Column(String(512), nullable=False)
    thumbnail_path = Column(String(512), nullable=False)
    mime_type = Column(String(50), nullable=False)
    file_size_bytes = Column(Integer, nullable=False)
    width = Column(Integer, nullable=False)
    height = Column(Integer, nullable=False)
    perceptual_hash = Column(String(64), index=True, nullable=False)
    is_deleted = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    user = relationship("User", back_populates="images")
    analyses = relationship("ImageAnalysis", back_populates="image", cascade="all, delete-orphan")


class ImageAnalysis(Base):
    __tablename__ = "image_analyses"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    image_id = Column(String(36), ForeignKey("image_assets.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    task_type = Column(String(50), nullable=False)  # classification, detection, explainability
    model_name = Column(String(100), nullable=False)
    model_version = Column(String(50), nullable=False)
    latency_ms = Column(Float, nullable=False)
    status = Column(String(50), default="completed", nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    user = relationship("User", back_populates="analyses")
    image = relationship("ImageAsset", back_populates="analyses")
    classification = relationship("ClassificationResult", uselist=False, back_populates="analysis", cascade="all, delete-orphan")
    detection = relationship("DetectionResult", uselist=False, back_populates="analysis", cascade="all, delete-orphan")
    explainability = relationship("ExplainabilityResult", uselist=False, back_populates="analysis", cascade="all, delete-orphan")


class ClassificationResult(Base):
    __tablename__ = "classification_results"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    analysis_id = Column(String(36), ForeignKey("image_analyses.id", ondelete="CASCADE"), nullable=False, unique=True)
    top_label = Column(String(100), nullable=False)
    top_score = Column(Float, nullable=False)
    is_uncertain = Column(Boolean, default=False, nullable=False)
    predictions_json = Column(Text, nullable=False)  # JSON list of top-k [{class_id, label, score}]
    embedding_json = Column(Text, nullable=False)    # JSON list of 576-dim normalized embedding
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    analysis = relationship("ImageAnalysis", back_populates="classification")


class DetectionResult(Base):
    __tablename__ = "detection_results"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    analysis_id = Column(String(36), ForeignKey("image_analyses.id", ondelete="CASCADE"), nullable=False, unique=True)
    total_objects = Column(Integer, nullable=False)
    class_counts_json = Column(Text, nullable=False) # JSON dict of {"label": count}
    detections_json = Column(Text, nullable=False)   # JSON list of bounding box objects
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    analysis = relationship("ImageAnalysis", back_populates="detection")


class ExplainabilityResult(Base):
    __tablename__ = "explainability_results"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    analysis_id = Column(String(36), ForeignKey("image_analyses.id", ondelete="CASCADE"), nullable=False, unique=True)
    target_class_id = Column(Integer, nullable=False)
    target_label = Column(String(100), nullable=False)
    confidence = Column(Float, nullable=False)
    heatmap_path = Column(String(512), nullable=False)
    disclaimer = Column(String(255), default="approximate explanation", nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    analysis = relationship("ImageAnalysis", back_populates="explainability")


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), nullable=True)
    action = Column(String(100), nullable=False)
    resource_type = Column(String(50), nullable=False)
    resource_id = Column(String(100), nullable=True)
    details_json = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
