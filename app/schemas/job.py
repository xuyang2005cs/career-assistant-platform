"""Pydantic contracts for the Job API."""

from datetime import datetime
from typing import Annotated, Self

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, StringConstraints, model_validator

from app.models.job import JobStatus

JobTitle = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=200)]
CompanyName = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=200)]
Location = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=200)]


class JobCreate(BaseModel):
    """Fields accepted when creating a job."""

    title: JobTitle
    company: CompanyName
    location: Location | None = None
    description: str | None = Field(default=None, max_length=20_000)
    source_url: HttpUrl | None = None
    status: JobStatus = JobStatus.SAVED


class JobUpdate(BaseModel):
    """Fields accepted for a partial job update."""

    title: JobTitle | None = None
    company: CompanyName | None = None
    location: Location | None = None
    description: str | None = Field(default=None, max_length=20_000)
    source_url: HttpUrl | None = None
    status: JobStatus | None = None

    @model_validator(mode="after")
    def validate_patch(self) -> Self:
        """Reject empty updates and nulls for required database fields."""

        if not self.model_fields_set:
            raise ValueError("At least one field must be provided")

        required_fields = {"title", "company", "status"}
        null_required_fields = [
            field_name
            for field_name in required_fields & self.model_fields_set
            if getattr(self, field_name) is None
        ]
        if null_required_fields:
            fields = ", ".join(sorted(null_required_fields))
            raise ValueError(f"Fields cannot be null: {fields}")

        return self


class JobRead(BaseModel):
    """Public representation of a stored job."""

    id: int
    title: str
    company: str
    location: str | None
    description: str | None
    source_url: str | None
    status: JobStatus
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class JobList(BaseModel):
    """Paginated collection of jobs."""

    items: list[JobRead]
    total: int
    page: int
    page_size: int
