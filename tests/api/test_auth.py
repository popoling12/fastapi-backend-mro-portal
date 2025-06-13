import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.main import app
from app.core.config import settings
from app.models.user import User, UserRole, UserStatus
from app.core.security import get_password_hash

client = TestClient(app)

def test_login_access_token_success(client: TestClient, db_session: Session):
    """Test successful login with valid credentials"""
    # Create test user
    test_user = User(
        email="test@example.com",
        username="testuser",
        hashed_password=get_password_hash("testpass123"),
        first_name="Test",
        last_name="User",
        role=UserRole.ADMIN,
        status=UserStatus.ACTIVE,
        is_active=True,
        is_verified=True
    )
    db_session.add(test_user)
    db_session.commit()

    response = client.post(
        "/api/v1/auth/login/access-token",
        data={
            "username": "test@example.com",
            "password": "testpass123"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_access_token_invalid_credentials(client: TestClient, db_session: Session):
    """Test login with invalid credentials"""
    response = client.post(
        "/api/v1/auth/login/access-token",
        data={
            "username": "test@example.com",
            "password": "wrongpassword"
        }
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect email or password"

def test_login_access_token_inactive_user(client: TestClient, db_session: Session):
    """Test login with inactive user"""
    # Create inactive user
    inactive_user = User(
        email="inactive@example.com",
        username="inactive",
        hashed_password=get_password_hash("password123"),
        first_name="Inactive",
        last_name="User",
        role=UserRole.ADMIN,
        status=UserStatus.INACTIVE,
        is_active=False,
        is_verified=True
    )
    db_session.add(inactive_user)
    db_session.commit()

    response = client.post(
        "/api/v1/auth/login/access-token",
        data={
            "username": "inactive@example.com",
            "password": "password123"
        }
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Inactive user"

def test_test_token_endpoint(client: TestClient, db_session: Session):
    """Test the test-token endpoint with valid token"""
    # Create test user
    test_user = User(
        email="token@example.com",
        username="tokenuser",
        hashed_password=get_password_hash("tokenpass123"),
        first_name="Token",
        last_name="User",
        role=UserRole.ADMIN,
        status=UserStatus.ACTIVE,
        is_active=True,
        is_verified=True
    )
    db_session.add(test_user)
    db_session.commit()

    # First login to get token
    login_response = client.post(
        "/api/v1/auth/login/access-token",
        data={
            "username": "token@example.com",
            "password": "tokenpass123"
        }
    )
    token = login_response.json()["access_token"]
    
    # Test the token
    response = client.post(
        "/api/v1/auth/login/test-token",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "email" in data
    assert data["email"] == "token@example.com"

def test_test_token_endpoint_invalid_token(client: TestClient):
    """Test the test-token endpoint with invalid token"""
    response = client.post(
        "/api/v1/auth/login/test-token",
        headers={"Authorization": "Bearer invalid_token"}
    )
    assert response.status_code == 401 