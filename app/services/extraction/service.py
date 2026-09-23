"""Extraction provider selection and truthful fallback orchestration."""

from functools import lru_cache

from app.core.config import Settings, get_settings
from app.schemas.extraction import JobExtractionPreview
from app.services.extraction.base import (
    ExtractionProvider,
    ExtractionProviderError,
    UnavailableExtractionProvider,
)
from app.services.extraction.deepseek import (
    DEFAULT_BASE_URL,
    DEFAULT_MODEL,
    DeepSeekExtractionProvider,
)
from app.services.extraction.mock import MockExtractionProvider
from app.services.extraction.rule_based import RuleBasedExtractionProvider


class ExtractionService:
    """Run one provider and optionally fall back to deterministic extraction."""

    def __init__(
        self,
        primary: ExtractionProvider,
        fallback: ExtractionProvider | None = None,
    ) -> None:
        self.primary = primary
        self.fallback = fallback

    async def extract(self, text: str) -> JobExtractionPreview:
        try:
            return await self.primary.extract(text)
        except ExtractionProviderError as exc:
            if self.fallback is None:
                raise
            fallback_result = await self.fallback.extract(text)
            return fallback_result.model_copy(
                update={
                    "extraction_method": "rule_based_fallback",
                    "fallback_reason": exc.code,
                }
            )


def build_extraction_service(settings: Settings) -> ExtractionService:
    """Build the configured provider graph without probing external systems."""

    rule_based = RuleBasedExtractionProvider()
    provider_name = settings.extraction_provider
    api_key = (
        settings.deepseek_api_key.get_secret_value().strip()
        if settings.deepseek_api_key is not None
        else ""
    )

    if provider_name == "rule_based":
        return ExtractionService(rule_based)
    if provider_name == "mock":
        if settings.app_env in {"development", "test"}:
            return ExtractionService(MockExtractionProvider())
        return ExtractionService(
            UnavailableExtractionProvider("mock_not_allowed"),
            fallback=rule_based,
        )

    wants_deepseek = provider_name == "deepseek" or (provider_name == "auto" and api_key)
    if wants_deepseek:
        if not api_key:
            return ExtractionService(
                UnavailableExtractionProvider("missing_api_key"),
                fallback=rule_based,
            )
        deepseek = DeepSeekExtractionProvider(
            api_key=api_key,
            base_url=settings.deepseek_base_url or DEFAULT_BASE_URL,
            model=settings.deepseek_model or DEFAULT_MODEL,
            timeout_seconds=settings.deepseek_timeout_seconds,
        )
        return ExtractionService(deepseek, fallback=rule_based)

    return ExtractionService(rule_based)


@lru_cache
def get_extraction_service() -> ExtractionService:
    """Return the provider graph selected from process configuration."""

    return build_extraction_service(get_settings())
