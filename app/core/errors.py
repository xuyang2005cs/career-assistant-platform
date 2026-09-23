"""Application exceptions and consistent API error responses."""

from typing import Any

from fastapi import FastAPI, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.schemas.error import ErrorDetail, ErrorResponse


class JobNotFoundError(Exception):
    """Raised when a requested job does not exist."""

    def __init__(self, job_id: int) -> None:
        self.job_id = job_id
        super().__init__(f"Job {job_id} was not found")


def error_payload(code: str, message: str, details: Any = None) -> dict[str, Any]:
    """Build the common error response envelope."""

    response = ErrorResponse(
        error=ErrorDetail(code=code, message=message, details=details)
    )
    return response.model_dump(exclude_none=True)


def register_exception_handlers(app: FastAPI) -> None:
    """Register application-specific and request-validation handlers."""

    @app.exception_handler(JobNotFoundError)
    async def job_not_found_handler(
        request: Request,
        exc: JobNotFoundError,
    ) -> JSONResponse:
        del request
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=error_payload("job_not_found", str(exc)),
        )

    @app.exception_handler(RequestValidationError)
    async def validation_error_handler(
        request: Request,
        exc: RequestValidationError,
    ) -> JSONResponse:
        del request
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            content=error_payload(
                "validation_error",
                "Request validation failed",
                jsonable_encoder(exc.errors()),
            ),
        )
