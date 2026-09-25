"""Health-check endpoint."""

from typing import Literal

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(tags=["运行状态"])


class HealthResponse(BaseModel):
    """Response returned when the API is ready to serve requests."""

    status: Literal["ok"]


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="检查服务状态",
    description="返回 API 服务的当前可用状态。",
)
def health_check() -> HealthResponse:
    """Report that the API process is healthy."""

    return HealthResponse(status="ok")
