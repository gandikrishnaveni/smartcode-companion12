import pytest
from httpx import AsyncClient
from fastapi import status

from smart_code_companion.main import app
from smart_code_companion.core.config import get_settings

# Base URL for the API. Uses the prefix from config.
BASE_URL = get_settings().API_V1_STR

@pytest.mark.asyncio
async def test_health_check():
    """
    Tests the /health endpoint to ensure it returns a 200 OK status.
    """
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get(f"{BASE_URL}/health")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"status": "ok"}


@pytest.mark.asyncio
@pytest.mark.parametrize("level, expected_keyword", [
    ("beginner", "Beginner"),
    ("intermediate", "Intermediate"),
    ("advanced", "Advanced"),
])
async def test_get_code_comment(level, expected_keyword):
    """
    Tests the /comment endpoint with different skill levels.
    This test uses the default 'mock' AI provider.
    """
    test_code = "def my_function(x):\n    return x * 2"
    request_data = {"code": test_code, "level": level}

    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post(f"{BASE_URL}/comment", json=request_data)

    assert response.status_code == status.HTTP_200_OK
    response_json = response.json()
    assert "comment" in response_json
    assert f"MOCK RESPONSE ({expected_keyword})" in response_json["comment"]


@pytest.mark.asyncio
async def test_get_code_comment_invalid_level():
    """
    Tests the /comment endpoint with an invalid skill level to ensure
    FastAPI's validation returns a 422 Unprocessable Entity error.
    """
    test_code = "def my_function(x):\n    return x * 2"
    request_data = {"code": test_code, "level": "expert"} # "expert" is not a valid level

    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post(f"{BASE_URL}/comment", json=request_data)

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
