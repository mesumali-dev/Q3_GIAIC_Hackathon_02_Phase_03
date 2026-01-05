---
id: 0002
title: Create JWT Auth Implementation Plan
stage: plan
date: 2025-12-30
surface: agent
model: claude-opus-4-5-20251101
feature: 002-jwt-auth
branch: 002-jwt-auth
user: mesumali
command: /sp.plan
labels: ["authentication", "jwt", "better-auth", "implementation-plan", "fastapi"]
links:
  spec: specs/002-jwt-auth/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/002-jwt-auth/plan.md
  - specs/002-jwt-auth/research.md
  - specs/002-jwt-auth/data-model.md
  - specs/002-jwt-auth/quickstart.md
  - specs/002-jwt-auth/contracts/auth-api.yaml
tests:
  - null
---

## Prompt

Create:
- Authentication feature spec
- Frontend auth UI
- Backend JWT verification layer
- API request protection

Execution phases:

1. Authentication specification
   - Define authentication flow
   - Define JWT structure and claims
   - Define frontend-backend interaction

2. Frontend authentication setup
   - Configure Better Auth with JWT plugin
   - Implement /login and /register pages
   - Handle form submission and error states
   - Store JWT securely
   - Implement auth-aware routing
   - Add API client that injects JWT header

3. Backend JWT verification
   - Read BETTER_AUTH_SECRET from environment
   - Add FastAPI middleware for JWT verification
   - Decode and validate token
   - Extract user identity into request context
   - Reject invalid or missing tokens

4. API protection
   - Protect all /api/* routes
   - Return standardized auth errors (401 / 403)

Decisions needing documentation:
- JWT-based stateless authentication vs session-based auth
- Frontend-issued JWT verified by backend
- Middleware-based auth enforcement vs per-route checks
- Minimal UI over design-heavy UI (hackathon priority)

Testing strategy:
- Register new user → success
- Login → JWT issued
- API call without token → 401
- API call with invalid token → 401
- API call with valid token → 200
- Token expiry respected

Validation checks:
- JWT secret shared between frontend and backend
- Frontend does not call backend without JWT
- Backend does not trust user_id from client

Technical details:
- Use Better Auth JWT plugin
- Use Authorization header for tokens
- Keep backend stateless
- Prepare for task CRUD in Part 3

## Response snapshot

Created comprehensive implementation plan for JWT Authentication feature:

**Phase 0 (Research)**:
- Researched Better Auth JWT plugin configuration
- Decided on HS256 algorithm with shared BETTER_AUTH_SECRET
- Chose localStorage for token storage (cross-origin requirement)
- Documented PyJWT verification pattern for FastAPI

**Phase 1 (Design Artifacts)**:
- Created data-model.md with User, Session, Account entities
- Created OpenAPI contract at contracts/auth-api.yaml
- Created quickstart.md with setup and testing instructions
- Updated CLAUDE.md agent context

**Implementation Plan**:
- Phase 1: Backend JWT Middleware (PyJWT verification, CORS, test endpoint)
- Phase 2: Frontend Better Auth Setup (install, configure, migrations)
- Phase 3: Authentication Pages (login, register with Tailwind)
- Phase 4: Route Protection (middleware, API client JWT injection)
- Phase 5: Integration Testing

**Constitution Check**: All 9 principles verified - PASSED

## Outcome

- ✅ Impact: High - Complete implementation plan ready for task generation
- 🧪 Tests: N/A - Planning phase (no code)
- 📁 Files: 5 files created (plan.md, research.md, data-model.md, quickstart.md, auth-api.yaml)
- 🔁 Next prompts: `/sp.tasks` to generate implementation tasks
- 🧠 Reflection: Research on Better Auth was crucial; HS256 decision simplifies cross-service auth

## Evaluation notes (flywheel)

- Failure modes observed: None - constitution check passed
- Graders run and results (PASS/FAIL): Constitution gates - PASS
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Proceed to task generation
