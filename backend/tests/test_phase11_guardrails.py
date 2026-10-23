"""Focused regression checks for the hardening boundary."""
from app.services.auth_service import create_access_token


def test_access_scope_is_required(client):
    token = create_access_token(999999, "student")
    response = client.get("/auth/me", headers={"X-Auth-Token": token})
    assert response.status_code == 401
    assert response.json()["detail"] == "User not found"


def test_query_access_token_fallback(client):
    client.post("/auth/register", json={"name": "Query", "email": "query@example.com", "password": "password123", "role": "student"})
    token = client.post("/auth/login", json={"email": "query@example.com", "password": "password123"}).json()["access_token"]
    assert client.get("/auth/me", params={"access_token": token}).status_code == 200
