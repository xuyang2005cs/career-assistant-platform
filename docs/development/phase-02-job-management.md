# Phase 2: Job Management API and SQLAlchemy

Date: 2026-09-24

## Goals

- Design one focused Job domain model.
- Add SQLAlchemy 2.x persistence and environment-based database configuration.
- Deliver validated CRUD, filtering, and pagination.
- Isolate automated tests from the development database.
- Verify OpenAPI and real HTTP behavior.
- Add genuine architecture, schema, and runtime evidence.

## Environment Check

- Python: 3.13.14
- FastAPI: 0.141.1
- SQLAlchemy: 2.0.54
- Pydantic: 2.13.5
- pytest: 9.1.1
- HTTPX: 0.28.1
- MySQL CLI: not found
- MySQL/MariaDB Windows service: not found
- TCP port 3306 listener: not found

No system-level database software was installed.

## Database Choice

SQLite is the actually verified Phase 2 development database. It supports the real local API demonstration without introducing a system installation. Each test uses a different temporary SQLite file through FastAPI dependency overrides.

The application reads `DATABASE_URL`, and SQLite-specific connection options are applied conditionally. This provides a clean switch point for a future MySQL environment, but MySQL is not claimed as verified.

## Model Design

The Job model contains only `id`, `title`, `company`, `location`, `description`, `source_url`, `status`, `created_at`, and `updated_at`. `title` and `company` are required and non-blank. `location`, `description`, and `source_url` may be absent.

Six statuses were selected: `saved`, `applied`, `interview`, `offer`, `rejected`, and `closed`. The final value distinguishes a withdrawn or expired opportunity from an explicit rejection.

## API Design

- `POST /api/v1/jobs` returns `201`.
- `GET /api/v1/jobs` returns pagination metadata and supports company, status, and location filters.
- `GET /api/v1/jobs/{job_id}` returns a job or a consistent `404` response.
- `PATCH /api/v1/jobs/{job_id}` updates only supplied fields and rejects empty patches.
- `DELETE /api/v1/jobs/{job_id}` returns `204` or a consistent `404` response.
- Validation failures return `422` with the shared `ErrorResponse` envelope.

## Test Strategy

The suite exercises the ASGI application through HTTPX. A fixture creates a new SQLite file and SQLAlchemy engine for every test, overrides `get_db`, and disposes the engine afterward. This prevents ordering dependencies and protects the development database.

Phase 2 result: 17 tests passed, including all required CRUD, validation, pagination, filtering, and missing-resource cases.

## Manual Acceptance

Uvicorn was started at `127.0.0.1:8000`. Real requests verified `/health`, `/docs`, create, get, combined filters, patch, delete, and missing-resource behavior. Swagger “Try it out” created a second synthetic Job and returned HTTP `201`.

See [API Acceptance Evidence](api-acceptance-phase-02.md) and the images in [`docs/images`](../images/README.md).

## Deferred Work

- MySQL driver selection and runtime verification
- Alembic migrations
- Entities other than Job
- Authentication and authorization
- AI, RAG, agents, MCP, and vector storage
