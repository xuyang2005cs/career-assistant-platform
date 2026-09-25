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
    tags=["岗位管理"],
    responses={
        status.HTTP_422_UNPROCESSABLE_CONTENT: {
            "model": ErrorResponse,
            "description": "请求参数校验失败",
        }
    },
)
DatabaseSession = Annotated[Session, Depends(get_db)]
JobId = Annotated[int, Path(gt=0)]


@router.post(
    "",
    response_model=JobRead,
    status_code=status.HTTP_201_CREATED,
    summary="创建岗位",
    description="创建一条岗位记录并返回完整岗位信息。",
)
def create_job(job_data: JobCreate, db: DatabaseSession) -> JobRead:
    """Create a job opportunity."""

    return JobRead.model_validate(job_service.create_job(db, job_data))


@router.get(
    "",
    response_model=JobList,
    summary="查询岗位列表",
    description="分页查询岗位，并支持按公司、状态和地点筛选。",
)
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
    summary="查询岗位详情",
    description="根据岗位 ID 查询一条岗位记录。",
    responses={
        status.HTTP_404_NOT_FOUND: {
            "model": ErrorResponse,
            "description": "岗位不存在",
        }
    },
)
def get_job(job_id: JobId, db: DatabaseSession) -> JobRead:
    """Return a job by identifier."""

    return JobRead.model_validate(job_service.get_job(db, job_id))


@router.patch(
    "/{job_id}",
    response_model=JobRead,
    summary="更新岗位",
    description="更新指定岗位中已提交的字段。",
    responses={
        status.HTTP_404_NOT_FOUND: {
            "model": ErrorResponse,
            "description": "岗位不存在",
        }
    },
)
def update_job(job_id: JobId, job_data: JobUpdate, db: DatabaseSession) -> JobRead:
    """Partially update a job."""

    return JobRead.model_validate(job_service.update_job(db, job_id, job_data))


@router.delete(
    "/{job_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="删除岗位",
    description="根据岗位 ID 删除一条岗位记录。",
    responses={
        status.HTTP_404_NOT_FOUND: {
            "model": ErrorResponse,
            "description": "岗位不存在",
        }
    },
)
def delete_job(job_id: JobId, db: DatabaseSession) -> Response:
    """Delete a job by identifier."""

    job_service.delete_job(db, job_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
