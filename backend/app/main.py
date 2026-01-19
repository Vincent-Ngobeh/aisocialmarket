from contextlib import asynccontextmanager
import logging
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi.errors import RateLimitExceeded

from app.core.config import get_settings
from app.core.database import engine, Base
from app.core.rate_limit import limiter
from app.core.error_handlers import rate_limit_handler, general_exception_handler
from app.api.routes import campaign, image, seasonal


settings = get_settings()

logging.getLogger("uvicorn.access").addFilter(
    lambda record: "X-Anthropic-Key" not in record.getMessage()
    and "X-OpenAI-Key" not in record.getMessage()
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    print(f"Starting {settings.app_name} v{settings.app_version}")
    print(f"Debug mode: {settings.debug}")

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("Database tables created")

    yield

    await engine.dispose()
    print("Shutting down application")


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="API for generating UK-focused social media marketing content using AI",
    lifespan=lifespan,
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, rate_limit_handler)
app.add_exception_handler(Exception, general_exception_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type", "X-Anthropic-Key", "X-OpenAI-Key"],
)


@app.get("/")
async def root():
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "status": "running",
    }


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "version": settings.app_version,
    }


app.include_router(campaign.router, prefix="/api/v1")
app.include_router(image.router, prefix="/api/v1")
app.include_router(seasonal.router, prefix="/api/v1")
