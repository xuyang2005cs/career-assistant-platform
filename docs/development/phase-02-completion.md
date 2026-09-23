# Phase 2 Completion Log

Date: 2026-09-24

## Outcome

Phase 2 now provides a complete Job management slice: persistence, validated CRUD, filters, pagination, deterministic demo data, a small browser demo, preview-only JD extraction, 40 automated tests, and reproducible visual evidence.

## Database and Test Isolation

- Development database: SQLite at the environment-configured `DATABASE_URL`; the default is `sqlite:///./career_assistant.db`.
- Demo seed: 10 fictional records across six lifecycle states and multiple companies/locations.
- Test database: a new temporary SQLite file for every pytest case through a dependency override.
- MySQL: CLI, Windows service, and port 3306 were unavailable; no installation was attempted and MySQL was not verified.
- Schema initialization stays on `Base.metadata.create_all()` because a single-table MVP has no migration history to evolve yet.

## Lifecycle, Filtering, and Pagination

The lifecycle is `saved`, `applied`, `interview`, `offer`, `rejected`, and `closed`. `closed` covers expired or withdrawn opportunities without mislabeling them as employer rejection. List requests support page/page-size plus case-insensitive exact company/location filters and status filtering.

## Demo Design

`GET /demo` is a framework-light HTML/CSS/JavaScript workbench served by FastAPI. It reads and writes through the existing REST API. It shows live status counts, filtering, the current Job list, and a four-step Paste → Extract → Review → Save flow. There is no parallel business implementation in the page.

## Extraction Provider Design

- `rule_based`: always available, deterministic, and tested; recognizes labeled title/company/location fields and a bounded skill vocabulary.
- `deepseek`: optional HTTP provider with timeout and classified handling for authentication, rate limits, server errors, network failures, and malformed responses.
- `mock`: deterministic test/development provider whose response is explicitly labeled `mock`.
- Fallback responses are explicitly labeled `rule_based_fallback` with a non-secret reason code.

Extraction creates a preview only. Persistence remains an explicit call to the Job API.

## DeepSeek Availability

Only the project configuration and current shell environment were checked. No `DEEPSEEK_API_KEY`, base URL, or model override was configured, so no real external call was attempted. The code default (`https://api.deepseek.com`, `deepseek-flash`) and JSON response mode were checked against the current official DeepSeek API documentation. Provider behavior is covered with HTTPX mock transports, not reported as real-provider verification.

## Verification

- `python -m pytest -v`: 40 passed.
- Real Uvicorn acceptance: health, Swagger, list, create, get, update, filter, pagination, extraction, delete, and post-delete 404.
- Browser acceptance: `/demo` and `/docs` rendered without console errors; a synthetic extracted preview was edited, saved, observed in the tracker, and deleted afterward.
- Seed idempotency: first normalization produced 10 demo records; a repeat produced `created=0, skipped=10`.

## Bugs and Lessons

The detailed issue log records the real failures and fixes. The most reusable lessons were to keep runtime error schemas aligned with OpenAPI, avoid `file:` navigation for automated screenshots, remove browser-console noise such as a missing favicon, and generate test evidence from machine-readable output rather than manually typing a result.

## Deferred

- MySQL runtime and driver verification
- Alembic migrations when schema evolution begins
- Real DeepSeek smoke test when the user deliberately supplies a key
- Authentication, additional career entities, deployment, and observability
