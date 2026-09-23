"""Deterministic, offline job-description extraction."""

import re

from app.schemas.extraction import JobExtractionPreview

FIELD_PATTERNS = {
    "title": re.compile(
        r"^\s*(?:job\s+title|role|title|position)\s*[:\-]\s*(?P<value>.+?)\s*$",
        re.IGNORECASE | re.MULTILINE,
    ),
    "company": re.compile(
        r"^\s*(?:company|organization|employer)\s*[:\-]\s*(?P<value>.+?)\s*$",
        re.IGNORECASE | re.MULTILINE,
    ),
    "location": re.compile(
        r"^\s*(?:location|workplace)\s*[:\-]\s*(?P<value>.+?)\s*$",
        re.IGNORECASE | re.MULTILINE,
    ),
}

SKILL_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("Python", re.compile(r"\bpython\b", re.IGNORECASE)),
    ("FastAPI", re.compile(r"\bfastapi\b", re.IGNORECASE)),
    ("SQL", re.compile(r"\bsql\b", re.IGNORECASE)),
    ("SQLAlchemy", re.compile(r"\bsqlalchemy\b", re.IGNORECASE)),
    ("Pytest", re.compile(r"\bpytest\b", re.IGNORECASE)),
    ("Git", re.compile(r"\bgit\b", re.IGNORECASE)),
    ("Linux", re.compile(r"\blinux\b", re.IGNORECASE)),
    ("Java", re.compile(r"\bjava\b", re.IGNORECASE)),
    ("JavaScript", re.compile(r"\bjavascript\b", re.IGNORECASE)),
    ("Docker", re.compile(r"\bdocker\b", re.IGNORECASE)),
    ("AWS", re.compile(r"\baws\b", re.IGNORECASE)),
    ("MySQL", re.compile(r"\bmysql\b", re.IGNORECASE)),
    ("PostgreSQL", re.compile(r"\bpostgres(?:ql)?\b", re.IGNORECASE)),
    ("REST", re.compile(r"\brest(?:ful)?\b", re.IGNORECASE)),
)

TITLE_HINT = re.compile(
    r"^\s*(?P<value>.+?\b(?:intern|engineer|developer|analyst|scientist|tester))\s*$",
    re.IGNORECASE | re.MULTILINE,
)
COMPANY_HINT = re.compile(
    r"\bat\s+(?P<value>[A-Z][A-Za-z0-9&.' -]{1,80})",
)


def _clean_value(value: str | None) -> str | None:
    if value is None:
        return None
    cleaned = value.strip().strip("-*• ")
    return cleaned or None


def _extract_field(text: str, field_name: str) -> str | None:
    match = FIELD_PATTERNS[field_name].search(text)
    return _clean_value(match.group("value")) if match else None


class RuleBasedExtractionProvider:
    """Extract labeled fields and known skills without network access."""

    async def extract(self, text: str) -> JobExtractionPreview:
        title = _extract_field(text, "title")
        company = _extract_field(text, "company")
        location = _extract_field(text, "location")

        if title is None:
            title_match = TITLE_HINT.search(text)
            title = _clean_value(title_match.group("value")) if title_match else None
        if company is None:
            company_match = COMPANY_HINT.search(text)
            company = _clean_value(company_match.group("value")) if company_match else None

        skills = [name for name, pattern in SKILL_PATTERNS if pattern.search(text)]

        return JobExtractionPreview(
            title=title,
            company=company,
            location=location,
            description=text,
            skills=skills,
            extraction_method="rule_based",
        )
