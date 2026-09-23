# Technical Decisions

## TD-001: Keep Phase 1 intentionally small

Only a health endpoint is implemented. Empty package boundaries communicate likely areas of responsibility without introducing unused frameworks or abstractions.

## TD-002: Test through ASGI

The health test uses HTTPX `ASGITransport` and `AsyncClient`. This verifies routing, serialization, and the HTTP contract without opening a network port during the test suite.

## TD-003: Use repository-local Git identity

The project uses repository-local author settings so unrelated global Git settings are not overwritten. The commit address is the GitHub-provided noreply form tied to the verified repository owner account.

## TD-004: Use compatible dependency ranges

Direct dependencies use bounded ranges in `requirements.txt`. This keeps Phase 1 simple while preventing accidental upgrades to a future major version. A lock strategy can be introduced when deployment environments are defined.

## TD-005: Use one service layer, not a repository stack

The Job router delegates CRUD and queries to `job_service.py`, which works directly with a request-scoped SQLAlchemy session. Repository, DAO, manager, and use-case layers would duplicate responsibilities at the current scale.

## TD-006: Validate SQLite now and state MySQL status honestly

No MySQL executable, Windows service, or port 3306 listener was present. Phase 2 therefore verifies SQLite for development and temporary SQLite files for tests. `DATABASE_URL` remains the future database switch point, but MySQL is not described as working.

## TD-007: Use `create_all()` before migrations are needed

The current application has one table and no deployed schema history to migrate. SQLAlchemy metadata initialization is simpler and sufficient. Alembic will be introduced when schema evolution across persistent environments becomes a real requirement.

## TD-008: Return pagination metadata

The list endpoint returns `items`, `total`, `page`, and `page_size`. Clients can render navigation without inferring totals from page length.

## TD-009: Keep ORM and API contracts separate

`JobCreate`, `JobUpdate`, `JobRead`, and `JobList` prevent database concerns from becoming public request contracts. Partial updates use explicit field tracking, and required database fields cannot be set to null.
