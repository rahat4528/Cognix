import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from ..core.config import settings
from ..core.database import engine, Base
from .routers import auth, images, inference, analyses, models

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    description="Cognix Computer Vision & Image Recognition API. Production-ready deep learning platform with classification, detection, Grad-CAM explainability, and similarity search."
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix=settings.API_V1_STR)
app.include_router(images.router, prefix=settings.API_V1_STR)
app.include_router(inference.router, prefix=settings.API_V1_STR)
app.include_router(analyses.router, prefix=settings.API_V1_STR)
app.include_router(models.router, prefix=settings.API_V1_STR)


@app.on_event("startup")
async def startup_event():
    # Automatically ensure database tables exist (SQLite zero-config or PostgreSQL)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "cognix-cv-backend",
        "version": "1.0.0"
    }
