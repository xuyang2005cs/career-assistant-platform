"""Seed the development database with safe, synthetic Job records."""

from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import SessionLocal, initialize_database
from app.models.job import Job, JobStatus

DEMO_JOBS: tuple[dict[str, Any], ...] = (
    {
        "title": "Python Backend Intern",
        "company": "Example Tech",
        "location": "Beijing",
        "description": "Build and test Python API services with FastAPI and SQL.",
        "source_url": "https://example.com/jobs/python-backend-intern",
        "status": JobStatus.SAVED,
    },
    {
        "title": "API Platform Engineer",
        "company": "Sample Labs",
        "location": "Shanghai",
        "description": "Improve internal APIs, service reliability, and developer tooling.",
        "source_url": "https://example.com/jobs/api-platform-engineer",
        "status": JobStatus.APPLIED,
    },
    {
        "title": "Software Test Intern",
        "company": "Nova Systems",
        "location": "Shenzhen",
        "description": "Create automated API tests and investigate product quality issues.",
        "source_url": "https://example.com/jobs/software-test-intern",
        "status": JobStatus.INTERVIEW,
    },
    {
        "title": "Cloud Support Engineer",
        "company": "CloudWorks",
        "location": "Remote",
        "description": "Support cloud services and improve operational documentation.",
        "source_url": "https://example.com/jobs/cloud-support-engineer",
        "status": JobStatus.SAVED,
    },
    {
        "title": "Data Engineering Intern",
        "company": "DataBridge",
        "location": "Hangzhou",
        "description": "Develop reliable data pipelines with Python and SQL.",
        "source_url": "https://example.com/jobs/data-engineering-intern",
        "status": JobStatus.APPLIED,
    },
    {
        "title": "AI Application Intern",
        "company": "Future Labs",
        "location": "Beijing",
        "description": "Prototype practical AI features and evaluate structured outputs.",
        "source_url": "https://example.com/jobs/ai-application-intern",
        "status": JobStatus.OFFER,
    },
    {
        "title": "Java Backend Intern",
        "company": "Example Tech",
        "location": "Shanghai",
        "description": "Maintain Java services and write integration tests.",
        "source_url": "https://example.com/jobs/java-backend-intern",
        "status": JobStatus.REJECTED,
    },
    {
        "title": "QA Automation Intern",
        "company": "Nova Systems",
        "location": "Remote",
        "description": "Automate regression scenarios for web and API workflows.",
        "source_url": "https://example.com/jobs/qa-automation-intern",
        "status": JobStatus.CLOSED,
    },
    {
        "title": "Platform Engineering Intern",
        "company": "CloudWorks",
        "location": "Shenzhen",
        "description": "Improve CI workflows and internal platform services.",
        "source_url": "https://example.com/jobs/platform-engineering-intern",
        "status": JobStatus.SAVED,
    },
    {
        "title": "Backend Data Services Intern",
        "company": "DataBridge",
        "location": "Hangzhou",
        "description": "Build database-backed services for analytics products.",
        "source_url": "https://example.com/jobs/backend-data-services-intern",
        "status": JobStatus.INTERVIEW,
    },
)


def seed_demo_data(db: Session) -> tuple[int, int]:
    """Insert missing demo rows and return `(created, skipped)` counts."""

    created = 0
    skipped = 0

    for job_data in DEMO_JOBS:
        existing_id = db.scalar(
            select(Job.id).where(
                Job.title == job_data["title"],
                Job.company == job_data["company"],
            )
        )
        if existing_id is not None:
            skipped += 1
            continue

        db.add(Job(**job_data))
        created += 1

    db.commit()
    return created, skipped


def main() -> None:
    """Initialize the schema and seed the configured development database."""

    initialize_database()
    with SessionLocal() as session:
        created, skipped = seed_demo_data(session)

    print(f"Demo data ready: created={created}, skipped={skipped}, total={len(DEMO_JOBS)}")


if __name__ == "__main__":
    main()
