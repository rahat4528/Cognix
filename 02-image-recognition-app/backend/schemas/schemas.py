from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, EmailStr


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    user_id: Optional[str] = None


class UserBase(BaseModel):
    email: EmailStr
    role: str = "researcher"


class UserCreate(UserBase):
    password: str = Field(..., min_length=6)


class UserResponse(UserBase):
    id: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class ImageAssetResponse(BaseModel):
    id: str
    user_id: str
    filename: str
    original_name: str
    mime_type: str
    file_size_bytes: int
    width: int
    height: int
    perceptual_hash: str
    thumbnail_url: str
    image_url: str
    created_at: datetime

    class Config:
        from_attributes = True


class PredictionItem(BaseModel):
    class_id: int
    label: str
    score: float


class ClassificationResponse(BaseModel):
    analysis_id: str
    image_id: str
    model_name: str
    model_version: str
    top_label: str
    top_score: float
    is_uncertain: bool
    predictions: List[PredictionItem]
    embedding: Optional[List[float]] = None
    latency_ms: float


class DetectedObjectItem(BaseModel):
    label: str
    class_id: int
    score: float
    bbox_pixels: List[float]
    bbox_normalized: List[float]
    width: float
    height: float


class DetectionResponse(BaseModel):
    analysis_id: str
    image_id: str
    model_name: str
    model_version: str
    total_objects: int
    class_counts: Dict[str, int]
    detections: List[DetectedObjectItem]
    latency_ms: float


class ExplainabilityResponse(BaseModel):
    analysis_id: str
    image_id: str
    model_name: str
    target_class_id: int
    target_label: str
    confidence: float
    heatmap_data_url: str
    disclaimer: str
    latency_ms: float


class SimilarityMatch(BaseModel):
    image_id: str
    original_name: str
    thumbnail_url: str
    similarity_score: float
    top_label: Optional[str] = None


class SimilaritySearchResponse(BaseModel):
    query_image_id: str
    total_candidates: int
    matches: List[SimilarityMatch]
