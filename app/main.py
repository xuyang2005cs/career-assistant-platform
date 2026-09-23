"""FastAPI application entry point."""

from fastapi import FastAPI

from app.api.health import router as health_router

app = FastAPI(
    title="Career Assistant Platform",
    description="Backend services for a career application workflow.",
    version="0.1.0",
)

app.include_router(health_router)
