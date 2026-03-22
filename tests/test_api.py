import time
import requests
import pytest

from tests.conftest import BASE_URL


# ---------------------------------------------------------------------------
# Happy path tests
# ---------------------------------------------------------------------------

def test_health_endpoint_returns_healthy():
    response = requests.get(f"{BASE_URL}/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_register_user_creates_new_user():
    username = f"newuser_{int(time.time())}"
    response = requests.post(
        f"{BASE_URL}/api/auth/register",
        json={"username": username, "password": "password123"},
    )
    assert response.status_code == 201
    body = response.json()
    assert body["message"] == "User created successfully"
    assert body["user"]["username"] == username


def test_login_returns_jwt_token():
    username = f"loginuser_{int(time.time())}"
    requests.post(
        f"{BASE_URL}/api/auth/register",
        json={"username": username, "password": "password123"},
    )
    response = requests.post(
        f"{BASE_URL}/api/auth/login",
        json={"username": username, "password": "password123"},
    )
    assert response.status_code == 200
    body = response.json()
    assert "access_token" in body
    assert len(body["access_token"]) > 0


def test_create_public_event_requires_auth_and_succeeds_with_token(auth_token):
    response = requests.post(
        f"{BASE_URL}/api/events",
        json={
            "title": "Test Public Event",
            "date": "2026-06-01T18:00:00",
            "is_public": True,
        },
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    assert response.status_code == 201
    body = response.json()
    assert body["title"] == "Test Public Event"
    assert body["is_public"] is True


def test_rsvp_to_public_event_succeeds_without_auth(auth_token):
    # Create a public event first (needs auth)
    create_resp = requests.post(
        f"{BASE_URL}/api/events",
        json={
            "title": "Public RSVP Event",
            "date": "2026-07-01T12:00:00",
            "is_public": True,
        },
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    assert create_resp.status_code == 201
    event_id = create_resp.json()["id"]

    # RSVP without any auth token
    rsvp_resp = requests.post(f"{BASE_URL}/api/rsvps/event/{event_id}", json={})
    assert rsvp_resp.status_code == 201
    assert rsvp_resp.json()["attending"] is True


# ---------------------------------------------------------------------------
# Edge case tests
# ---------------------------------------------------------------------------

def test_duplicate_username_registration_returns_400():
    username = f"dupuser_{int(time.time())}"
    requests.post(
        f"{BASE_URL}/api/auth/register",
        json={"username": username, "password": "password123"},
    )
    response = requests.post(
        f"{BASE_URL}/api/auth/register",
        json={"username": username, "password": "anotherpassword"},
    )
    assert response.status_code == 400
    assert "error" in response.json()


def test_create_event_without_auth_returns_401():
    response = requests.post(
        f"{BASE_URL}/api/events",
        json={"title": "Unauthorized Event", "date": "2026-08-01T10:00:00"},
    )
    assert response.status_code == 401


def test_rsvp_to_non_public_event_without_auth_returns_error(auth_token):
    # Create a private (non-public) event
    create_resp = requests.post(
        f"{BASE_URL}/api/events",
        json={
            "title": "Private Event",
            "date": "2026-09-01T20:00:00",
            "is_public": False,
        },
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    assert create_resp.status_code == 201
    event_id = create_resp.json()["id"]

    # Attempt RSVP without auth
    rsvp_resp = requests.post(f"{BASE_URL}/api/rsvps/event/{event_id}", json={})
    assert rsvp_resp.status_code == 401
    assert "error" in rsvp_resp.json()
