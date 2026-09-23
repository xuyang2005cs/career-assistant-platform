"""FastAPI application entry point."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.health import router as health_router
from app.api.jobs import router as jobs_router
from app.core.config import get_settings
from app.core.database import initialize_database
from app.core.errors import register_exception_handlers


@asynccontextmanager
async def lifespan(application: FastAPI) -> AsyncIterator[None]:
    """Initialize local schema resources for the application process."""

    del application
    initialize_database()
    yield


settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    description="Backend services for a career application workflow.",
    version="0.2.0",
    lifespan=lifespan,
)

register_exception_handlers(app)
app.include_router(health_router)
app.include_router(jobs_router)
