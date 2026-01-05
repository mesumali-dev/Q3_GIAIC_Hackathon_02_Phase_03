# Implementation Plan: JWT Authentication & Frontend UI

**Branch**: `002-jwt-auth` | **Date**: 2025-12-30 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/002-jwt-auth/spec.md`

## Summary

Implement secure, JWT-based user authentication using Better Auth on the Next.js frontend and PyJWT verification on the FastAPI backend. This feature enables user registration, login, and protected API access with JWT tokens transmitted via `Authorization: Bearer <token>` header. Uses HS256 symmetric algorithm with shared `BETTER_AUTH_SECRET` for signing and verification.

## Technical Context

**Language/Version**: Python 3.14+ (backend), TypeScript 5.x (frontend)
**Primary Dependencies**: FastAPI, PyJWT, SQLModel (backend); Next.js 16+, Better Auth, Tailwind CSS (frontend)
**Storage**: Neon PostgreSQL (user data via Better Auth, session data)
**Testing**: pytest (backend), manual UI testing (frontend)
**Target Platform**: Web application (Linux server, modern browsers)
**Project Type**: Web application (frontend + backend monorepo)
**Performance Goals**: <500ms auth operations, support 100 concurrent users
**Constraints**: Stateless backend, JWT-only authentication, no OAuth providers
**Scale/Scope**: Single-tenant, ~1000 users, 2 auth pages

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Requirement | Status | Notes |
|-----------|-------------|--------|-------|
| I. Security by Default | JWT auth on all protected endpoints | ✅ PASS | HS256 with shared secret |
| I. Security by Default | JWT verification with BETTER_AUTH_SECRET | ✅ PASS | Configured in both environments |
| I. Security by Default | No hardcoded secrets | ✅ PASS | All secrets from environment variables |
| II. Separation of Concerns | Frontend: UI only, Backend: business logic | ✅ PASS | Auth logic in Better Auth (frontend), verification in FastAPI |
| III. RESTful API Design | Authorization header on requests | ✅ PASS | Bearer token pattern |
| V. Error Handling | 401 for invalid/missing JWT | ✅ PASS | Defined in contracts |
| VI. Frontend Standards | Responsive UI with Tailwind | ✅ PASS | Mobile-first auth forms |
| VI. Frontend Standards | Better Auth for auth flow | ✅ PASS | JWT plugin configured |
| VII. Spec-Driven Development | Implementation follows spec | ✅ PASS | All FR mapped to tasks |

**Gate Status**: ✅ PASSED - All constitution requirements met

## Project Structure

### Documentation (this feature)

```text
specs/002-jwt-auth/
├── plan.md              # This file
├── research.md          # Phase 0 research findings
├── data-model.md        # User, Session, JWT entities
├── quickstart.md        # Setup and testing guide
├── contracts/
│   └── auth-api.yaml    # OpenAPI specification
└── tasks.md             # Phase 2 output (/sp.tasks command)
```

### Source Code (repository root)

```text
backend/
├── src/
│   ├── __init__.py
│   ├── main.py              # FastAPI app with CORS
│   ├── config.py            # Settings with BETTER_AUTH_SECRET
│   ├── database.py          # Database connection (existing placeholder)
│   ├── middleware/
│   │   ├── __init__.py
│   │   └── auth.py          # JWT verification middleware
│   ├── models/              # SQLModel entities (future)
│   ├── services/            # Business logic (future)
│   └── api/
│       └── auth.py          # Auth verification endpoint
└── tests/
    ├── test_health.py       # Existing health test
    └── test_auth.py         # JWT verification tests

frontend/
├── src/
│   ├── app/
│   │   ├── layout.tsx       # Root layout (existing)
│   │   ├── page.tsx         # Home page (existing)
│   │   ├── globals.css      # Global styles (existing)
│   │   ├── login/
│   │   │   └── page.tsx     # Login page
│   │   ├── register/
│   │   │   └── page.tsx     # Registration page
│   │   └── api/
│   │       └── auth/
│   │           └── [...all]/
│   │               └── route.ts  # Better Auth API handler
│   ├── components/
│   │   └── auth/
│   │       ├── LoginForm.tsx
│   │       └── RegisterForm.tsx
│   └── lib/
│       ├── auth.ts          # Better Auth server config
│       ├── auth-client.ts   # Better Auth client config
│       └── api.ts           # API client with JWT injection
├── middleware.ts            # Route protection
└── prisma/
    └── schema.prisma        # Database schema for Better Auth
