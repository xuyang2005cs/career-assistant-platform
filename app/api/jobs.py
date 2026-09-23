"""REST endpoints for Job management."""

from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query, Response, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.job import JobStatus
from app.schemas.error import ErrorResponse
from app.schemas.job import JobCreate, JobList, JobRead, JobUpdate
from app.services import job_service

router = APIRouter(
    prefix="/api/v1/jobs",
    tags=["jobs"],
    responses={
        status.HTTP_422_UNPROCESSABLE_CONTENT: {
            "model": ErrorResponse,
            "description": "Request validation failed",
        }
    },
)
DatabaseSession = Annotated[Session, Depends(get_db)]
JobId = Annotated[int, Path(gt=0)]


@router.post("", response_model=JobRead, status_code=status.HTTP_201_CREATED)
def create_job(job_data: JobCreate, db: DatabaseSession) -> JobRead:
    """Create a job opportunity."""

    return JobRead.model_validate(job_service.create_job(db, job_data))


@router.get("", response_model=JobList)
def list_jobs(
    db: DatabaseSession,
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 20,
    company: Annotated[str | None, Query(min_length=1, max_length=200)] = None,
    status_filter: Annotated[
        JobStatus | None,
        Query(alias="status"),
    ] = None,
    location: Annotated[str | None, Query(min_length=1, max_length=200)] = None,
) -> JobList:
    """List jobs with pagination and optional exact-match filters."""

    return job_service.list_jobs(
        db,
        page=page,
        page_size=page_size,
        company=company,
        status=status_filter,
        location=location,
    )


@router.get(
    "/{job_id}",
    response_model=JobRead,
    responses={
        status.HTTP_404_NOT_FOUND: {
            "model": ErrorResponse,
            "description": "Job not found",
        }
    },
)
def get_job(job_id: JobId, db: DatabaseSession) -> JobRead:
    """Return a job by identifier."""

    return JobRead.model_validate(job_service.get_job(db, job_id))


@router.patch(
    "/{job_id}",
    response_model=JobRead,
    responses={
        status.HTTP_404_NOT_FOUND: {
            "model": ErrorResponse,
            "description": "Job not found",
        }
    },
)
def update_job(job_id: JobId, job_data: JobUpdate, db: DatabaseSession) -> JobRead:
    """Partially update a job."""

    return JobRead.model_validate(job_service.update_job(db, job_id, job_data))


@router.delete(
    "/{job_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        status.HTTP_404_NOT_FOUND: {
            "model": ErrorResponse,
            "description": "Job not found",
        }
    },
)
def delete_job(job_id: JobId, db: DatabaseSession) -> Response:
    """Delete a job by identifier."""

    job_service.delete_job(db, job_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
