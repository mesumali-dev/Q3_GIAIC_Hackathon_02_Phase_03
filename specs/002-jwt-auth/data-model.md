# Data Model: JWT Authentication & Frontend UI

**Feature Branch**: `002-jwt-auth`
**Date**: 2025-12-30
**Status**: Draft

## Overview

This document defines the data entities required for JWT authentication. The User entity is the primary data model, with JWT tokens being transient authentication credentials.

---

## Entity: User

The User entity represents an authenticated user in the system.

### Fields

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | UUID | Primary Key, Auto-generated | Unique identifier for the user |
| `email` | String | Unique, Not Null, Valid Email | User's email address for login |
| `password_hash` | String | Not Null | Bcrypt-hashed password (never stored in plain text) |
| `name` | String | Nullable | User's display name (optional) |
| `email_verified` | Boolean | Default: false | Whether email has been verified |
| `created_at` | Timestamp | Auto-generated | When the user account was created |
| `updated_at` | Timestamp | Auto-updated | When the user account was last modified |

### Validation Rules

- **email**: Must be valid email format, case-insensitive uniqueness
- **password**: Minimum 8 characters (validated at input, stored as hash)
- **name**: Maximum 255 characters

### Relationships

- One User has Many Tasks (foreign key in Task entity, defined in Part 3)

---

## Entity: Session (Better Auth Managed)

Better Auth manages sessions internally. This entity is created by the library.

### Fields (Better Auth Schema)

| Field | Type | Description |
|-------|------|-------------|
| `id` | String | Session identifier |
| `userId` | String | Foreign key to User |
| `expiresAt` | Timestamp | Session expiration time |
| `token` | String | Session token (hashed) |
| `ipAddress` | String | Client IP address |
| `userAgent` | String | Client user agent |
| `createdAt` | Timestamp | Session creation time |
| `updatedAt` | Timestamp | Session update time |

### Notes

- Sessions are managed by Better Auth automatically
- JWT tokens are derived from sessions
- Multiple sessions allowed per user (multi-device support)

---

## Entity: Account (Better Auth Managed)

Better Auth uses this for OAuth providers. For email/password, this links credentials.

### Fields (Better Auth Schema)

| Field | Type | Description |
|-------|------|-------------|
| `id` | String | Account identifier |
| `userId` | String | Foreign key to User |
| `providerId` | String | Auth provider (e.g., "credential") |
| `accountId` | String | Provider-specific account ID |
| `password` | String | Hashed password (for credential provider) |
| `createdAt` | Timestamp | Account creation time |
| `updatedAt` | Timestamp | Account update time |

---

## Transient: JWT Token

JWT tokens are not persisted but are critical to the authentication flow.

### Payload Structure

```json
{
  "sub": "user-uuid-here",
  "email": "user@example.com",
  "iat": 1704067200,
  "exp": 1704153600
}
```

### Claims

| Claim | Type | Description | Source |
|-------|------|-------------|--------|
| `sub` | String (UUID) | Subject - User ID | `user.id` |
| `email` | String | User's email | `user.email` |
| `iat` | Number (Unix) | Issued At timestamp | Auto-generated |
| `exp` | Number (Unix) | Expiration timestamp | `iat + 24 hours` |

### Validation Rules (Backend)

1. Signature MUST be verified with `BETTER_AUTH_SECRET`
2. `exp` MUST be in the future
3. `sub` MUST be a valid UUID format
4. `sub` MUST match route `user_id` parameter (ownership check)

---

## Frontend State: AuthState

Client-side state representation (not persisted to database).

### Fields

| Field | Type | Description |
|-------|------|-------------|
| `isAuthenticated` | Boolean | Whether user is logged in |
| `user` | Object | User info (id, email, name) |
| `token` | String | JWT token (stored in localStorage) |
| `isLoading` | Boolean | Auth operation in progress |
| `error` | String | Error message if any |

### State Transitions

```
Initial → Loading → Authenticated | Error
Authenticated → Loading → Unauthenticated (on logout)
```

---

## Database Schema (SQLModel)

### User Table (Python)

```python
from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime
import uuid

class User(SQLModel, table=True):
    __tablename__ = "user"

    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        primary_key=True,
    )
    email: str = Field(unique=True, index=True)
    name: Optional[str] = Field(default=None, max_length=255)
    email_verified: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
```

### Notes

- Password is stored in the Account table (Better Auth pattern)
- Better Auth handles password hashing with bcrypt
- The User model does NOT store plain text passwords

---

## Better Auth Database Adapter

Better Auth requires specific tables. The adapter creates:

| Table | Purpose |
|-------|---------|
| `user` | User accounts |
| `session` | Active sessions |
| `account` | Authentication providers |
| `verification` | Email verification tokens |

### Prisma Schema (for Better Auth)

```prisma
model User {
  id            String    @id @default(uuid())
  email         String    @unique
  name          String?
  emailVerified Boolean   @default(false)
  createdAt     DateTime  @default(now())
  updatedAt     DateTime  @updatedAt
  sessions      Session[]
  accounts      Account[]
}

model Session {
  id        String   @id @default(uuid())
  userId    String
  token     String   @unique
  expiresAt DateTime
  ipAddress String?
  userAgent String?
  createdAt DateTime @default(now())
  updatedAt DateTime @updatedAt
  user      User     @relation(fields: [userId], references: [id], onDelete: Cascade)
}

model Account {
  id         String   @id @default(uuid())
  userId     String
  providerId String
  accountId  String
  password   String?
  createdAt  DateTime @default(now())
  updatedAt  DateTime @updatedAt
  user       User     @relation(fields: [userId], references: [id], onDelete: Cascade)
}
```

---

## Entity Relationship Diagram

```
┌─────────────────┐       ┌─────────────────┐
│      User       │       │     Session     │
├─────────────────┤       ├─────────────────┤
│ id (PK)         │───┐   │ id (PK)         │
│ email           │   │   │ userId (FK)     │───┐
│ name            │   │   │ token           │   │
│ emailVerified   │   │   │ expiresAt       │   │
│ createdAt       │   └──►│ createdAt       │   │
│ updatedAt       │       │ updatedAt       │   │
└─────────────────┘       └─────────────────┘   │
        │                                        │
        │         ┌─────────────────┐           │
        │         │     Account     │           │
        │         ├─────────────────┤           │
        └────────►│ id (PK)         │◄──────────┘
                  │ userId (FK)     │
                  │ providerId      │
                  │ accountId       │
                  │ password (hash) │
                  │ createdAt       │
                  │ updatedAt       │
                  └─────────────────┘
```

---

## Migration Notes

1. **Phase 1 (Foundation)**: Database placeholder only, no schema
2. **Phase 2 (This Feature)**: Create User, Session, Account tables via Better Auth
3. **Phase 3 (Tasks)**: Add Task table with `user_id` foreign key

### Migration Strategy

- Use Better Auth's built-in Prisma/Drizzle adapter
- Run adapter's migration command to create auth tables
- Backend SQLModel only needs to read from these tables for verification
