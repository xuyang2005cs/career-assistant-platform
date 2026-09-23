"""Request and response contracts for job-description extraction."""

from typing import Annotated, Literal

from pydantic import BaseModel, Field, StringConstraints

from app.models.job import JobStatus

JobDescriptionText = Annotated[
    str,
    StringConstraints(strip_whitespace=True, min_length=1, max_length=20_000),
]
ExtractionMethod = Literal["rule_based", "deepseek", "mock", "rule_based_fallback"]


class JobExtractRequest(BaseModel):
    """Text submitted for a non-persistent extraction preview."""

    text: JobDescriptionText


class JobExtractionPreview(BaseModel):
    """Structured preview that can later be confirmed through the Job API."""

    title: str | None
    company: str | None
    location: str | None
    description: str
    source_url: None = None
    suggested_status: JobStatus = JobStatus.SAVED
    skills: list[str] = Field(default_factory=list)
    extraction_method: ExtractionMethod
    model: str | None = None
    latency_ms: int | None = None
    fallback_reason: str | None = None


class DeepSeekExtractionPayload(BaseModel):
    """Strict subset expected from a DeepSeek JSON response."""

    title: str | None = None
    company: str | None = None
    location: str | None = None
    skills: list[str] = Field(default_factory=list, max_length=30)
