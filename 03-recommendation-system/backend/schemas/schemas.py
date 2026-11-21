from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, EmailStr


class Token(BaseModel):
    access_token: str
    token_type: str


class UserBase(BaseModel):
    email: EmailStr
    role: str = "customer"


class UserCreate(UserBase):
    password: str = Field(..., min_length=6)


class UserResponse(UserBase):
    id: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class ItemResponse(BaseModel):
    id: str
    title: str
    category: str
    price: float
    rating: float
    review_count: int
    tags: str
    description: str
    image_url: Optional[str] = None

    class Config:
        from_attributes = True


class InteractionCreate(BaseModel):
    item_id: str
    interaction_type: str  # click, favorite, add_to_cart, purchase
    session_id: Optional[str] = None


class RecommendationItem(BaseModel):
    item: ItemResponse
    score: float
    explanation: Optional[str] = None
    model_contributions: Optional[Dict[str, float]] = None
    is_cold_start: bool = False


class ColdStartQuizRequest(BaseModel):
    selected_categories: List[str]
    price_tier: str = "mid"
    tech_affinity: str = "high"


class BenchmarkMetrics(BaseModel):
    ndcg_at_10: float
    recall_at_10: float
    precision_at_10: float
    map_at_10: float
    catalog_coverage: float
