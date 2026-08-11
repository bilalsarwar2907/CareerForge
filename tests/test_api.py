import pytest
from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)


# --- Auth ---

def test_register():
    response = client.post("/auth/register", json={
        "username": "testuser_api",
        "password": "testpass123"
    })
    # 200 registered or 400 if already exists from a previous run
    assert response.status_code in (200, 400)


def test_login():
    # Ensure user exists first
    client.post("/auth/register", json={
        "username": "testuser_api",
        "password": "testpass123"
    })
    response = client.post("/auth/login", json={
        "username": "testuser_api",
        "password": "testpass123"
    })
    assert response.status_code == 200
    assert "access_token" in response.json()


def test_login_wrong_password():
    response = client.post("/auth/login", json={
        "username": "testuser_api",
        "password": "wrongpassword"
    })
    assert response.status_code == 401


# --- Helper to get token ---

def get_token():
    client.post("/auth/register", json={
        "username": "testuser_api",
        "password": "testpass123"
    })
    response = client.post("/auth/login", json={
        "username": "testuser_api",
        "password": "testpass123"
    })
    return response.json()["access_token"]


# --- Protected routes ---

def test_protected_route_without_token():
    response = client.get("/applications")
    assert response.status_code == 401

def test_get_applications():
    token = get_token()
    response = client.get(
        "/applications",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_create_application():
    token = get_token()
    response = client.post(
        "/applications",
        json={"company": "TestCo", "role": "Dev", "status": "applied"},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert response.json()["saved"] is True


def test_search_jobs():
    token = get_token()
    response = client.get(
        "/jobs/search?keywords=python",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert isinstance(response.json(), list)


# --- Health ---

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"