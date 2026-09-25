"""Smoke tests for the lightweight demonstration page."""

import pytest
from httpx import AsyncClient


@pytest.mark.anyio
async def test_demo_page_loads(client: AsyncClient) -> None:
    response = await client.get("/demo")

    assert response.status_code == 200
    assert "Career Assistant Platform" in response.text
    assert "职位信息提取" in response.text
    assert "/static/demo.css" in response.text


@pytest.mark.anyio
@pytest.mark.parametrize("asset", ["demo.css", "demo.js"])
async def test_demo_assets_load(client: AsyncClient, asset: str) -> None:
    response = await client.get(f"/static/{asset}")

    assert response.status_code == 200
    assert response.content
