from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from core.config import settings
from core.database import init_db
from api.routers import (
    auth, workspaces, datasets, transformations, charts, dashboards, sql, ml
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize database tables on startup
    await init_db()
    yield

app = FastAPI(
    title=settings.APP_NAME,
    description="Cognix Data Visualization Dashboard Backend API",
    version="1.0.0",
    lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(auth.router, prefix="/api/v1")
app.include_router(workspaces.router, prefix="/api/v1")
app.include_router(datasets.router, prefix="/api/v1")
app.include_router(transformations.router, prefix="/api/v1")
app.include_router(charts.router, prefix="/api/v1")
app.include_router(dashboards.router, prefix="/api/v1")
app.include_router(sql.router, prefix="/api/v1")
app.include_router(ml.router, prefix="/api/v1")

@app.get("/api/v1/health")
async def health_check():
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "environment": settings.ENV
    }
