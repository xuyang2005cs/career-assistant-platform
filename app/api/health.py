"""Health-check endpoint."""

from typing import Literal

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(tags=["health"])


class HealthResponse(BaseModel):
    """Response returned when the API is ready to serve requests."""

    status: Literal["ok"]


@router.get("/health", response_model=HealthResponse)
def health_check() -> HealthResponse:
    """Report that the API process is healthy."""

    return HealthResponse(status="ok")
