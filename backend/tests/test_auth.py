"""
Authentication Tests

Tests for JWT authentication endpoints including:
- User registration (POST /api/auth/register)
- User login (POST /api/auth/login)
- JWT verification (GET /api/auth/verify)

@see specs/003-backend-auth-refactor/contracts/auth-api.yaml
"""

import uuid
from datetime import datetime, timedelta, timezone

import jwt
import pytest
from httpx import ASGITransport, AsyncClient
from sqlmodel import Session, SQLModel, create_engine, select
from sqlmodel.pool import StaticPool

from src.config import get_settings
from src.database import get_db
from src.main import app
from src.models.user import User

# Get settings for test configuration
settings = get_settings()


# Test database setup
@pytest.fixture(name="session")
def session_fixture():
    """Create a test database session with in-memory SQLite."""
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(session: Session):
    """Create a test client with dependency overrides."""

    def get_session_override():
        return session

    app.dependency_overrides[get_db] = get_session_override
    transport = ASGITransport(app=app)
    client = AsyncClient(transport=transport, base_url="http://test")
    yield client
    app.dependency_overrides.clear()


def create_test_token(
    user_id: str = "test-user-123",
    email: str = "test@example.com",
    expired: bool = False,
    invalid_secret: bool = False,
) -> str:
    """
    Create a JWT token for testing.

    Args:
        user_id: User ID to include in token
        email: Email to include in token
        expired: If True, create an expired token
        invalid_secret: If True, sign with wrong secret

    Returns:
        JWT token string
    """
    now = datetime.now(timezone.utc)

    if expired:
        exp = now - timedelta(hours=1)  # Expired 1 hour ago
    else:
        exp = now + timedelta(hours=24)  # Valid for 24 hours

    payload = {
        "sub": user_id,
        "email": email,
        "iat": now,
        "exp": exp,
    }

    secret = "wrong-secret" if invalid_secret else settings.BETTER_AUTH_SECRET

    return jwt.encode(payload, secret, algorithm="HS256")


@pytest.fixture
def anyio_backend():
    return "asyncio"


# =============================================================================
# User Story 1: User Registration Tests
# =============================================================================


@pytest.mark.anyio
async def test_register_success(client: AsyncClient):
    """Test successful user registration."""
    response = await client.post(
        "/api/auth/register",
        json={"name": "New User", "email": "newuser@example.com", "password": "password123"},
    )

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["name"] == "New User"
    assert data["user"]["email"] == "newuser@example.com"
    assert "id" in data["user"]


@pytest.mark.anyio
async def test_register_duplicate_email(client: AsyncClient):
    """Test 409 response when email is already registered."""
    # First registration
    await client.post(
        "/api/auth/register",
        json={"name": "First User", "email": "duplicate@example.com", "password": "password123"},
    )

    # Second registration with same email
    response = await client.post(
        "/api/auth/register",
        json={"name": "Second User", "email": "duplicate@example.com", "password": "password456"},
    )

    assert response.status_code == 409
    data = response.json()
    assert "already registered" in data["detail"].lower()


@pytest.mark.anyio
async def test_register_short_password(client: AsyncClient):
    """Test 400 response for password less than 8 characters."""
    response = await client.post(
        "/api/auth/register",
        json={"name": "Test User", "email": "user@example.com", "password": "short"},
    )

    assert response.status_code == 422  # FastAPI returns 422 for validation errors
    data = response.json()
    assert "detail" in data


@pytest.mark.anyio
async def test_register_invalid_email(client: AsyncClient):
    """Test 400 response for invalid email format."""
    response = await client.post(
        "/api/auth/register",
        json={"name": "Test User", "email": "not-an-email", "password": "password123"},
    )

    assert response.status_code == 422  # FastAPI returns 422 for validation errors
    data = response.json()
    assert "detail" in data


# =============================================================================
# User Story 2: User Login Tests
# =============================================================================


@pytest.mark.anyio
async def test_login_success(client: AsyncClient):
    """Test successful login with valid credentials."""
    # First register a user
    await client.post(
        "/api/auth/register",
        json={"name": "Login User", "email": "loginuser@example.com", "password": "password123"},
    )

    # Then login
    response = await client.post(
        "/api/auth/login",
        json={"email": "loginuser@example.com", "password": "password123"},
    )

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["name"] == "Login User"
    assert data["user"]["email"] == "loginuser@example.com"


