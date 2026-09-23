"""Shared API error response contracts."""

from typing import Any

from pydantic import BaseModel


class ErrorDetail(BaseModel):
    """Machine-readable and human-readable error information."""

    code: str
    message: str
    details: list[dict[str, Any]] | None = None


class ErrorResponse(BaseModel):
    """Common error response envelope."""

    error: ErrorDetail
