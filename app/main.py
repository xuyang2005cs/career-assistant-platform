"""FastAPI application entry point."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.api.demo import router as demo_router
from app.api.extraction import router as extraction_router
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
static_directory = Path(__file__).resolve().parent / "static"

app = FastAPI(
    title=settings.app_name,
    description="面向求职岗位管理与职位信息提取的后端服务。",
    version="0.2.0",
    lifespan=lifespan,
)

register_exception_handlers(app)
app.mount("/static", StaticFiles(directory=static_directory), name="static")
app.include_router(health_router)
app.include_router(jobs_router)
app.include_router(extraction_router)
app.include_router(demo_router)
