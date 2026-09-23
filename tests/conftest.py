"""Shared fixtures for isolated API integration tests."""

from collections.abc import AsyncIterator, Generator
from pathlib import Path

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.database import Base, get_db
from app.main import app


@pytest.fixture
def anyio_backend() -> str:
    """Run asynchronous tests on asyncio only."""

    return "asyncio"


@pytest.fixture
async def client(tmp_path: Path) -> AsyncIterator[AsyncClient]:
    """Provide an API client backed by a fresh SQLite database per test."""

    database_path = tmp_path / "test.db"
    test_engine = create_engine(
        f"sqlite:///{database_path.as_posix()}",
        connect_args={"check_same_thread": False},
    )
    testing_session = sessionmaker(
        bind=test_engine,
        autoflush=False,
        expire_on_commit=False,
    )
    Base.metadata.create_all(bind=test_engine)

    def override_get_db() -> Generator[Session, None, None]:
        with testing_session() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://test") as api_client:
        yield api_client

    app.dependency_overrides.clear()
    test_engine.dispose()
