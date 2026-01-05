# Data Model: Backend Authentication Refactor

**Feature**: 003-backend-auth-refactor
**Date**: 2025-12-30
**ORM**: SQLModel (Python)

## Entity Relationship Diagram

```
┌─────────────────────────────────────────┐
│                  User                    │
├─────────────────────────────────────────┤
│ id: UUID (PK)                           │
│ email: str (UNIQUE, indexed)            │
│ hashed_password: str                    │
│ created_at: datetime                    │
│ updated_at: datetime                    │
└─────────────────────────────────────────┘
         │
         │ 1:N (future)
         ▼
┌─────────────────────────────────────────┐
│                  Task                    │
│            (future feature)              │
├─────────────────────────────────────────┤
│ id: UUID (PK)                           │
│ user_id: UUID (FK → User.id)            │
│ title: str                              │
│ completed: bool                         │
│ created_at: datetime                    │
│ updated_at: datetime                    │
└─────────────────────────────────────────┘
```

## User Entity

### Purpose
Represents a registered user in the system. Stores authentication credentials and audit information.

### SQLModel Definition

```python
from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4
from sqlmodel import Field, SQLModel

class User(SQLModel, table=True):
    """
    User model for authentication.

    Attributes:
        id: Unique identifier (UUID v4)
        email: User's email address (unique, used for login)
        hashed_password: bcrypt-hashed password (never store plain text)
        created_at: Timestamp when user was created
        updated_at: Timestamp of last update
    """
    __tablename__ = "users"

    id: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
        description="Unique user identifier"
    )
    email: str = Field(
        index=True,
        unique=True,
        max_length=255,
        description="User email address for login"
    )
    hashed_password: str = Field(
        max_length=255,
        description="bcrypt hashed password"
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Account creation timestamp"
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column_kwargs={"onupdate": datetime.utcnow},
        description="Last update timestamp"
    )
```

### Field Specifications

| Field | Type | Constraints | Validation |
|-------|------|-------------|------------|
| id | UUID | PRIMARY KEY, NOT NULL | Auto-generated UUID v4 |
| email | VARCHAR(255) | UNIQUE, NOT NULL, INDEX | Valid email format |
| hashed_password | VARCHAR(255) | NOT NULL | bcrypt hash (60 chars) |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Auto-set on insert |
| updated_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Auto-update on change |

### Database Schema (PostgreSQL)

```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Index for email lookups during login
CREATE INDEX idx_users_email ON users(email);
```

## Request/Response Schemas

### Registration Request

```python
from pydantic import BaseModel, EmailStr, Field

class RegisterRequest(BaseModel):
    """Request body for user registration"""
    email: EmailStr = Field(
        description="Valid email address",
        example="user@example.com"
    )
    password: str = Field(
        min_length=8,
        description="Password (minimum 8 characters)",
        example="securepassword123"
    )
```

### Login Request

```python
class LoginRequest(BaseModel):
    """Request body for user login"""
    email: EmailStr = Field(
        description="Registered email address",
        example="user@example.com"
    )
    password: str = Field(
        description="User password",
        example="securepassword123"
    )
```

### Auth Response

```python
class UserResponse(BaseModel):
    """User data returned in responses (no password)"""
    id: str = Field(description="User UUID")
    email: str = Field(description="User email")

    class Config:
        from_attributes = True

class AuthResponse(BaseModel):
    """Response for successful authentication"""
    access_token: str = Field(
        description="JWT access token",
        example="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
    )
    token_type: str = Field(
        default="bearer",
        description="Token type (always 'bearer')"
    )
    user: UserResponse = Field(
        description="Authenticated user info"
    )
```

### Error Response

```python
class ErrorResponse(BaseModel):
    """Standard error response"""
    detail: str = Field(
        description="Error message",
        example="Invalid credentials"
    )
```

## JWT Token Structure

### Payload

```json
{
    "sub": "550e8400-e29b-41d4-a716-446655440000",
    "email": "user@example.com",
    "exp": 1735689600,
    "iat": 1735603200
}
```

| Claim | Type | Description |
|-------|------|-------------|
| sub | string (UUID) | User ID (subject) |
| email | string | User email address |
| exp | integer | Expiration timestamp (Unix) |
| iat | integer | Issued at timestamp (Unix) |

### Token Configuration

```python
JWT_ALGORITHM = "HS256"
JWT_EXPIRY_HOURS = 24
```

## Validation Rules

### Email Validation
- Must be valid email format (RFC 5322)
- Maximum 255 characters
- Unique in database (case-insensitive comparison recommended)

### Password Validation
- Minimum 8 characters
- No maximum length (bcrypt handles this)
- Stored as bcrypt hash (60 characters)

### Password Hashing

```python
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    """Hash a plain text password"""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)
```

## State Transitions

### User Lifecycle

```
[Not Registered] → register() → [Active]
                                    │
                                    ├─→ login() → [Authenticated] (has JWT)
                                    │
                                    └─→ logout() → [Active] (no JWT)
```

### JWT Lifecycle

```
[None] → login/register → [Valid Token]
                              │
                              ├─→ API request → [Token Verified]
                              │
                              ├─→ 24h passes → [Expired Token] → 401 Unauthorized
                              │
                              └─→ logout → [None]
```

## Database Migrations

### Initial Migration (003-backend-auth-refactor)

```python
# Using SQLModel create_db_and_tables or Alembic

from sqlmodel import SQLModel, create_engine

engine = create_engine(DATABASE_URL)

def create_tables():
    SQLModel.metadata.create_all(engine)
```

### Migration Script (Alembic alternative)

```sql
-- Up migration
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);

-- Down migration
DROP INDEX IF EXISTS idx_users_email;
DROP TABLE IF EXISTS users;
```

## Security Considerations

1. **Password Storage**: NEVER store plain text passwords
2. **Email Uniqueness**: Database constraint prevents duplicate registrations
3. **UUID vs Auto-increment**: UUIDs prevent user enumeration
4. **Token Expiry**: 24-hour expiry limits exposure window
5. **No Password in Response**: UserResponse excludes hashed_password
