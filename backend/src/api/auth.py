"""
Authentication API routes for the backend application.

This module provides authentication-related endpoints:
- POST /api/auth/register: Register a new user
- POST /api/auth/login: Login and get JWT token
- GET /api/auth/verify: Verify JWT token and return user info

@see specs/003-backend-auth-refactor/contracts/auth-api.yaml
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session

from src.database import get_db
from src.middleware.auth import CurrentUser
from src.schemas.auth import (
    AuthResponse,
    LoginRequest,
    RegisterRequest,
    UserResponse,
)
from src.services.auth_service import (
    authenticate_user,
    create_access_token,
    create_user,
    get_user_by_email,
)

# Create router for auth endpoints
router = APIRouter(prefix="/api/auth", tags=["Authentication"])


@router.post("/register", response_model=AuthResponse)
async def register(
    request: RegisterRequest,
    db: Session = Depends(get_db),
) -> AuthResponse:
    """
    Register a new user account.

    Creates a new user with the provided email and password,
    hashes the password, and returns a JWT access token.

    Args:
        request: Registration request with email and password
        db: Database session (injected)

    Returns:
        AuthResponse with access_token and user info

    Raises:
        HTTPException: 409 if email already registered
    """
    # Check if email already exists
    existing_user = get_user_by_email(db, request.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        )

    try:
        # Create new user
        user = create_user(db, request.name, request.email, request.password)

        # Generate JWT token
        access_token = create_access_token(user)

        return AuthResponse(
            access_token=access_token,
            token_type="bearer",
            user=UserResponse(id=str(user.id), name=user.name, email=user.email),
        )

    except IntegrityError:
        # Handle race condition where email was registered between check and insert
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        )


@router.post("/login", response_model=AuthResponse)
async def login(
    request: LoginRequest,
    db: Session = Depends(get_db),
) -> AuthResponse:
    """
    Login with email and password.

    Authenticates the user and returns a JWT access token.

    Args:
        request: Login request with email and password
        db: Database session (injected)

    Returns:
        AuthResponse with access_token and user info

    Raises:
        HTTPException: 401 if credentials are invalid
    """
    # Authenticate user (returns None if invalid)
    user = authenticate_user(db, request.email, request.password)

    if not user:
        # Use same error message for both wrong password and non-existent email
        # This prevents email enumeration attacks
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    # Generate JWT token
    access_token = create_access_token(user)

    return AuthResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse(id=str(user.id), name=user.name, email=user.email),
    )


@router.get("/verify")
async def verify_token(current_user: CurrentUser) -> dict:
    """
    Verify JWT token and return user information.

    This endpoint verifies the JWT token in the Authorization header
    and returns the authenticated user's information.

    Args:
        current_user: Authenticated user from JWT (injected by dependency)

    Returns:
        dict: User information including:
            - authenticated: Always true if endpoint is reached
            - user_id: User's unique identifier
            - email: User's email address
    """
    return {
        "authenticated": True,
        "user_id": current_user["user_id"],
        "email": current_user.get("email"),
    }
