"""Optional DeepSeek JSON extraction provider."""

import json
from time import perf_counter
from typing import Any

import httpx
from pydantic import ValidationError

from app.schemas.extraction import DeepSeekExtractionPayload, JobExtractionPreview
from app.services.extraction.base import ExtractionProviderError

DEFAULT_BASE_URL = "https://api.deepseek.com"
DEFAULT_MODEL = "deepseek-flash"


class DeepSeekExtractionProvider:
    """Call DeepSeek's OpenAI-compatible chat-completions API."""

    def __init__(
        self,
        *,
        api_key: str,
        base_url: str = DEFAULT_BASE_URL,
        model: str = DEFAULT_MODEL,
        timeout_seconds: float = 10.0,
        client: httpx.AsyncClient | None = None,
    ) -> None:
        self.api_key = api_key
        self.base_url = base_url.rstrip("/") or DEFAULT_BASE_URL
        self.model = model.strip() or DEFAULT_MODEL
        self.timeout_seconds = timeout_seconds
        self.client = client

    async def extract(self, text: str) -> JobExtractionPreview:
        started = perf_counter()
        client = self.client or httpx.AsyncClient(timeout=self.timeout_seconds)
        owns_client = self.client is None

        try:
            response = await client.post(
                f"{self.base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json=self._request_payload(text),
            )
            self._raise_for_status(response)
            result = self._parse_response(response, text)
        except httpx.TimeoutException as exc:
            raise ExtractionProviderError("timeout") from exc
        except httpx.RequestError as exc:
            raise ExtractionProviderError("network_error") from exc
        finally:
            if owns_client:
                await client.aclose()

        latency_ms = max(0, round((perf_counter() - started) * 1000))
        return result.model_copy(update={"latency_ms": latency_ms})

    def _request_payload(self, text: str) -> dict[str, Any]:
        system_prompt = (
            "Extract a job description into JSON. Return only an object with keys "
            "title, company, location, and skills. Use null when a field is unknown. "
            "skills must be an array of concise technology names."
        )
        return {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": text},
            ],
            "response_format": {"type": "json_object"},
            "stream": False,
            "temperature": 0,
        }

    @staticmethod
    def _raise_for_status(response: httpx.Response) -> None:
        if response.status_code == 401:
            raise ExtractionProviderError("authentication_error")
        if response.status_code == 429:
            raise ExtractionProviderError("rate_limited")
        if 500 <= response.status_code:
            raise ExtractionProviderError("provider_server_error")
        if response.is_error:
            raise ExtractionProviderError("provider_http_error")

    def _parse_response(self, response: httpx.Response, text: str) -> JobExtractionPreview:
        try:
            response_data = response.json()
            content = response_data["choices"][0]["message"]["content"]
            payload = DeepSeekExtractionPayload.model_validate(json.loads(content))
        except (ValueError, KeyError, IndexError, TypeError, ValidationError) as exc:
            raise ExtractionProviderError("invalid_response") from exc

        skills = list(dict.fromkeys(skill.strip() for skill in payload.skills if skill.strip()))
        return JobExtractionPreview(
            title=payload.title,
            company=payload.company,
            location=payload.location,
            description=text,
            skills=skills,
            extraction_method="deepseek",
            model=self.model,
        )
