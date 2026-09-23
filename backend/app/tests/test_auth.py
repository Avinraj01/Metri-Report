from unittest.mock import patch
from app.models import RoleEnum, AuthProviderEnum

def test_local_login_success(client):
    response = client.post("/api/auth/login", json={
        "email": "engineer@metrireport.local",
        "password": "engineer123"
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["role"] == "TEST_ENGINEER"
    assert data["auth_provider"] == "LOCAL"

def test_local_login_invalid_password(client):
    response = client.post("/api/auth/login", json={
        "email": "engineer@metrireport.local",
        "password": "wrongpassword"
    })
    assert response.status_code == 401
    assert "Invalid email or password" in response.json()["detail"]

def test_google_login_new_user_safe_role(client):
    mock_payload = {
        "sub": "google-oauth2|999888777",
        "email": "dr.patel@nationalmetrology.gov.in",
        "email_verified": True,
        "name": "Dr. K. Patel",
        "picture": "https://lh3.googleusercontent.com/a/sample-avatar"
    }
    with patch("app.api.auth.verify_google_token", return_value=mock_payload):
        response = client.post("/api/auth/google", json={"id_token": "valid-mock-google-token"})
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "dr.patel@nationalmetrology.gov.in"
        assert data["role"] == "VIEWER"  # Safe default role!
        assert data["auth_provider"] == "GOOGLE"

def test_google_login_account_linking(client):
    # Existing engineer email logs in via Google
    mock_payload = {
        "sub": "google-oauth2|123456789",
        "email": "engineer@metrireport.local",
        "email_verified": True,
        "name": "Avinash Kumar (Google)",
        "picture": "https://avatar.google.com/test"
    }
    with patch("app.api.auth.verify_google_token", return_value=mock_payload):
        response = client.post("/api/auth/google", json={"id_token": "valid-google-token-link"})
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "engineer@metrireport.local"
        assert data["role"] == "TEST_ENGINEER"  # Retains existing role!
        assert data["auth_provider"] in ["HYBRID", "LOCAL"]

def test_google_login_invalid_or_unverified_token(client):
    with patch("app.api.auth.verify_google_token", return_value=None):
        response = client.post("/api/auth/google", json={"id_token": "tampered-token"})
        assert response.status_code == 401
        assert "Invalid, expired or unverified" in response.json()["detail"]

def test_get_current_user_profile(client, engineer_headers):
    response = client.get("/api/auth/me", headers=engineer_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "engineer@metrireport.local"
    assert data["role"] == "TEST_ENGINEER"
