"""
JWT Authentication middleware for the backend application.

This module provides JWT verification for all authenticated endpoints.
Uses PyJWT with HS256 algorithm and BETTER_AUTH_SECRET for verification.

Security Notes:
- JWT signatures are verified using BETTER_AUTH_SECRET
- JWT expiry is enforced
- User ID from JWT is extracted for ownership verification

@see US4: Backend JWT Verification
"""

from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, Header, status

from src.config import get_settings


def verify_jwt(
    authorization: Annotated[str | None, Header()] = None
) -> dict:
    """
    Verify JWT token from Authorization header.

    Extracts and validates the JWT token, returning the decoded payload.

    Args:
        authorization: The Authorization header value (e.g., "Bearer <token>")

    Returns:
        Decoded JWT payload containing user information

    Raises:
        HTTPException: 401 if token is missing, expired, or invalid
    """
    settings = get_settings()

    # Check for missing Authorization header
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing Authorization header",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Check for correct Bearer format
    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Authorization header format. Use 'Bearer <token>'",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Extract token from header
    token = authorization[7:]  # Remove "Bearer " prefix

    # Check for empty token
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing token in Authorization header",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        # Verify and decode the JWT token
        payload = jwt.decode(
            token,
            settings.BETTER_AUTH_SECRET,
            algorithms=[settings.JWT_ALGORITHM],
        )
        return payload

    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )

    except jwt.InvalidSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token signature",
            headers={"WWW-Authenticate": "Bearer"},
        )

    except jwt.InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )


def get_current_user(payload: Annotated[dict, Depends(verify_jwt)]) -> dict:
    """
    Get current user information from verified JWT payload.

    This is a FastAPI dependency that extracts user info from the JWT.

    Args:
        payload: Decoded JWT payload from verify_jwt dependency

    Returns:
        User information dict with user_id and email

    Raises:
        HTTPException: 401 if user_id (sub claim) is missing
    """
    user_id = payload.get("sub")
    email = payload.get("email")

    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token: missing user identifier",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return {
        "user_id": user_id,
        "email": email,
    }


def verify_user_ownership(jwt_user_id: str, route_user_id: str) -> bool:
    """
    Verify that the authenticated user owns the requested resource.

    Args:
        jwt_user_id: User ID extracted from JWT token (sub claim)
        route_user_id: User ID from the route parameter

    Returns:
        True if user IDs match

    Raises:
        HTTPException: 403 if user IDs don't match
    """
    if jwt_user_id != route_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: Cannot access another user's resources",
        )
    return True


# Type alias for dependency injection
CurrentUser = Annotated[dict, Depends(get_current_user)]
