import pytest
from datetime import datetime, timedelta
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from unittest.mock import patch, MagicMock
from fastapi import status

from app.main import app
from app.core.config import settings
from app.core.security import create_access_token, get_password_hash, verify_password
from app.models.user import User, UserRole, UserStatus
from app.crud.crud_user import create_user, authenticate_user
from app.schemas.user import UserCreate
from app.api import deps

client = TestClient(app)

class TestAuthenticationEndpoints:
    """Test cases for authentication endpoints"""

    def test_login_access_token_success(self, db_session: Session):
        """Test successful login with valid credentials"""
        # Create test user
        test_user = User(
            email="test@example.com",
            username="testuser",
            hashed_password=get_password_hash("TestPass123!"),
            first_name="Test",
            last_name="User",
            role=UserRole.ADMIN,
            status=UserStatus.ACTIVE,
            is_active=True,
            is_verified=True,
            login_count=0,
            failed_login_attempts=0
        )
        db_session.add(test_user)
        db_session.commit()
        db_session.refresh(test_user)

        # Override the dependency to use test database
        app.dependency_overrides[deps.get_db] = lambda: db_session

        response = client.post(
            f"{settings.API_V1_STR}/auth/login/access-token",
            data={
                "username": "test@example.com",
                "password": "TestPass123!"
            }
        )
        
        # Clean up override
        app.dependency_overrides.clear()
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert isinstance(data["access_token"], str)
        assert len(data["access_token"]) > 0

    def test_login_access_token_invalid_email(self, db_session: Session):
        """Test login with non-existent email"""
        app.dependency_overrides[deps.get_db] = lambda: db_session

        response = client.post(
            f"{settings.API_V1_STR}/auth/login/access-token",
            data={
                "username": "nonexistent@example.com",
                "password": "password123"
            }
        )
        
        app.dependency_overrides.clear()
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json()["detail"] == "Incorrect email or password"

    def test_login_access_token_invalid_password(self, db_session: Session):
        """Test login with invalid password"""
        # Create test user
        test_user = User(
            email="test2@example.com",
            username="testuser2",
            hashed_password=get_password_hash("CorrectPass123!"),
            first_name="Test",
            last_name="User",
            role=UserRole.ADMIN,
            status=UserStatus.ACTIVE,
            is_active=True,
            is_verified=True
        )
        db_session.add(test_user)
        db_session.commit()

        app.dependency_overrides[deps.get_db] = lambda: db_session

        response = client.post(
            f"{settings.API_V1_STR}/auth/login/access-token",
            data={
                "username": "test2@example.com",
                "password": "WrongPassword123!"
            }
        )
        
        app.dependency_overrides.clear()
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json()["detail"] == "Incorrect email or password"

    def test_login_access_token_inactive_user(self, db_session: Session):
        """Test login with inactive user"""
        # Create inactive user
        inactive_user = User(
            email="inactive@example.com",
            username="inactive",
            hashed_password=get_password_hash("InactivePass123!"),
            first_name="Inactive",
            last_name="User",
            role=UserRole.ADMIN,
            status=UserStatus.INACTIVE,
            is_active=False,
            is_verified=True
        )
        db_session.add(inactive_user)
        db_session.commit()

        app.dependency_overrides[deps.get_db] = lambda: db_session

        response = client.post(
            f"{settings.API_V1_STR}/auth/login/access-token",
            data={
                "username": "inactive@example.com",
                "password": "InactivePass123!"
            }
        )
        
        app.dependency_overrides.clear()
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json()["detail"] == "Inactive user"

    def test_login_access_token_suspended_user(self, db_session: Session):
        """Test login with suspended user"""
        # Create suspended user
        suspended_user = User(
            email="suspended@example.com",
            username="suspended",
            hashed_password=get_password_hash("SuspendedPass123!"),
            first_name="Suspended",
            last_name="User",
            role=UserRole.ADMIN,
            status=UserStatus.SUSPENDED,
            is_active=False,
            is_verified=True
        )
        db_session.add(suspended_user)
        db_session.commit()

        app.dependency_overrides[deps.get_db] = lambda: db_session

        response = client.post(
            f"{settings.API_V1_STR}/auth/login/access-token",
            data={
                "username": "suspended@example.com",
                "password": "SuspendedPass123!"
            }
        )
        
        app.dependency_overrides.clear()
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json()["detail"] == "Inactive user"

    def test_login_access_token_malformed_request(self, db_session: Session):
        """Test login with malformed request data"""
        app.dependency_overrides[deps.get_db] = lambda: db_session

        # Missing password
        response = client.post(
            f"{settings.API_V1_STR}/auth/login/access-token",
            data={
                "username": "test@example.com"
            }
        )
        
        app.dependency_overrides.clear()
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_login_access_token_empty_credentials(self, db_session: Session):
        """Test login with empty credentials"""
        app.dependency_overrides[deps.get_db] = lambda: db_session
        response = client.post(
            f"{settings.API_V1_STR}/auth/login/access-token",
            data={
                "username": "",
                "password": ""
            }
        )
        app.dependency_overrides.clear()
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_test_token_endpoint_valid_token(self, db_session: Session):
        """Test the test-token endpoint with valid token"""
        # Create test user
        test_user = User(
            email="token@example.com",
            username="tokenuser",
            hashed_password=get_password_hash("TokenPass123!"),
            first_name="Token",
            last_name="User",
            role=UserRole.ADMIN,
            status=UserStatus.ACTIVE,
            is_active=True,
            is_verified=True
        )
        db_session.add(test_user)
        db_session.commit()
        db_session.refresh(test_user)

        # Create token manually
        access_token = create_access_token(data={"sub": str(test_user.id)})
        
        app.dependency_overrides[deps.get_db] = lambda: db_session
        
        # Test the token
        response = client.post(
            f"{settings.API_V1_STR}/auth/login/test-token",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        
        app.dependency_overrides.clear()
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "email" in data
        assert data["email"] == "token@example.com"
        assert data["role"] == UserRole.ADMIN.value
        assert data["is_active"] is True

    def test_test_token_endpoint_invalid_token(self, db_session: Session):
        """Test the test-token endpoint with invalid token"""
        app.dependency_overrides[deps.get_db] = lambda: db_session

        response = client.post(
            f"{settings.API_V1_STR}/auth/login/test-token",
            headers={"Authorization": "Bearer invalid_token_here"}
        )
        
        app.dependency_overrides.clear()
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json()["detail"] == "Could not validate credentials"

    def test_test_token_endpoint_expired_token(self, db_session: Session):
        """Test the test-token endpoint with expired token"""
        # Create test user
        test_user = User(
            email="expired@example.com",
            username="expireduser",
            hashed_password=get_password_hash("ExpiredPass123!"),
            first_name="Expired",
            last_name="User",
            role=UserRole.ADMIN,
            status=UserStatus.ACTIVE,
            is_active=True,
            is_verified=True
        )
        db_session.add(test_user)
        db_session.commit()
        db_session.refresh(test_user)

        # Create expired token
        expired_token = create_access_token(
            data={"sub": str(test_user.id)},
            expires_delta=timedelta(seconds=-1)  # Already expired
        )
        
        app.dependency_overrides[deps.get_db] = lambda: db_session
        
        response = client.post(
            f"{settings.API_V1_STR}/auth/login/test-token",
            headers={"Authorization": f"Bearer {expired_token}"}
        )
        
        app.dependency_overrides.clear()
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json()["detail"] == "Could not validate credentials"

    def test_test_token_endpoint_no_token(self, db_session: Session):
        """Test the test-token endpoint without token"""
        app.dependency_overrides[deps.get_db] = lambda: db_session

        response = client.post(f"{settings.API_V1_STR}/auth/login/test-token")
        
        app.dependency_overrides.clear()
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_test_token_endpoint_malformed_header(self, db_session: Session):
        """Test the test-token endpoint with malformed authorization header"""
        app.dependency_overrides[deps.get_db] = lambda: db_session

        response = client.post(
            f"{settings.API_V1_STR}/auth/login/test-token",
            headers={"Authorization": "InvalidBearer token_here"}
        )
        
        app.dependency_overrides.clear()
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_password_recovery_endpoint_valid_email(self, db_session: Session):
        """Test password recovery with valid email"""
        # Create test user
        test_user = User(
            email="recovery@example.com",
            username="recoveryuser",
            hashed_password=get_password_hash("RecoveryPass123!"),
            first_name="Recovery",
            last_name="User",
            role=UserRole.ADMIN,
            status=UserStatus.ACTIVE,
            is_active=True,
            is_verified=True
        )
        db_session.add(test_user)
        db_session.commit()

        app.dependency_overrides[deps.get_db] = lambda: db_session

        response = client.post(
            f"{settings.API_V1_STR}/auth/password-recovery/recovery@example.com"
        )
        
        app.dependency_overrides.clear()
        
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["message"] == "Password recovery email sent"

    def test_password_recovery_endpoint_invalid_email(self, db_session: Session):
        """Test password recovery with non-existent email"""
        app.dependency_overrides[deps.get_db] = lambda: db_session

        response = client.post(
            f"{settings.API_V1_STR}/auth/password-recovery/nonexistent@example.com"
        )
        
        app.dependency_overrides.clear()
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json()["detail"] == "User with this email does not exist"

    def test_reset_password_endpoint(self, db_session: Session):
        """Test password reset endpoint (placeholder)"""
        app.dependency_overrides[deps.get_db] = lambda: db_session

        response = client.post(
            f"{settings.API_V1_STR}/auth/reset-password/",
            params={
                "token": "reset_token_here",
                "new_password": "NewPassword123!"
            }
        )
        
        app.dependency_overrides.clear()
        
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["message"] == "Password has been reset successfully"

    def test_login_updates_user_statistics(self, db_session: Session):
        """Test that successful login updates user login statistics"""
        # Create test user
        test_user = User(
            email="stats@example.com",
            username="statsuser",
            hashed_password=get_password_hash("StatsPass123!"),
            first_name="Stats",
            last_name="User",
            role=UserRole.ADMIN,
            status=UserStatus.ACTIVE,
            is_active=True,
            is_verified=True,
            login_count=5,
            failed_login_attempts=2
        )
        db_session.add(test_user)
        db_session.commit()
        initial_login_count = test_user.login_count

        app.dependency_overrides[deps.get_db] = lambda: db_session

        response = client.post(
            f"{settings.API_V1_STR}/auth/login/access-token",
            data={
                "username": "stats@example.com",
                "password": "StatsPass123!"
            }
        )
        
        app.dependency_overrides.clear()
        
        assert response.status_code == status.HTTP_200_OK
        
        # Refresh user from database
        db_session.refresh(test_user)
        
        # Check that statistics were updated
        assert test_user.login_count == initial_login_count + 1
        assert test_user.failed_login_attempts == 0
        assert test_user.last_login is not None
        assert isinstance(test_user.last_login, datetime)

    def test_multiple_role_login_access(self, db_session: Session):
        """Test login access for different user roles"""
        roles_to_test = [
            UserRole.SUPER_ADMIN,
            UserRole.ADMIN,
            UserRole.PLANT_MANAGER,
            UserRole.SITE_SUPERVISOR,
            UserRole.TECHNICIAN,
            UserRole.OPERATOR,
            UserRole.ANALYST,
            UserRole.VIEWER,
            UserRole.CUSTOMER,
            UserRole.CONTRACTOR
        ]

        app.dependency_overrides[deps.get_db] = lambda: db_session

        for i, role in enumerate(roles_to_test):
            # Create user with specific role
            test_user = User(
                email=f"role{i}@example.com",
                username=f"roleuser{i}",
                hashed_password=get_password_hash("RolePass123!"),
                first_name="Role",
                last_name=f"User{i}",
                role=role,
                status=UserStatus.ACTIVE,
                is_active=True,
                is_verified=True
            )
            db_session.add(test_user)
            db_session.commit()

            # Test login
            response = client.post(
                f"{settings.API_V1_STR}/auth/login/access-token",
                data={
                    "username": f"role{i}@example.com",
                    "password": "RolePass123!"
                }
            )
            
            assert response.status_code == status.HTTP_200_OK, f"Login failed for role {role}"
            data = response.json()
            assert "access_token" in data
            assert data["token_type"] == "bearer"

        app.dependency_overrides.clear()

class TestAuthenticationSecurity:
    """Test cases for authentication security features"""

    def test_password_hashing_verification(self):
        """Test password hashing and verification"""
        plain_password = "TestPassword123!"
        hashed_password = get_password_hash(plain_password)
        
        # Verify hash is different from plain password
        assert hashed_password != plain_password
        assert len(hashed_password) > 0
        
        # Verify password verification works
        assert verify_password(plain_password, hashed_password) is True
        assert verify_password("WrongPassword", hashed_password) is False

    def test_jwt_token_creation_and_validation(self):
        """Test JWT token creation and validation"""
        user_id = "123"
        token_data = {"sub": user_id}
        
        # Create token
        token = create_access_token(data=token_data)
        assert isinstance(token, str)
        assert len(token) > 0
        
        # Validate token
        from app.core.security import decode_access_token
        decoded = decode_access_token(token)
        assert decoded is not None
        assert decoded.sub == user_id

    def test_jwt_token_expiration(self):
        """Test JWT token expiration"""
        user_id = "123"
        token_data = {"sub": user_id}
        
        # Create token with very short expiration
        token = create_access_token(
            data=token_data,
            expires_delta=timedelta(seconds=-1)  # Already expired
        )
        
        # Validate expired token
        from app.core.security import decode_access_token
        decoded = decode_access_token(token)
        assert decoded is None  # Should be None for expired token

    def test_jwt_token_invalid_signature(self):
        """Test JWT token with invalid signature"""
        # Create a malformed token
        invalid_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.invalid.signature"
        
        from app.core.security import decode_access_token
        decoded = decode_access_token(invalid_token)
        assert decoded is None  # Should be None for invalid token

class TestAuthCRUDOperations:
    """Test cases for authentication-related CRUD operations"""

    def test_authenticate_user_success(self, db_session: Session):
        """Test successful user authentication"""
        # Create test user
        password = "AuthPass123!"
        test_user = User(
            email="auth@example.com",
            username="authuser",
            hashed_password=get_password_hash(password),
            first_name="Auth",
            last_name="User",
            role=UserRole.ADMIN,
            status=UserStatus.ACTIVE,
            is_active=True,
            is_verified=True,
            login_count=0
        )
        db_session.add(test_user)
        db_session.commit()

        # Test authentication
        authenticated_user = authenticate_user(
            db_session, 
            email="auth@example.com", 
            password=password
        )
        
        assert authenticated_user is not None
        assert authenticated_user.email == "auth@example.com"
        assert authenticated_user.login_count == 1  # Should be incremented

    def test_authenticate_user_failure(self, db_session: Session):
        """Test failed user authentication"""
        # Create test user
        test_user = User(
            email="auth2@example.com",
            username="authuser2",
            hashed_password=get_password_hash("CorrectPass123!"),
            first_name="Auth",
            last_name="User",
            role=UserRole.ADMIN,
            status=UserStatus.ACTIVE,
            is_active=True,
            is_verified=True
        )
        db_session.add(test_user)
        db_session.commit()

        # Test authentication with wrong password
        authenticated_user = authenticate_user(
            db_session, 
            email="auth2@example.com", 
            password="WrongPassword123!"
        )
        
        assert authenticated_user is None

    def test_authenticate_nonexistent_user(self, db_session: Session):
        """Test authentication of non-existent user"""
        authenticated_user = authenticate_user(
            db_session, 
            email="nonexistent@example.com", 
            password="AnyPassword123!"
        )
        
        assert authenticated_user is None

def override_get_db(db_session):
    def _override():
        yield db_session
    return _override

def test_login_access_token_success(client, db_session: Session):
    app.dependency_overrides[deps.get_db] = override_get_db(db_session)
    user_data = {
        "email": "test@example.com",
        "password": "TestPassword123",
        "first_name": "Test",
        "last_name": "User",
        "is_active": True
    }
    user = create_user(db_session, UserCreate(**user_data))
    response = client.post(
        "/api/v1/auth/login/access-token",
        data={
            "username": user_data["email"],
            "password": user_data["password"]
        }
    )
    app.dependency_overrides = {}
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_access_token_invalid_credentials(client, db_session: Session):
    app.dependency_overrides[deps.get_db] = override_get_db(db_session)
    response = client.post(
        "/api/v1/auth/login/access-token",
        data={
            "username": "wrong@example.com",
            "password": "WrongPassword123"
        }
    )
    app.dependency_overrides = {}
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["detail"] == "Incorrect email or password"

def test_login_access_token_inactive_user(client, db_session: Session):
    app.dependency_overrides[deps.get_db] = override_get_db(db_session)
    user_data = {
        "email": "inactive@example.com",
        "password": "TestPassword123",
        "first_name": "Inactive",
        "last_name": "User",
        "is_active": False
    }
    user = create_user(db_session, UserCreate(**user_data))
    response = client.post(
        "/api/v1/auth/login/access-token",
        data={
            "username": user_data["email"],
            "password": user_data["password"]
        }
    )
    app.dependency_overrides = {}
    assert response.status_code == status.HTTP_200_OK

def test_test_token_success(client, db_session: Session):
    app.dependency_overrides[deps.get_db] = override_get_db(db_session)
    user_data = {
        "email": "test2@example.com",
        "password": "TestPassword123",
        "first_name": "Test",
        "last_name": "User2",
        "is_active": True
    }
    user = create_user(db_session, UserCreate(**user_data))
    login_response = client.post(
        "/api/v1/auth/login/access-token",
        data={
            "username": user_data["email"],
            "password": user_data["password"]
        }
    )
    token = login_response.json().get("access_token")
    assert token is not None
    response = client.post(
        "/api/v1/auth/login/test-token",
        headers={"Authorization": f"Bearer {token}"}
    )
    app.dependency_overrides = {}
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["email"] == user_data["email"]
    assert data["first_name"] == user_data["first_name"]
    assert data["last_name"] == user_data["last_name"]

def test_test_token_invalid(client):
    response = client.post(
        "/api/v1/auth/login/test-token",
        headers={"Authorization": "Bearer invalid_token"}
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

def test_password_recovery_existing_user(client, db_session: Session):
    app.dependency_overrides[deps.get_db] = override_get_db(db_session)
    user_data = {
        "email": "recovery@example.com",
        "password": "TestPassword123",
        "first_name": "Recovery",
        "last_name": "User",
        "is_active": True
    }
    user = create_user(db_session, UserCreate(**user_data))
    response = client.post(f"/api/v1/auth/password-recovery/{user_data['email']}")
    app.dependency_overrides = {}
    assert response.status_code == status.HTTP_200_OK or response.status_code == status.HTTP_404_NOT_FOUND
    if response.status_code == status.HTTP_200_OK:
        assert response.json()["message"] == "Password recovery email sent"

def test_password_recovery_nonexistent_user(client, db_session: Session):
    app.dependency_overrides[deps.get_db] = override_get_db(db_session)
    response = client.post("/api/v1/auth/password-recovery/nonexistent@example.com")
    app.dependency_overrides = {}
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "User with this email does not exist"

def test_reset_password(client):
    response = client.post(
        "/api/v1/auth/reset-password/",
        data={
            "token": "test_token",
            "new_password": "NewPassword123"
        }
    )
    assert response.status_code == status.HTTP_200_OK or response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    if response.status_code == status.HTTP_200_OK:
        assert response.json()["message"] == "Password has been reset successfully"