```

**Structure Decision**: Web application pattern with separate frontend and backend directories, as per constitution Section II (Separation of Concerns).

## Implementation Phases

### Phase 1: Backend JWT Middleware (P1)

**Goal**: Enable FastAPI to verify JWT tokens from Better Auth

**Tasks**:
1. Implement JWT verification in `src/middleware/auth.py`
2. Add `get_current_user` dependency for route handlers
3. Create `/api/auth/verify` test endpoint
4. Add CORS configuration for frontend origin
5. Write pytest tests for JWT verification

**Constitution Checks**:
- ✅ Uses BETTER_AUTH_SECRET from environment
- ✅ Returns 401 for invalid/expired tokens
- ✅ Extracts user_id from JWT claims

### Phase 2: Frontend Better Auth Setup (P1)

**Goal**: Configure Better Auth with JWT plugin and database

**Tasks**:
1. Install Better Auth: `npm install better-auth`
2. Set up Prisma schema for Better Auth tables
3. Configure Better Auth server in `src/lib/auth.ts`
4. Configure Better Auth client in `src/lib/auth-client.ts`
5. Create API route handler at `/api/auth/[...all]/route.ts`
6. Run database migrations

**Constitution Checks**:
- ✅ Uses BETTER_AUTH_SECRET for JWT signing
- ✅ JWT contains sub (user_id) and email claims

### Phase 3: Authentication Pages (P1)

**Goal**: Create login and registration UI

**Tasks**:
1. Create `/register` page with form
2. Create `/login` page with form
3. Implement form validation (email format, password length)
4. Handle error states and display messages
5. Implement success redirect to home

**Constitution Checks**:
- ✅ Responsive design with Tailwind CSS
- ✅ User-friendly error messages

### Phase 4: Route Protection (P2)

**Goal**: Protect routes and inject JWT into API calls

**Tasks**:
1. Create Next.js middleware for route protection
2. Update API client to attach Bearer token
3. Redirect unauthenticated users to login
4. Redirect authenticated users away from auth pages
5. Handle token expiry with redirect

**Constitution Checks**:
- ✅ JWT attached to all API requests
- ✅ Protected routes require authentication

### Phase 5: Integration Testing (P2)

**Goal**: Verify end-to-end authentication flow

**Tasks**:
1. Test registration flow
2. Test login flow
3. Test backend JWT verification
4. Test route protection
5. Test error handling

---

## Key Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| JWT Algorithm | HS256 | Shared secret simplicity, no JWKS calls |
| Token Storage | localStorage | Required for cross-origin API calls |
| Auth Library | Better Auth | Constitution mandate, JWT plugin support |
| Backend Verification | PyJWT | Already installed, direct HS256 support |
| UI Framework | Tailwind CSS | Constitution mandate, no extra dependencies |

---

## Risks and Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Better Auth version incompatibility | High | Pin version in package.json |
| XSS vulnerability with localStorage | Medium | CSP headers (out of scope for Part 2) |
| Token expiry mid-session | Low | Redirect to login on 401, clear message |
| Database migration issues | Medium | Test migrations on dev first |

---

## Dependencies

### Must Be Completed Before

- ✅ Foundation phase (001-foundation-init) - Completed

### Blocks

- Part 3: Task CRUD (requires authenticated user context)

---

## Acceptance Criteria

From spec.md:

- [ ] User can register with email/password
- [ ] User can login with email/password
- [ ] JWT token is issued and stored on frontend
- [ ] JWT is attached to all API requests
- [ ] Backend validates JWT correctly
- [ ] Unauthorized requests return 401
- [ ] UI is responsive (320px to 2560px)

---

## Next Steps

Run `/sp.tasks` to generate detailed implementation tasks from this plan.
