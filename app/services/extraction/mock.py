"""Deterministic extraction provider for tests and local demonstrations."""

from app.schemas.extraction import JobExtractionPreview


class MockExtractionProvider:
    """Return an explicit mock result; never impersonate a real model."""

    async def extract(self, text: str) -> JobExtractionPreview:
        return JobExtractionPreview(
            title="Mock Backend Intern",
            company="Mock Company",
            location="Remote",
            description=text,
            skills=["Python", "FastAPI"],
            extraction_method="mock",
            model="mock-provider",
            latency_ms=0,
        )
