"""Job-description extraction preview endpoint."""

from typing import Annotated

from fastapi import APIRouter, Depends, status

from app.schemas.error import ErrorResponse
from app.schemas.extraction import JobExtractRequest, JobExtractionPreview
from app.services.extraction import ExtractionService, get_extraction_service

router = APIRouter(
    prefix="/api/v1",
    tags=["extraction"],
    responses={
        status.HTTP_422_UNPROCESSABLE_CONTENT: {
            "model": ErrorResponse,
            "description": "Request validation failed",
        }
    },
)
ExtractionServiceDependency = Annotated[
    ExtractionService,
    Depends(get_extraction_service),
]


@router.post("/job-extract", response_model=JobExtractionPreview)
async def extract_job(
    request: JobExtractRequest,
    service: ExtractionServiceDependency,
) -> JobExtractionPreview:
    """Extract a non-persistent Job preview from pasted description text."""

    return await service.extract(request.text)
