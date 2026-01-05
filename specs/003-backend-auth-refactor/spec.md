# Feature Specification: Backend Authentication Refactor

**Feature Branch**: `003-backend-auth-refactor`
**Created**: 2025-12-30
**Status**: Draft
**Input**: User description: "Move ALL authentication to FastAPI backend using SQLModel. Frontend becomes pure UI layer with no Prisma/Better Auth."

## Context

The current implementation (002-jwt-auth) uses Better Auth with Prisma on the frontend for authentication. However, the project requirements explicitly specify:
- **ORM**: SQLModel (not Prisma)
- **Backend**: FastAPI handles ALL business logic including authentication
- **Frontend**: Pure UI layer that sends requests to backend APIs

This refactor aligns the authentication system with the project architecture requirements.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - User Registration (Priority: P1) 🎯 MVP

A new user can create an account by submitting their email and password to the backend API, which stores credentials securely using SQLModel.

**Why this priority**: Registration is the entry point for all users - without this, no other auth features work.

**Independent Test**: Navigate to /register, submit valid email/password, verify user is created in database and JWT is returned.

**Acceptance Scenarios**:

1. **Given** a user on the registration page with valid email and password (8+ chars), **When** they submit the form, **Then** the backend creates the user with hashed password, returns a JWT token, and frontend redirects to home.
2. **Given** a user submitting an already registered email, **When** they submit the form, **Then** backend returns 409 Conflict with "Email already registered" message.
3. **Given** a user submitting password with less than 8 characters, **When** they submit the form, **Then** backend returns 400 Bad Request with validation error.

---

### User Story 2 - User Login (Priority: P1)

An existing user can log in by submitting credentials to the backend API, receiving a JWT token for subsequent authenticated requests.

**Why this priority**: Login is the primary authentication flow used on every session.

**Independent Test**: Navigate to /login with registered user credentials, submit form, verify JWT is received and stored, user redirected to home.

**Acceptance Scenarios**:

1. **Given** a registered user on the login page, **When** they submit correct email and password, **Then** backend returns JWT token, frontend stores it and redirects to home.
2. **Given** a user submitting incorrect password, **When** they submit the form, **Then** backend returns 401 Unauthorized with "Invalid credentials" message.
3. **Given** a non-existent email, **When** they submit the form, **Then** backend returns 401 Unauthorized with "Invalid credentials" message (same as wrong password for security).

---

### User Story 3 - JWT Token Verification (Priority: P1)

The backend verifies JWT tokens on protected endpoints and extracts user identity for authorization.

**Why this priority**: All protected API calls depend on valid JWT verification.

**Independent Test**: Call GET /api/auth/verify with valid JWT → 200, invalid JWT → 401, no token → 401.

**Acceptance Scenarios**:

1. **Given** a valid JWT in Authorization header, **When** calling a protected endpoint, **Then** backend extracts user_id and processes request.
2. **Given** an expired JWT, **When** calling a protected endpoint, **Then** backend returns 401 with "Token has expired" message.
3. **Given** no Authorization header, **When** calling a protected endpoint, **Then** backend returns 401 with "Missing Authorization header" message.

---

### User Story 4 - User Logout (Priority: P2)

A logged-in user can log out, which clears their JWT token from the frontend.

**Why this priority**: Logout enables secure session termination but is not critical for MVP.

**Independent Test**: While logged in, click logout button, verify token is cleared and user is redirected to login page.

**Acceptance Scenarios**:

1. **Given** a logged-in user, **When** they click the logout button, **Then** JWT is removed from localStorage and user is redirected to /login.

---

### User Story 5 - Protected Route Access (Priority: P2)

Unauthenticated users are redirected to login when accessing protected routes. Authenticated users are redirected away from auth pages.

**Why this priority**: Route protection enhances UX but basic auth works without it.

**Independent Test**: Access protected page without token → redirect to /login; access /login with valid token → redirect to home.

**Acceptance Scenarios**:

1. **Given** an unauthenticated user, **When** accessing a protected route (e.g., /), **Then** they are redirected to /login.
2. **Given** an authenticated user, **When** accessing /login or /register, **Then** they are redirected to home page.

