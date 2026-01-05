"""
User model for authentication.

This module defines the User SQLModel for storing user credentials.
Uses UUID for primary key and bcrypt-hashed passwords.

@see data-model.md for entity specifications
"""

from datetime import datetime, timezone
from uuid import UUID, uuid4

from sqlmodel import Field, SQLModel


class User(SQLModel, table=True):
    """
    User model for authentication.

    Attributes:
        id: Unique identifier (UUID v4)
        name: User's display name
        email: User's email address (unique, used for login)
        hashed_password: bcrypt-hashed password (never store plain text)
        created_at: Timestamp when user was created
        updated_at: Timestamp of last update
    """

    __tablename__ = "users"

    id: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
        description="Unique user identifier",
    )
    name: str = Field(
        max_length=255,
        description="User display name",
    )
    email: str = Field(
        index=True,
        unique=True,
        max_length=255,
        description="User email address for login",
    )
    hashed_password: str = Field(
        max_length=255,
        description="bcrypt hashed password",
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Account creation timestamp",
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Last update timestamp",
    )
