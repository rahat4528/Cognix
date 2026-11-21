import os
from typing import List
from pydantic_settings import BaseSettings
from pydantic import ConfigDict

class Settings(BaseSettings):
    model_config = ConfigDict(env_file=".env", case_sensitive=True, extra="ignore")

    APP_NAME: str = "Cognix Data Visualization Dashboard"
    ENV: str = "development"
    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"

    # JWT Authentication
    JWT_SECRET: str = "cognix_dataviz_super_secret_jwt_key_must_be_at_least_32_chars!"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Database: SQLite fallback for local development/tests, PostgreSQL for prod
    DATABASE_URL: str = "sqlite+aiosqlite:///./cognix_dataviz_dev.db"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # Storage
    STORAGE_BACKEND: str = "local"  # 'local' or 's3'
    STORAGE_LOCAL_PATH: str = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "storage", "datasets"))
    S3_ENDPOINT: str = "http://localhost:9000"
    S3_ACCESS_KEY: str = "cognix_minio_admin"
    S3_SECRET_KEY: str = "cognix_minio_secret_key"
    S3_BUCKET: str = "cognix-dataviz-datasets"

    # CORS
    CORS_ORIGINS: str = "http://localhost:3000,http://127.0.0.1:3000,http://localhost:8000"

    # Limits
    MAX_UPLOAD_SIZE_BYTES: int = 100 * 1024 * 1024  # 100MB
    SQL_QUERY_TIMEOUT_SECONDS: int = 15
    SQL_MAX_RESULT_ROWS: int = 10000

    @property
    def cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]

settings = Settings()
