# Phase 2 API Acceptance Evidence

Date: 2026-09-24

All records below are synthetic. Uvicorn served the real application on `http://127.0.0.1:8000` backed by the local SQLite development database.

## Endpoint Results

| Operation | Result |
|---|---|
| `GET /health` | `200`, `{"status":"ok"}` |
| `GET /docs` | `200` |
| `POST /api/v1/jobs` | `201`, created Job 1 |
| `GET /api/v1/jobs/1` | `200`, returned Job 1 |
| Filter by company + status + location | `200`, total 1 |
| `PATCH /api/v1/jobs/1` | `200`, status changed to `applied`, location to `Shanghai` |
| Filter by updated status + location | `200`, total 1 |
| `DELETE /api/v1/jobs/1` | `204`, empty body |
| `GET /api/v1/jobs/1` after delete | `404` |
| Swagger `POST /api/v1/jobs` | `201`, created synthetic Job 2 |

## Example Create Response

```json
{
  "id": 2,
  "title": "API Platform Engineer",
  "company": "Sample Labs",
  "location": "Shanghai",
  "description": "Synthetic Swagger demonstration record.",
  "source_url": "https://example.com/jobs/api-platform-engineer",
  "status": "applied",
  "created_at": "2026-09-23T17:36:12.768189",
  "updated_at": "2026-09-23T17:36:12.768192"
}
```

The matching live Swagger response is captured in [`job-api-example.png`](../images/job-api-example.png).

## OpenAPI Verification

The generated document exposed:

- Paths: `/health`, `/api/v1/jobs`, `/api/v1/jobs/{job_id}`
- Operations: create, list, get, update, and delete
- Schemas: `JobCreate`, `JobUpdate`, `JobRead`, `JobList`, `JobStatus`, `ErrorDetail`, `ErrorResponse`, and `HealthResponse`
- Explicit `201`, `204`, `404`, and custom `422` response documentation
