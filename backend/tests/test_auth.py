import pyotp
from fastapi.testclient import TestClient

from app.services.auth_service import create_temp_token


def _register(client: TestClient, email: str, role: str = "student"):
    return client.post(
        "/auth/register",
        json={"name": "Test User", "email": email, "password": "password123", "role": role},
    )


def _login(client: TestClient, email: str, password: str = "password123"):
    return client.post("/auth/login", json={"email": email, "password": password})


def test_register(client):
    r = _register(client, "student@example.com")
    assert r.status_code == 201
    data = r.json()
    assert data["email"] == "student@example.com"
    assert data["role"] == "student"
    assert "password_hash" not in data


def test_register_duplicate_email(client):
    _register(client, "dup@example.com")
    r = _register(client, "dup@example.com")
    assert r.status_code == 409
    assert "already registered" in r.json()["detail"]


def test_login_wrong_password(client):
    _register(client, "wrongpass@example.com")
    r = _login(client, "wrongpass@example.com", "badpassword")
    assert r.status_code == 401


def test_full_2fa_flow(client):
    register_resp = _register(client, "2fa@example.com")
    assert register_resp.status_code == 201

    login_resp = _login(client, "2fa@example.com")
    assert login_resp.status_code == 200
    assert login_resp.json().get("access_token")

    token = login_resp.json()["access_token"]

    setup_resp = client.post("/auth/2fa/setup", headers={"Authorization": f"Bearer {token}"})
    assert setup_resp.status_code == 200
    setup_data = setup_resp.json()
    assert setup_data["otpauth_uri"]
    assert setup_data["qr_code"].startswith("data:image/png;base64,")
    secret = setup_data["secret"]

    code = pyotp.TOTP(secret).now()
    verify_resp = client.post(
        "/auth/2fa/verify",
        headers={"Authorization": f"Bearer {token}"},
        json={"code": code},
    )
    assert verify_resp.status_code == 200
    assert verify_resp.json()["message"] == "2FA enabled successfully"

    me_resp = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me_resp.json()["totp_enabled"] is True

    second_login = _login(client, "2fa@example.com")
    assert second_login.status_code == 200
    assert second_login.json()["requires_2fa"] is True
    temp_token = second_login.json()["temp_token"]

    totp_code = pyotp.TOTP(secret).now()
    two_fa_login = client.post(
        "/auth/2fa/login", json={"temp_token": temp_token, "code": totp_code}
    )
    assert two_fa_login.status_code == 200
    full_token = two_fa_login.json()["access_token"]

    me_after = client.get("/auth/me", headers={"Authorization": f"Bearer {full_token}"})
    assert me_after.status_code == 200
    assert me_after.json()["email"] == "2fa@example.com"


def test_two_fa_token_cannot_access_normal_routes(client):
    _register(client, "scoped@example.com")
    temp = create_temp_token(1)
    r = client.get("/auth/me", headers={"Authorization": f"Bearer {temp}"})
    assert r.status_code == 401
    assert "scope" in r.json()["detail"]


def test_role_guard_403(client):
    from fastapi import Depends, FastAPI
    from app.main import app
    from app.deps import require_role

    @app.get("/_test/teacher-only")
    def teacher_only(_=Depends(require_role("teacher"))):
        return {"ok": True}

    _register(client, "student-role@example.com", role="student")
    login = _login(client, "student-role@example.com")
    token = login.json()["access_token"]

    r = client.get("/_test/teacher-only", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 403
    assert "teacher" in r.json()["detail"]
