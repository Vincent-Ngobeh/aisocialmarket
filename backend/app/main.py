"""
AI Social Market - FastAPI Application
A tool helping UK small businesses generate social media marketing content.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.api.routes import campaign


settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan handler.
    Runs on startup and shutdown.
    """
    # Startup
    print(f"Starting {settings.app_name} v{settings.app_version}")
    print(f"Debug mode: {settings.debug}")
    yield
    # Shutdown
    print("Shutting down application")


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="API for generating UK-focused social media marketing content using AI",
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Root endpoint - basic API information."""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "status": "running",
        "docs": "/docs",
    }


@app.get("/health")
async def health_check():
    """
    Health check endpoint for deployment platforms.
    Railway and other platforms use this to verify the app is running.
    """
    return {
        "status": "healthy",
        "version": settings.app_version,
    }


# Include routers
app.include_router(campaign.router, prefix="/api/v1")
