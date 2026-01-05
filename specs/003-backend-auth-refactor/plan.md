# Implementation Plan: Backend Authentication Refactor

**Branch**: `003-backend-auth-refactor` | **Date**: 2025-12-30 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/003-backend-auth-refactor/spec.md`

## Summary

Refactor authentication to move ALL auth logic from frontend (Better Auth + Prisma) to FastAPI backend using SQLModel. Frontend becomes a pure UI layer that calls backend APIs for registration, login, and JWT token management. This aligns with project requirements specifying SQLModel as the only ORM.

**Key Changes**:
1. **Backend**: Add User model (SQLModel), POST /api/auth/register, POST /api/auth/login endpoints
2. **Frontend**: Remove Better Auth and Prisma, simplify forms to call backend APIs
3. **JWT**: Backend issues tokens using PyJWT with BETTER_AUTH_SECRET

## Technical Context

**Language/Version**: Python 3.11+ (backend), TypeScript 5.x (frontend)
**Primary Dependencies**:
- Backend: FastAPI, SQLModel, PyJWT, bcrypt, uvicorn
- Frontend: Next.js 16+ (App Router), Tailwind CSS
**Storage**: Neon PostgreSQL via SQLModel ORM
**Testing**: pytest (backend), Manual E2E testing
**Target Platform**: Linux server (backend), Web browsers (frontend)
**Project Type**: Web application (frontend + backend)
**Performance Goals**: Registration <2s, Login <1s, JWT verification <10ms
**Constraints**: Stateless authentication, 24h token expiry, bcrypt password hashing
**Scale/Scope**: Single-user development phase, multi-user production

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Security by Default | ✅ PASS | JWT auth on all endpoints, bcrypt hashing, no hardcoded secrets |
| II. Separation of Concerns | ✅ PASS | Backend handles auth logic, frontend is pure UI |
| III. RESTful API Design | ✅ PASS | POST /api/auth/register, POST /api/auth/login, GET /api/auth/verify |
| IV. Data Integrity | ✅ PASS | User model with SQLModel, unique email constraint |
| V. Error Handling | ✅ PASS | 400, 401, 409, 500 status codes defined |
| VI. Frontend Standards | ⚠️ UPDATE | Remove Better Auth requirement - backend handles auth |
| VII. Spec-Driven Dev | ✅ PASS | Implementation follows spec.md requirements |

**Note**: Constitution Principle VI mentions "Better Auth MUST be used for authentication flow on the frontend" - this refactor changes that to "Backend MUST handle authentication; frontend MUST only handle UI and API calls". This is an authorized deviation per user requirements.

## Project Structure

### Documentation (this feature)

```text
specs/003-backend-auth-refactor/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
│   ├── auth-api.yaml    # OpenAPI spec for auth endpoints
│   └── responses.yaml   # Common response schemas
└── tasks.md             # Phase 2 output (created by /sp.tasks)
```

### Source Code (repository root)

```text
backend/
├── src/
│   ├── models/
│   │   └── user.py          # NEW: User SQLModel
│   ├── services/
│   │   └── auth_service.py  # NEW: Registration, login logic
│   ├── api/
│   │   └── auth.py          # MODIFY: Add register, login endpoints
│   ├── middleware/
│   │   └── auth.py          # EXISTING: JWT verification
│   └── config.py            # EXISTING: Settings
└── tests/
    └── test_auth.py         # MODIFY: Add register, login tests

