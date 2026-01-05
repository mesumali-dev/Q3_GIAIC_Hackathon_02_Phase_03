"""
Authentication service for user management.

Provides functions for password hashing, JWT token generation,
user creation, and authentication.

@see research.md for algorithm decisions
@see data-model.md for User model specification
"""

from datetime import datetime, timedelta, timezone

import bcrypt
import jwt
from sqlmodel import Session, select

from src.config import get_settings
from src.models.user import User


def hash_password(password: str) -> str:
    """
    Hash a plain text password using bcrypt.

    Args:
        password: Plain text password to hash

    Returns:
        bcrypt hash of the password
    """
    # bcrypt requires bytes, encode the password
    password_bytes = password.encode("utf-8")
    # Generate salt and hash
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against its bcrypt hash.

    Args:
        plain_password: Plain text password to verify
        hashed_password: bcrypt hash to verify against

    Returns:
        True if password matches hash, False otherwise
    """
    password_bytes = plain_password.encode("utf-8")
    hashed_bytes = hashed_password.encode("utf-8")
    return bcrypt.checkpw(password_bytes, hashed_bytes)


def create_access_token(user: User) -> str:
    """
    Create a JWT access token for a user.

    Token payload includes:
    - sub: User ID (UUID as string)
    - email: User's email address
    - exp: Expiration timestamp
    - iat: Issued at timestamp

    Args:
        user: User model instance

    Returns:
        Encoded JWT token string
    """
    settings = get_settings()

    now = datetime.now(timezone.utc)
    expire = now + timedelta(hours=settings.JWT_EXPIRY_HOURS)

    payload = {
        "sub": str(user.id),
        "email": user.email,
        "exp": expire,
        "iat": now,
    }

    return jwt.encode(
        payload,
        settings.BETTER_AUTH_SECRET,
        algorithm=settings.JWT_ALGORITHM,
    )


def create_user(db: Session, name: str, email: str, password: str) -> User:
    """
    Create a new user in the database.

    Args:
        db: Database session
        name: User's display name
        email: User's email address
        password: Plain text password (will be hashed)

    Returns:
        Created User model instance

    Note:
        Caller should handle IntegrityError for duplicate emails
    """
    hashed = hash_password(password)
    user = User(name=name, email=email, hashed_password=hashed)

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


def authenticate_user(db: Session, email: str, password: str) -> User | None:
    """
    Authenticate a user with email and password.

    Args:
        db: Database session
        email: User's email address
        password: Plain text password to verify

    Returns:
        User instance if authentication succeeds, None otherwise
    """
    statement = select(User).where(User.email == email)
    user = db.exec(statement).first()

    if not user:
        return None

    if not verify_password(password, user.hashed_password):
        return None

    return user


def get_user_by_email(db: Session, email: str) -> User | None:
    """
    Get a user by email address.

    Args:
        db: Database session
        email: Email address to search for

    Returns:
        User instance if found, None otherwise
    """
    statement = select(User).where(User.email == email)
    return db.exec(statement).first()
