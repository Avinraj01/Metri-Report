import pytest

def test_unauthenticated_request_blocked(client):
    response = client.get("/api/auth/me")
    assert response.status_code == 401

def test_invalid_jwt_token_rejected(client):
    response = client.get("/api/auth/me", headers={"Authorization": "Bearer invalid.jwt.signature"})
    assert response.status_code == 401
    assert "Invalid or expired access token" in response.json()["detail"]

def test_viewer_cannot_register_instrument(client, viewer_headers):
    payload = {
        "instrument_name": "Unauthorized Test Scale",
        "model": "TEST-100",
        "instrument_type": "Platform Scale",
        "serial_number": "UNAUTH-001",
        "manufacturer": "Acme Corp",
        "applicant_name": "Acme Corp",
        "accuracy_class": "III",
        "max_capacity": 1000.0,
        "min_capacity": 10.0,
        "e_value": 0.5,
        "d_value": 0.5,
        "unit": "kg"
    }
    response = client.post("/api/instruments", json=payload, headers=viewer_headers)
    assert response.status_code == 403
    assert "Operation not permitted for role VIEWER" in response.json()["detail"]

def test_viewer_cannot_modify_user_roles(client, viewer_headers, db_session):
    from app.models import User
    target_user = db_session.query(User).filter(User.email == "viewer@metrireport.local").first()
    response = client.put(f"/api/users/{target_user.id}/role", json={"role": "ADMIN"}, headers=viewer_headers)
    assert response.status_code == 403

def test_admin_can_modify_user_roles(client, admin_headers, db_session):
    from app.models import User
    target_user = db_session.query(User).filter(User.email == "viewer@metrireport.local").first()
    response = client.put(f"/api/users/{target_user.id}/role", json={"role": "TEST_ENGINEER"}, headers=admin_headers)
    assert response.status_code == 200
    assert response.json()["role"] == "TEST_ENGINEER"
    # Revert back
    client.put(f"/api/users/{target_user.id}/role", json={"role": "VIEWER"}, headers=admin_headers)
