<!--
SYNC IMPACT REPORT
==================
Version change: 0.0.0 → 1.0.0 (initial ratification)
Modified principles: N/A (initial version)
Added sections:
  - Core Principles (7 principles)
  - Technology Stack (Section 2)
  - Development Workflow (Section 3)
  - Governance
Removed sections: N/A (initial version)
Templates status:
  - .specify/templates/plan-template.md ✅ compatible (Constitution Check section present)
  - .specify/templates/spec-template.md ✅ compatible (requirements structure aligned)
  - .specify/templates/tasks-template.md ✅ compatible (phase structure aligned)
Deferred items: None
-->

# AI-Native Todo Full-Stack Web Application Constitution

## Core Principles

### I. Security by Default

All system components MUST enforce security measures without requiring explicit opt-in:

- Every API endpoint MUST require JWT authentication via the `Authorization: Bearer <token>` header
- JWT signatures MUST be verified on every request using `BETTER_AUTH_SECRET` environment variable
- JWT expiry MUST be enforced; expired tokens MUST return 401 Unauthorized
- Users MUST only access their own tasks; cross-user data access is forbidden under all conditions
- Backend MUST validate that the `user_id` in route parameters matches the JWT claim
- No secrets or tokens MUST be hardcoded; all sensitive values MUST use environment variables
- Frontend MUST never directly access the database; all data flows through authenticated API calls

**Rationale**: Security vulnerabilities in multi-user applications can expose sensitive data. Defense-in-depth through mandatory authentication and authorization prevents data breaches.

### II. Separation of Concerns

The application MUST maintain strict boundaries between architectural layers:

- **Frontend (Next.js 16+ App Router)**: UI rendering, client-side state, API request orchestration
- **Backend (FastAPI)**: Business logic, authentication verification, data access
- **Database (Neon PostgreSQL)**: Data persistence via SQLModel ORM
- No business logic MUST exist in the frontend beyond UI state handling
- Backend MUST be stateless; no shared session storage between requests
- All database queries MUST be filtered by authenticated user ID

**Rationale**: Clear separation enables independent testing, deployment, and scaling of each layer while reducing the blast radius of changes.

### III. RESTful API Design

All API endpoints MUST follow REST conventions and ownership patterns:

- Base path: `/api`
- Required endpoints with user-scoped routes:
  - `GET /api/{user_id}/tasks` - List all tasks for user
  - `POST /api/{user_id}/tasks` - Create new task
  - `GET /api/{user_id}/tasks/{id}` - Get specific task
  - `PUT /api/{user_id}/tasks/{id}` - Update task
  - `DELETE /api/{user_id}/tasks/{id}` - Delete task
  - `PATCH /api/{user_id}/tasks/{id}/complete` - Toggle completion status
- Requests without valid JWT MUST return 401 Unauthorized
- Route `user_id` MUST match JWT user ID; mismatch MUST return 403 Forbidden
- Completion status toggling MUST be idempotent

**Rationale**: Consistent API design reduces cognitive load, enables predictable client implementations, and enforces ownership at the URL level.

### IV. Data Integrity and Ownership

Every data operation MUST preserve integrity and enforce ownership:

- Each task MUST be associated with exactly one user via foreign key
- Tasks MUST persist in Neon PostgreSQL with SQLModel ORM
- Deleting a task MUST NOT affect other users' data
- All database queries MUST include user ID filter from authenticated JWT
- Backend MUST never trust client-provided user_id without JWT validation

**Rationale**: Data integrity ensures consistency and prevents corruption. Ownership enforcement at the data layer provides defense-in-depth beyond API authorization.

### V. Error Handling Standards

All errors MUST use consistent HTTP status codes with safe messages:

- 401 Unauthorized: Missing or invalid JWT token
- 403 Forbidden: Valid JWT but user lacks permission (wrong user_id)
- 404 Not Found: Resource does not exist or user lacks access
- 422 Unprocessable Entity: Request validation failures
- 500 Internal Server Error: Server errors with safe messages (no stack traces)
- Error responses MUST NOT expose internal implementation details

**Rationale**: Consistent error handling improves debuggability for developers and prevents information leakage to potential attackers.

