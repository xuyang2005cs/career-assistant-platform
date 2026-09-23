"""Tests for the synthetic development-data seed."""

from pathlib import Path

from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import Session

from app.core.database import Base
from app.models.job import Job, JobStatus
from scripts.seed_demo_data import DEMO_JOBS, seed_demo_data


def test_seed_demo_data_is_complete_and_idempotent(tmp_path: Path) -> None:
    engine = create_engine(f"sqlite:///{(tmp_path / 'seed.db').as_posix()}")
    Base.metadata.create_all(bind=engine)

    with Session(engine) as session:
        first_created, first_skipped = seed_demo_data(session)
        second_created, second_skipped = seed_demo_data(session)
        total = session.scalar(select(func.count(Job.id)))
        statuses = set(session.scalars(select(Job.status)).all())

    engine.dispose()

    assert first_created == len(DEMO_JOBS) == 10
    assert first_skipped == 0
    assert second_created == 0
    assert second_skipped == 10
    assert total == 10
    assert statuses == set(JobStatus)
