"""Unit and API integration tests for Authentication & Production Backend Hardening."""

import pytest
from app.core.security import hash_password, verify_password, create_access_token, decode_access_token
from app.db.models import User


def test_password_hashing_and_verification():
    """Test salted password hashing and verification."""
    raw_pass = "MySecretPass123!"
    hashed = hash_password(raw_pass)

    assert hashed != raw_pass
    assert ":" in hashed
    assert verify_password(raw_pass, hashed) is True
    assert verify_password("WrongPassword", hashed) is False


def test_jwt_token_generation_and_decoding():
    """Test JWT token encoding and decoding."""
    payload = {"sub": "1001", "email": "test@edusense.ai", "role": "student"}
    token = create_access_token(payload)

    assert isinstance(token, str)
    decoded = decode_access_token(token)
    assert decoded["sub"] == "1001"
    assert decoded["email"] == "test@edusense.ai"


def test_post_auth_register_api(client, db_session):
    """Test POST /auth/register API endpoint."""
    payload = {
        "name": "Auth Student",
        "email": "authstudent@example.com",
        "password": "Password123!",
        "role": "student",
    }

    response = client.post("/auth/register", json=payload)
    assert response.status_code == 201
    data = response.json()

    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["email"] == "authstudent@example.com"
    assert data["role"] == "student"

    # Verify user in database
    db_user = db_session.query(User).filter(User.email == "authstudent@example.com").first()
    assert db_user is not None
    assert verify_password("Password123!", db_user.hashed_password) is True


def test_post_auth_login_api(client, db_session):
    """Test POST /auth/login API endpoint."""
    user = User(
        id=701,
        name="Login Student",
        email="loginstudent@example.com",
        hashed_password=hash_password("LoginPass123!"),
        role="student",
    )
    db_session.add(user)
    db_session.commit()

    # Successful login
    login_payload = {
        "email": "loginstudent@example.com",
        "password": "LoginPass123!",
    }
    response = client.post("/auth/login", json=login_payload)
    assert response.status_code == 200
    data = response.json()

    assert "access_token" in data
    assert data["user_id"] == 701

    # Failed login with wrong password
    bad_response = client.post("/auth/login", json={"email": "loginstudent@example.com", "password": "WrongPassword"})
    assert bad_response.status_code == 401


def test_get_auth_me_protected_api(client, db_session):
    """Test GET /auth/me authenticated endpoint with Bearer header."""
    user = User(
        id=702,
        name="Me Learner",
        email="melearner@example.com",
        hashed_password=hash_password("MePass123!"),
        role="student",
    )
    db_session.add(user)
    db_session.commit()

    token = create_access_token({"sub": "702", "email": "melearner@example.com", "role": "student"})

    # Authorized call
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/auth/me", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 702
    assert data["email"] == "melearner@example.com"

    # Unauthorized call without token
    unauth_response = client.get("/auth/me")
    assert unauth_response.status_code == 401


def test_request_id_middleware(client):
    """Test X-Request-ID response header injection."""
    response = client.get("/health")
    assert response.status_code == 200
    assert "X-Request-ID" in response.headers
    assert len(response.headers["X-Request-ID"]) > 10
