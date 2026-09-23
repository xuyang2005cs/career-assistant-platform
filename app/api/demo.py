"""Lightweight portfolio demonstration page."""

from pathlib import Path

from fastapi import APIRouter
from fastapi.responses import FileResponse

router = APIRouter(tags=["demo"])
DEMO_PAGE = Path(__file__).resolve().parents[1] / "static" / "demo.html"


@router.get("/demo", response_class=FileResponse, include_in_schema=False)
def demo_page() -> FileResponse:
    """Serve the static Job tracker and extraction workflow."""

    return FileResponse(DEMO_PAGE)
