"""SQLAlchemy engine, session, and schema initialization."""

from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import get_settings


class Base(DeclarativeBase):
    """Base class for SQLAlchemy ORM models."""


settings = get_settings()
engine_options: dict[str, object] = {}
if settings.database_url.startswith("sqlite"):
    engine_options["connect_args"] = {"check_same_thread": False}

engine = create_engine(settings.database_url, **engine_options)
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


def get_db() -> Generator[Session, None, None]:
    """Provide one database session per API request."""

    with SessionLocal() as session:
        yield session


def initialize_database() -> None:
    """Create tables required by the current application model."""

    # Import model modules before create_all so their table metadata is known.
    from app.models import job  # noqa: F401

    Base.metadata.create_all(bind=engine)
