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
    role = Column(String(50), default="customer", nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    interactions = relationship("Interaction", back_populates="user", cascade="all, delete-orphan")
    preference = relationship("UserPreference", uselist=False, back_populates="user", cascade="all, delete-orphan")


class Item(Base):
    __tablename__ = "items"

    id = Column(String(50), primary_key=True)
    title = Column(String(255), nullable=False)
    category = Column(String(100), index=True, nullable=False)
    price = Column(Float, nullable=False)
    rating = Column(Float, default=4.5, nullable=False)
    review_count = Column(Integer, default=0, nullable=False)
    tags = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    image_url = Column(String(512), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    interactions = relationship("Interaction", back_populates="item", cascade="all, delete-orphan")


class Interaction(Base):
    __tablename__ = "interactions"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    item_id = Column(String(50), ForeignKey("items.id", ondelete="CASCADE"), index=True, nullable=False)
    interaction_type = Column(String(50), nullable=False)  # click, favorite, add_to_cart, purchase
    weight = Column(Float, nullable=False)  # 1.0, 2.0, 3.0, 5.0
    session_id = Column(String(100), index=True, nullable=True)
    timestamp = Column(Float, index=True, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    user = relationship("User", back_populates="interactions")
    item = relationship("Item", back_populates="interactions")


class UserPreference(Base):
    """Stores preference profile from cold-start onboarding quiz."""
    __tablename__ = "user_preferences"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    selected_categories_json = Column(Text, nullable=False)  # JSON list of category strings
    price_tier = Column(String(50), default="mid", nullable=False)  # budget, mid, premium
    tech_affinity = Column(String(50), default="high", nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    user = relationship("User", back_populates="preference")


class ABEvent(Base):
    __tablename__ = "ab_events"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    experiment_id = Column(String(100), index=True, nullable=False)
    variant_id = Column(String(50), index=True, nullable=False)
    user_id = Column(String(36), nullable=False)
    event_type = Column(String(50), nullable=False)  # impression, click, conversion
    item_id = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
