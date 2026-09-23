"""Business operations for Job records."""

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.errors import JobNotFoundError
from app.models.job import Job, JobStatus
from app.schemas.job import JobCreate, JobList, JobRead, JobUpdate


def create_job(db: Session, job_data: JobCreate) -> Job:
    """Persist and return a new job."""

    job = Job(**job_data.model_dump(mode="json"))
    db.add(job)
    db.commit()
    db.refresh(job)
    return job


def list_jobs(
    db: Session,
    *,
    page: int,
    page_size: int,
    company: str | None = None,
    status: JobStatus | None = None,
    location: str | None = None,
) -> JobList:
    """Return jobs matching filters with stable, metadata-rich pagination."""

    filters = []
    if company is not None:
        filters.append(func.lower(Job.company) == company.strip().casefold())
    if status is not None:
        filters.append(Job.status == status)
    if location is not None:
        filters.append(func.lower(Job.location) == location.strip().casefold())

    total = db.scalar(select(func.count(Job.id)).where(*filters)) or 0
    jobs = db.scalars(
        select(Job)
        .where(*filters)
        .order_by(Job.created_at.desc(), Job.id.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    ).all()

    return JobList(
        items=[JobRead.model_validate(job) for job in jobs],
        total=total,
        page=page,
        page_size=page_size,
    )


def get_job(db: Session, job_id: int) -> Job:
    """Return one job or raise the domain not-found exception."""

    job = db.get(Job, job_id)
    if job is None:
        raise JobNotFoundError(job_id)
    return job


def update_job(db: Session, job_id: int, job_data: JobUpdate) -> Job:
    """Apply a partial update to an existing job."""

    job = get_job(db, job_id)
    changes = job_data.model_dump(exclude_unset=True, mode="json")
    for field_name, value in changes.items():
        setattr(job, field_name, value)

    db.commit()
    db.refresh(job)
    return job


def delete_job(db: Session, job_id: int) -> None:
    """Delete an existing job."""

    job = get_job(db, job_id)
    db.delete(job)
    db.commit()