---

### Edge Cases

- What happens when JWT secret is missing? → Backend startup fails with clear error message.
- How does system handle malformed JWT? → 401 Unauthorized with "Invalid token" message.
- What happens when database connection fails during registration? → 500 Internal Server Error, user sees "Server error, please try again".
- How does system handle concurrent registrations with same email? → Database unique constraint prevents duplicates.

## Requirements *(mandatory)*

### Functional Requirements

#### Backend Authentication API

- **FR-001**: Backend MUST provide POST /api/auth/register endpoint accepting email and password, returning JWT on success.
- **FR-002**: Backend MUST provide POST /api/auth/login endpoint accepting email and password, returning JWT on success.
- **FR-003**: Backend MUST provide GET /api/auth/verify endpoint returning user info if token is valid.
- **FR-004**: Backend MUST hash passwords using bcrypt before storing in database.
- **FR-005**: Backend MUST generate JWT tokens using HS256 algorithm with shared secret (BETTER_AUTH_SECRET).
- **FR-006**: Backend MUST set JWT expiration to 24 hours.
- **FR-007**: Backend MUST return appropriate HTTP status codes (200, 400, 401, 409, 500).

#### Backend Validation

- **FR-008**: Backend MUST validate email format before creating user.
- **FR-009**: Backend MUST enforce minimum password length of 8 characters.
- **FR-010**: Backend MUST check for duplicate email addresses and return 409 if exists.
- **FR-011**: Backend MUST return same error message for wrong password and non-existent user (security).

#### Backend Storage (SQLModel)

- **FR-012**: Backend MUST store users using SQLModel ORM with Neon PostgreSQL.
- **FR-013**: User model MUST include: id (UUID), email (unique), hashed_password, created_at, updated_at.
- **FR-014**: Backend MUST NOT store plain text passwords.

#### Frontend Requirements

- **FR-015**: Frontend MUST call backend /api/auth/register for user registration.
- **FR-016**: Frontend MUST call backend /api/auth/login for user login.
- **FR-017**: Frontend MUST store JWT token in localStorage after successful auth.
- **FR-018**: Frontend MUST attach JWT as Authorization: Bearer header on all API requests.
- **FR-019**: Frontend MUST redirect to /login on 401 responses.
- **FR-020**: Frontend MUST display validation errors from backend responses.
- **FR-021**: Frontend MUST show loading state during API calls.
- **FR-022**: Frontend MUST clear token and redirect to /login on logout.

#### Cleanup Requirements

- **FR-023**: Frontend MUST remove Better Auth dependency (better-auth package).
- **FR-024**: Frontend MUST remove Prisma dependency and schema (prisma package, prisma/ directory).
- **FR-025**: Frontend MUST remove Better Auth API route handler (/api/auth/[...all]).

### Key Entities

- **User**: Represents a registered user. Attributes: id (UUID primary key), email (unique, indexed), hashed_password, created_at, updated_at. Stored in users table.
- **JWT Token**: Stateless authentication token. Payload contains: sub (user_id), email, exp (expiration). Not stored in database.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Zero Prisma dependencies in frontend package.json after refactor.
- **SC-002**: Zero Better Auth dependencies in frontend package.json after refactor.
- **SC-003**: All authentication handled by FastAPI backend using SQLModel.
- **SC-004**: Registration flow completes in under 2 seconds (excluding network latency).
- **SC-005**: Login flow completes in under 1 second (excluding network latency).
- **SC-006**: Backend JWT verification adds less than 10ms latency to protected requests.
- **SC-007**: All auth endpoints return proper HTTP status codes as specified.
- **SC-008**: Frontend forms display validation errors clearly and immediately.

### Technical Verification

- **SC-009**: `npm list prisma` returns empty in frontend directory.
- **SC-010**: `npm list better-auth` returns empty in frontend directory.
- **SC-011**: Backend tests pass for all auth endpoints (register, login, verify).
- **SC-012**: Manual E2E test: register → logout → login → verify → logout succeeds.