### VI. Frontend Standards

The Next.js frontend MUST follow these UI/UX requirements:

- Frontend MUST attach JWT token to every API request via Authorization header
- UI MUST be responsive and mobile-friendly across all screen sizes
- Frontend MUST never directly query the database
- All data MUST be fetched from backend APIs only
- Better Auth MUST be used for authentication flow on the frontend
- Client-side state MUST only handle UI concerns, not business logic

**Rationale**: Responsive design ensures accessibility across devices. Strict API-only data access maintains security boundaries and enables backend changes without frontend updates.

### VII. Spec-Driven Development

All implementation MUST follow the spec-driven workflow:

- Features MUST map directly to defined Basic Level requirements
- Implementation MUST be guided by specs, plans, and tasks artifacts
- Changes MUST be small, testable, and reference code precisely
- No APIs, data, or contracts MUST be invented; ask targeted clarifiers if missing
- Prefer the smallest viable diff; do not refactor unrelated code
- Cite existing code with code references; propose new code in fenced blocks

**Rationale**: Spec-driven development ensures traceability from requirements to implementation, reduces scope creep, and enables clear acceptance criteria.

## Technology Stack

The following technology constraints are mandatory for all implementations:

| Layer | Technology | Version/Notes |
|-------|------------|---------------|
| Frontend Framework | Next.js | 16+ with App Router |
| Frontend Auth | Better Auth | JWT-based authentication |
| Backend Framework | Python FastAPI | Latest stable |
| ORM | SQLModel | For Python data models |
| Database | Neon Serverless PostgreSQL | Cloud-hosted |
| Auth Secret | `BETTER_AUTH_SECRET` | Environment variable for JWT |
| Workflow | Claude Code + Spec-Kit Plus | Spec-driven development |

### API Contract Summary

```
Authorization: Bearer <JWT_TOKEN> (required on all endpoints)

GET    /api/{user_id}/tasks           → List tasks
POST   /api/{user_id}/tasks           → Create task
GET    /api/{user_id}/tasks/{id}      → Get task
PUT    /api/{user_id}/tasks/{id}      → Update task
DELETE /api/{user_id}/tasks/{id}      → Delete task
PATCH  /api/{user_id}/tasks/{id}/complete → Toggle complete
```

## Development Workflow

### Quality Gates

All changes MUST pass these gates before merge:

1. **Security Review**: JWT auth implemented, no hardcoded secrets
2. **API Compliance**: Endpoints match contract, proper status codes
3. **Data Isolation**: Queries filter by authenticated user
4. **Responsive Check**: UI works on mobile and desktop
5. **Error Handling**: All paths return appropriate status codes

### Project Structure

```text
backend/
├── src/
│   ├── models/      # SQLModel entities
│   ├── services/    # Business logic
│   └── api/         # FastAPI routes
└── tests/

frontend/
├── src/
│   ├── components/  # React components
│   ├── app/         # Next.js App Router pages
│   └── lib/         # Utilities, auth, API clients
└── tests/
```

### Commit Standards

- Commits MUST be atomic and focused on single concerns
- Commit messages MUST follow conventional format
- Security-sensitive changes MUST be explicitly noted

## Governance

This constitution supersedes all other practices for this project.

### Amendment Process

1. Proposed changes MUST be documented with rationale
2. Amendments MUST specify version bump type (MAJOR/MINOR/PATCH)
3. Breaking changes to principles require MAJOR version bump
4. New principles or material expansions require MINOR version bump
5. Clarifications and typo fixes require PATCH version bump

### Compliance

- All PRs MUST verify compliance with these principles
- Complexity MUST be justified against Principle VII (smallest viable diff)
- Security violations are blocking issues

### Success Criteria

The project is considered successful when:

- [ ] All 5 Basic Level features fully implemented
- [ ] Multi-user task isolation verified
- [ ] JWT authentication working end-to-end
- [ ] Backend rejects unauthorized and cross-user requests
- [ ] Responsive UI functioning across screen sizes
- [ ] Clean, readable, spec-compliant codebase

**Version**: 1.0.0 | **Ratified**: 2025-12-30 | **Last Amended**: 2025-12-30
