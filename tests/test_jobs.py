"""Integration tests for the Job REST API."""

from typing import Any

import pytest
from httpx import AsyncClient, Response


def job_payload(**overrides: Any) -> dict[str, Any]:
    """Build fictional job data suitable for tests and demonstrations."""

    payload: dict[str, Any] = {
        "title": "Python Backend Intern",
        "company": "Example Tech",
        "location": "Remote",
        "description": "Build and test reliable API services.",
        "source_url": "https://example.com/jobs/backend-intern",
        "status": "saved",
    }
    payload.update(overrides)
    return payload


async def create_job(client: AsyncClient, **overrides: Any) -> Response:
    """Create a fictional job through the public API."""

    return await client.post("/api/v1/jobs", json=job_payload(**overrides))


@pytest.mark.anyio
async def test_create_job_success(client: AsyncClient) -> None:
    response = await create_job(client)

    assert response.status_code == 201
    body = response.json()
    assert body["id"] == 1
    assert body["title"] == "Python Backend Intern"
    assert body["company"] == "Example Tech"
    assert body["status"] == "saved"
    assert body["created_at"]
    assert body["updated_at"]


@pytest.mark.anyio
async def test_create_job_rejects_blank_title(client: AsyncClient) -> None:
    response = await create_job(client, title="   ")

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "validation_error"


@pytest.mark.anyio
async def test_create_job_rejects_invalid_url(client: AsyncClient) -> None:
    response = await create_job(client, source_url="not-a-url")

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "validation_error"


@pytest.mark.anyio
async def test_list_jobs(client: AsyncClient) -> None:
    await create_job(client)
    await create_job(client, title="API Engineer", company="Sample Labs")

    response = await client.get("/api/v1/jobs")

    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 2
    assert body["page"] == 1
    assert body["page_size"] == 20
    assert len(body["items"]) == 2


@pytest.mark.anyio
async def test_list_jobs_paginates(client: AsyncClient) -> None:
    for index in range(3):
        await create_job(client, title=f"Backend Role {index + 1}")

    response = await client.get("/api/v1/jobs", params={"page": 2, "page_size": 2})

    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 3
    assert body["page"] == 2
    assert body["page_size"] == 2
    assert len(body["items"]) == 1


@pytest.mark.anyio
async def test_list_jobs_rejects_invalid_pagination(client: AsyncClient) -> None:
    response = await client.get("/api/v1/jobs", params={"page": 0, "page_size": 101})

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "validation_error"


@pytest.mark.anyio
async def test_filter_jobs_by_company(client: AsyncClient) -> None:
    await create_job(client, company="Example Tech")
    await create_job(client, company="Sample Labs", title="Platform Engineer")

    response = await client.get("/api/v1/jobs", params={"company": "example tech"})

    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 1
    assert body["items"][0]["company"] == "Example Tech"


@pytest.mark.anyio
async def test_filter_jobs_by_status(client: AsyncClient) -> None:
    await create_job(client, status="saved")
    await create_job(client, status="applied", title="Applied Role")

    response = await client.get("/api/v1/jobs", params={"status": "applied"})

    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 1
    assert body["items"][0]["status"] == "applied"


@pytest.mark.anyio
async def test_filter_jobs_by_location(client: AsyncClient) -> None:
    await create_job(client, location="Remote")
    await create_job(client, location="Shanghai", title="Local Backend Role")

    response = await client.get("/api/v1/jobs", params={"location": "shanghai"})

    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 1
    assert body["items"][0]["location"] == "Shanghai"


@pytest.mark.anyio
async def test_get_existing_job(client: AsyncClient) -> None:
    created = await create_job(client)
    job_id = created.json()["id"]

    response = await client.get(f"/api/v1/jobs/{job_id}")

    assert response.status_code == 200
    assert response.json()["id"] == job_id


@pytest.mark.anyio
async def test_get_missing_job_returns_404(client: AsyncClient) -> None:
    response = await client.get("/api/v1/jobs/999")

    assert response.status_code == 404
    assert response.json() == {
        "error": {
            "code": "job_not_found",
            "message": "Job 999 was not found",
        }
    }


@pytest.mark.anyio
async def test_update_job(client: AsyncClient) -> None:
    created = await create_job(client)
    job_id = created.json()["id"]

    response = await client.patch(
        f"/api/v1/jobs/{job_id}",
        json={"status": "interview", "location": "Shanghai"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "interview"
    assert body["location"] == "Shanghai"


@pytest.mark.anyio
async def test_update_job_rejects_invalid_status(client: AsyncClient) -> None:
    created = await create_job(client)
    job_id = created.json()["id"]

    response = await client.patch(
        f"/api/v1/jobs/{job_id}",
        json={"status": "unknown"},
    )

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "validation_error"


@pytest.mark.anyio
async def test_update_job_rejects_empty_patch(client: AsyncClient) -> None:
    created = await create_job(client)
    job_id = created.json()["id"]

    response = await client.patch(f"/api/v1/jobs/{job_id}", json={})

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "validation_error"


@pytest.mark.anyio
async def test_delete_job(client: AsyncClient) -> None:
    created = await create_job(client)
    job_id = created.json()["id"]

    response = await client.delete(f"/api/v1/jobs/{job_id}")

    assert response.status_code == 204
    assert response.content == b""
    get_response = await client.get(f"/api/v1/jobs/{job_id}")
    assert get_response.status_code == 404


@pytest.mark.anyio
async def test_delete_missing_job_returns_404(client: AsyncClient) -> None:
    response = await client.delete("/api/v1/jobs/999")

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "job_not_found"