@pytest.mark.anyio
async def test_login_wrong_password(client: AsyncClient):
    """Test 401 response for wrong password."""
    # First register a user
    await client.post(
        "/api/auth/register",
        json={"name": "Wrong Pass User", "email": "wrongpass@example.com", "password": "correctpassword"},
    )

    # Try login with wrong password
    response = await client.post(
        "/api/auth/login",
        json={"email": "wrongpass@example.com", "password": "wrongpassword"},
    )

    assert response.status_code == 401
    data = response.json()
    assert "invalid credentials" in data["detail"].lower()


@pytest.mark.anyio
async def test_login_nonexistent_email(client: AsyncClient):
    """Test 401 response for non-existent email (same message as wrong password for security)."""
    response = await client.post(
        "/api/auth/login",
        json={"email": "nonexistent@example.com", "password": "password123"},
    )

    assert response.status_code == 401
    data = response.json()
    # Same error message for security (prevents email enumeration)
    assert "invalid credentials" in data["detail"].lower()


# =============================================================================
# User Story 3: JWT Token Verification Tests
# =============================================================================


@pytest.mark.anyio
async def test_verify_valid_token(client: AsyncClient):
    """Test successful JWT verification with valid token."""
    token = create_test_token()

    response = await client.get(
        "/api/auth/verify",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["authenticated"] is True
    assert data["user_id"] == "test-user-123"
    assert data["email"] == "test@example.com"


@pytest.mark.anyio
async def test_verify_expired_token(client: AsyncClient):
    """Test 401 response for expired token."""
    token = create_test_token(expired=True)

    response = await client.get(
        "/api/auth/verify",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 401
    data = response.json()
    assert "expired" in data["detail"].lower()


@pytest.mark.anyio
async def test_verify_invalid_signature(client: AsyncClient):
    """Test 401 response for token signed with wrong secret."""
    token = create_test_token(invalid_secret=True)

    response = await client.get(
        "/api/auth/verify",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 401
    data = response.json()
    assert "invalid" in data["detail"].lower() or "signature" in data["detail"].lower()


@pytest.mark.anyio
async def test_verify_missing_authorization_header(client: AsyncClient):
    """Test 401 response when Authorization header is missing."""
    response = await client.get("/api/auth/verify")

    assert response.status_code == 401
    data = response.json()
    assert "missing" in data["detail"].lower() or "authorization" in data["detail"].lower()


@pytest.mark.anyio
async def test_verify_invalid_bearer_format(client: AsyncClient):
    """Test 401 response when Authorization header has wrong format."""
    response = await client.get(
        "/api/auth/verify",
        headers={"Authorization": "InvalidFormat token123"},
    )

    assert response.status_code == 401
    data = response.json()
    assert "invalid" in data["detail"].lower() or "format" in data["detail"].lower()


@pytest.mark.anyio
async def test_verify_empty_token(client: AsyncClient):
    """Test 401 response when token is empty."""
    response = await client.get(
        "/api/auth/verify",
        headers={"Authorization": "Bearer "},
    )

    assert response.status_code == 401


@pytest.mark.anyio
async def test_verify_malformed_token(client: AsyncClient):
    """Test 401 response for malformed token."""
    response = await client.get(
        "/api/auth/verify",
        headers={"Authorization": "Bearer not.a.valid.jwt.token"},
    )

    assert response.status_code == 401
    data = response.json()
    assert "invalid" in data["detail"].lower()


# =============================================================================
# Integration Tests
# =============================================================================


@pytest.mark.anyio
async def test_register_then_verify_token(client: AsyncClient):
    """Test that a token from registration works for verification."""
    # Register
    register_response = await client.post(
        "/api/auth/register",
        json={"name": "Integration User", "email": "integrationtest@example.com", "password": "password123"},
    )
    assert register_response.status_code == 200
    token = register_response.json()["access_token"]

    # Verify the token
    verify_response = await client.get(
        "/api/auth/verify",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert verify_response.status_code == 200
    data = verify_response.json()
    assert data["authenticated"] is True
    assert data["email"] == "integrationtest@example.com"


@pytest.mark.anyio
async def test_login_then_verify_token(client: AsyncClient):
    """Test that a token from login works for verification."""
    # Register first
    await client.post(
        "/api/auth/register",
        json={"name": "Login Verify User", "email": "loginverify@example.com", "password": "password123"},
    )

    # Login
    login_response = await client.post(
        "/api/auth/login",
        json={"email": "loginverify@example.com", "password": "password123"},
    )
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]

    # Verify the token
    verify_response = await client.get(
        "/api/auth/verify",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert verify_response.status_code == 200
    data = verify_response.json()
    assert data["authenticated"] is True
    assert data["email"] == "loginverify@example.com"


@pytest.mark.anyio
async def test_health_check_no_auth_required(client: AsyncClient):
    """Verify health check endpoint doesn't require authentication."""
    response = await client.get("/health")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
