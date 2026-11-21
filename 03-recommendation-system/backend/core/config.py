import os
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    PROJECT_NAME: str = "Cognix Recommendation System"
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = os.getenv("SECRET_KEY", "cognix-recsys-super-secret-key-2026")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24

    # Dual SQLite / Postgres Database URL
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "sqlite+aiosqlite:///./cognix_recommendation.db"
    )

    CORS_ORIGINS: List[str] = ["http://localhost:3002", "http://127.0.0.1:3002", "http://localhost:3000"]

    class Config:
        case_sensitive = True


settings = Settings()
