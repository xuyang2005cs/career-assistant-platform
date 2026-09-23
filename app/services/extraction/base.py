"""Provider contracts and safe failure types."""

from typing import Protocol

from app.schemas.extraction import JobExtractionPreview


class ExtractionProviderError(Exception):
    """A provider failure safe to classify without exposing sensitive data."""

    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


class ExtractionProvider(Protocol):
    """Minimal asynchronous provider contract."""

    async def extract(self, text: str) -> JobExtractionPreview:
        """Convert job-description text into a structured preview."""


class UnavailableExtractionProvider:
    """Provider placeholder that triggers a truthful fallback reason."""

    def __init__(self, reason: str) -> None:
        self.reason = reason

    async def extract(self, text: str) -> JobExtractionPreview:
        del text
        raise ExtractionProviderError(self.reason)
