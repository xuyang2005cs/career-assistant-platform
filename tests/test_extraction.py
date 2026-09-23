"""Tests for extraction providers, fallback behavior, and the preview API."""

import json

import httpx
import pytest
from httpx import AsyncClient

from app.services.extraction.base import ExtractionProviderError
from app.services.extraction.deepseek import DeepSeekExtractionProvider
from app.services.extraction.mock import MockExtractionProvider
from app.services.extraction.rule_based import RuleBasedExtractionProvider
from app.services.extraction.service import ExtractionService

SYNTHETIC_JD = """Company: Example Tech
Role: Python Backend Intern
Location: Beijing

Requirements:
Python, FastAPI, SQL, Git, and Linux
"""


class FailingProvider:
    """Test double that exercises the production fallback path."""

    async def extract(self, text: str):
        del text
        raise ExtractionProviderError("timeout")


def deepseek_response(content: dict[str, object]) -> httpx.Response:
    return httpx.Response(
        200,
        json={
            "choices": [
                {
                    "message": {
                        "content": json.dumps(content),
                    }
                }
            ]
        },
    )


@pytest.mark.anyio
async def test_rule_based_extraction() -> None:
    result = await RuleBasedExtractionProvider().extract(SYNTHETIC_JD)

    assert result.title == "Python Backend Intern"
    assert result.company == "Example Tech"
    assert result.location == "Beijing"
    assert result.skills == ["Python", "FastAPI", "SQL", "Git", "Linux"]
    assert result.extraction_method == "rule_based"


@pytest.mark.anyio
async def test_rule_based_extraction_handles_unlabeled_title() -> None:
    text = "Backend Engineer\nat Nova Systems\nBuild REST APIs with Python and PostgreSQL."

    result = await RuleBasedExtractionProvider().extract(text)

    assert result.title == "Backend Engineer"
    assert result.company == "Nova Systems"
    assert result.skills == ["Python", "PostgreSQL", "REST"]


@pytest.mark.anyio
async def test_mock_provider_is_explicit() -> None:
    result = await MockExtractionProvider().extract(SYNTHETIC_JD)

    assert result.extraction_method == "mock"
    assert result.model == "mock-provider"
    assert result.company == "Mock Company"


@pytest.mark.anyio
async def test_extraction_service_falls_back_truthfully() -> None:
    service = ExtractionService(FailingProvider(), RuleBasedExtractionProvider())

    result = await service.extract(SYNTHETIC_JD)

    assert result.extraction_method == "rule_based_fallback"
    assert result.fallback_reason == "timeout"
    assert result.title == "Python Backend Intern"


@pytest.mark.anyio
async def test_job_extract_endpoint(client: AsyncClient) -> None:
    response = await client.post("/api/v1/job-extract", json={"text": SYNTHETIC_JD})

    assert response.status_code == 200
    body = response.json()
    assert body["title"] == "Python Backend Intern"
    assert body["company"] == "Example Tech"
    assert body["extraction_method"] == "rule_based"
    assert body["suggested_status"] == "saved"


@pytest.mark.anyio
async def test_job_extract_rejects_empty_input(client: AsyncClient) -> None:
    response = await client.post("/api/v1/job-extract", json={"text": "   "})

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "validation_error"


@pytest.mark.anyio
async def test_job_extract_rejects_overlong_input(client: AsyncClient) -> None:
    response = await client.post("/api/v1/job-extract", json={"text": "x" * 20_001})

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "validation_error"


@pytest.mark.anyio
async def test_deepseek_provider_parses_successful_json() -> None:
    async def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/chat/completions"
        assert request.headers["Authorization"] == "Bearer test-key"
        return deepseek_response(
            {
                "title": "Python Backend Intern",
                "company": "Example Tech",
                "location": "Beijing",
                "skills": ["Python", "FastAPI", "SQL", "Python"],
            }
        )

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as http_client:
        provider = DeepSeekExtractionProvider(
            api_key="test-key",
            base_url="https://api.deepseek.test",
            model="deepseek-test",
            client=http_client,
        )
        result = await provider.extract(SYNTHETIC_JD)

    assert result.extraction_method == "deepseek"
    assert result.model == "deepseek-test"
    assert result.skills == ["Python", "FastAPI", "SQL"]
    assert result.latency_ms is not None


@pytest.mark.anyio
@pytest.mark.parametrize(
    ("status_code", "expected_code"),
    [
        (401, "authentication_error"),
        (429, "rate_limited"),
        (503, "provider_server_error"),
    ],
)
async def test_deepseek_provider_classifies_http_errors(
    status_code: int,
    expected_code: str,
) -> None:
    async def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(status_code, request=request)

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as http_client:
        provider = DeepSeekExtractionProvider(api_key="test-key", client=http_client)
        with pytest.raises(ExtractionProviderError, match=expected_code):
            await provider.extract(SYNTHETIC_JD)


@pytest.mark.anyio
async def test_deepseek_provider_classifies_timeout() -> None:
    async def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ReadTimeout("synthetic timeout", request=request)

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as http_client:
        provider = DeepSeekExtractionProvider(api_key="test-key", client=http_client)
        with pytest.raises(ExtractionProviderError, match="timeout"):
            await provider.extract(SYNTHETIC_JD)


@pytest.mark.anyio
async def test_deepseek_provider_rejects_invalid_json_body() -> None:
    async def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, text="not-json", request=request)

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as http_client:
        provider = DeepSeekExtractionProvider(api_key="test-key", client=http_client)
        with pytest.raises(ExtractionProviderError, match="invalid_response"):
            await provider.extract(SYNTHETIC_JD)


@pytest.mark.anyio
async def test_deepseek_provider_rejects_invalid_message_content() -> None:
    async def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={"choices": [{"message": {"content": "not-json"}}]},
            request=request,
        )

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as http_client:
        provider = DeepSeekExtractionProvider(api_key="test-key", client=http_client)
        with pytest.raises(ExtractionProviderError, match="invalid_response"):
            await provider.extract(SYNTHETIC_JD)
