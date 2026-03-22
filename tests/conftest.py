import time
import requests
import pytest

BASE_URL = "http://localhost:5000"


@pytest.fixture
def auth_token():
    """Register a unique user, log in, and return a valid JWT token."""
    username = f"testuser_{int(time.time())}"
    password = "testpassword123"

    requests.post(
        f"{BASE_URL}/api/auth/register",
        json={"username": username, "password": password},
    )

    response = requests.post(
        f"{BASE_URL}/api/auth/login",
        json={"username": username, "password": password},
    )
    assert response.status_code == 200, f"Login failed: {response.text}"
    return response.json()["access_token"]