frontend/
├── src/
│   ├── components/
│   │   └── auth/
│   │       ├── RegisterForm.tsx  # MODIFY: Call backend API
│   │       └── LoginForm.tsx     # MODIFY: Call backend API
│   ├── app/
│   │   ├── page.tsx              # EXISTING: Home with auth status
│   │   ├── register/page.tsx     # EXISTING: Registration page
│   │   ├── login/page.tsx        # EXISTING: Login page
│   │   └── api/auth/[...all]/    # DELETE: Better Auth route
│   └── lib/
│       ├── auth.ts               # DELETE: Better Auth server
│       ├── auth-client.ts        # DELETE: Better Auth client
│       └── api.ts                # MODIFY: Add auth API calls
├── prisma/                       # DELETE: Entire directory
├── middleware.ts                 # MODIFY: Use localStorage JWT check
└── package.json                  # MODIFY: Remove better-auth, prisma
```

**Structure Decision**: Web application structure with backend handling all business logic (including authentication) and frontend as pure UI layer. This aligns with the project constitution's separation of concerns principle.

## Architecture Sketch

```
┌─────────────────────────────────────────────────────────────────────┐
│                           FRONTEND (Next.js)                        │
│  ┌───────────────────┐    ┌───────────────────┐                    │
│  │   RegisterForm    │    │    LoginForm      │                    │
│  │  - email input    │    │  - email input    │                    │
│  │  - password input │    │  - password input │                    │
│  │  - submit → API   │    │  - submit → API   │                    │
│  └─────────┬─────────┘    └─────────┬─────────┘                    │
│            │                        │                               │
│            └──────────┬─────────────┘                               │
│                       ▼                                             │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │                    lib/api.ts                                 │  │
│  │  - POST /api/auth/register                                    │  │
│  │  - POST /api/auth/login                                       │  │
│  │  - Stores JWT in localStorage                                 │  │
│  │  - Attaches Authorization: Bearer header                      │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                       │                                             │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │                    middleware.ts                              │  │
│  │  - Checks localStorage for token                              │  │
│  │  - Redirects unauthenticated to /login                        │  │
│  │  - Redirects authenticated away from /login, /register        │  │
│  └──────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
                                │
                                │ HTTP (JSON)
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                          BACKEND (FastAPI)                          │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │                    api/auth.py                                │  │
│  │  POST /api/auth/register                                      │  │
│  │    → validate email/password                                  │  │
│  │    → hash password (bcrypt)                                   │  │
│  │    → create user (SQLModel)                                   │  │
│  │    → generate JWT (PyJWT)                                     │  │
│  │    → return { access_token, user }                            │  │
│  │                                                               │  │
│  │  POST /api/auth/login                                         │  │
│  │    → find user by email                                       │  │
│  │    → verify password (bcrypt)                                 │  │
│  │    → generate JWT (PyJWT)                                     │  │
│  │    → return { access_token, user }                            │  │
│  │                                                               │  │
│  │  GET /api/auth/verify                                         │  │
│  │    → verify JWT (existing)                                    │  │
│  │    → return { user_id, email }                                │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                       │                                             │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │                services/auth_service.py                       │  │
│  │  - create_user(email, password) → User                        │  │
│  │  - authenticate_user(email, password) → User | None           │  │
│  │  - create_access_token(user) → str (JWT)                      │  │
│  │  - hash_password(password) → str                              │  │
│  │  - verify_password(plain, hashed) → bool                      │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                       │                                             │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │                  models/user.py                               │  │
│  │  class User(SQLModel, table=True):                            │  │
│  │      id: UUID (primary key)                                   │  │
│  │      email: str (unique, indexed)                             │  │
│  │      hashed_password: str                                     │  │
│  │      created_at: datetime                                     │  │
│  │      updated_at: datetime                                     │  │
│  └──────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
                                │
                                │ SQL
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      Neon PostgreSQL                                │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │  users table                                                  │  │
│  │  - id UUID PRIMARY KEY                                        │  │
│  │  - email VARCHAR UNIQUE NOT NULL                              │  │
│  │  - hashed_password VARCHAR NOT NULL                           │  │
│  │  - created_at TIMESTAMP DEFAULT NOW()                         │  │
│  │  - updated_at TIMESTAMP DEFAULT NOW()                         │  │
│  └──────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
```

## Key Decisions

| Decision | Choice | Alternatives Considered | Rationale |
|----------|--------|------------------------|-----------|
| Auth location | Backend (FastAPI) | Frontend (Better Auth) | Project requires SQLModel; backend handles all business logic |
| Password hashing | bcrypt | argon2, scrypt | Industry standard, well-tested, PyJWT compatible |
| JWT library | PyJWT | python-jose, authlib | Already installed, simple API, HS256 support |
| Token storage | localStorage | httpOnly cookie, sessionStorage | Simple implementation, explicit header attachment |
| User ID format | UUID | Auto-increment int | Better for distributed systems, harder to enumerate |

## Testing Strategy

### Backend Tests (pytest)

| Test Case | Endpoint | Expected |
|-----------|----------|----------|
| Register with valid data | POST /api/auth/register | 200, returns JWT and user |
| Register with existing email | POST /api/auth/register | 409, "Email already registered" |
| Register with short password | POST /api/auth/register | 400, validation error |
| Register with invalid email | POST /api/auth/register | 400, validation error |
| Login with valid credentials | POST /api/auth/login | 200, returns JWT and user |
| Login with wrong password | POST /api/auth/login | 401, "Invalid credentials" |
| Login with non-existent email | POST /api/auth/login | 401, "Invalid credentials" |
| Verify with valid token | GET /api/auth/verify | 200, returns user info |
| Verify with expired token | GET /api/auth/verify | 401, "Token has expired" |
| Verify with invalid token | GET /api/auth/verify | 401, "Invalid token" |
| Verify without token | GET /api/auth/verify | 401, "Missing Authorization header" |

### Manual E2E Tests

1. **Registration Flow**: Navigate to /register → Submit valid email/password → Verify redirect to home → Verify JWT in localStorage
2. **Login Flow**: Navigate to /login → Submit registered credentials → Verify redirect to home → Verify JWT in localStorage
3. **Logout Flow**: Click logout → Verify JWT cleared → Verify redirect to /login
4. **Route Protection**: Clear localStorage → Access protected route → Verify redirect to /login
5. **Auth Redirect**: Login → Access /login → Verify redirect to home

## Complexity Tracking

> No constitution violations requiring justification. All changes align with principles.

| Aspect | Complexity Level | Notes |
|--------|-----------------|-------|
| Backend changes | Low-Medium | Add User model, 2 endpoints, 1 service file |
| Frontend changes | Low | Remove dependencies, simplify API calls |
| Migration risk | Low | No existing user data to migrate |
| Testing effort | Medium | 11 backend tests, 5 E2E flows |

## Phase Summary

| Phase | Artifact | Status |
|-------|----------|--------|
| Phase 0 | research.md | Pending |
| Phase 1 | data-model.md | Pending |
| Phase 1 | contracts/auth-api.yaml | Pending |
| Phase 1 | quickstart.md | Pending |
| Phase 2 | tasks.md | Created by /sp.tasks |
