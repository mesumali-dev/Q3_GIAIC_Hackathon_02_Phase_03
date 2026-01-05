"""
Authentication schemas for request/response validation.

These Pydantic models define the structure of auth-related API requests
and responses, with built-in validation.

@see contracts/auth-api.yaml for OpenAPI specification
"""

from pydantic import BaseModel, EmailStr, Field


class RegisterRequest(BaseModel):
    """Request body for user registration."""

    name: str = Field(
        min_length=1,
        max_length=255,
        description="User display name",
        examples=["John Doe"],
    )
    email: EmailStr = Field(
        description="Valid email address",
        examples=["user@example.com"],
    )
    password: str = Field(
        min_length=8,
        description="Password (minimum 8 characters)",
        examples=["securepassword123"],
    )


class LoginRequest(BaseModel):
    """Request body for user login."""

    email: EmailStr = Field(
        description="Registered email address",
        examples=["user@example.com"],
    )
    password: str = Field(
        description="User password",
        examples=["securepassword123"],
    )


class UserResponse(BaseModel):
    """User data returned in responses (no password)."""

    id: str = Field(description="User UUID")
    name: str = Field(description="User display name")
    email: str = Field(description="User email")

    model_config = {"from_attributes": True}


class AuthResponse(BaseModel):
    """Response for successful authentication."""

    access_token: str = Field(
        description="JWT access token",
        examples=["eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."],
    )
    token_type: str = Field(
        default="bearer",
        description="Token type (always 'bearer')",
    )
    user: UserResponse = Field(description="Authenticated user info")


class ErrorResponse(BaseModel):
    """Standard error response."""

    detail: str = Field(
        description="Error message",
        examples=["Invalid credentials"],
    )
