---
id: 0001
title: Initial Constitution Ratification
stage: constitution
date: 2025-12-30
surface: agent
model: claude-opus-4-5-20251101
feature: none
branch: master
user: mesumali
command: /sp.constitution
labels: ["constitution", "governance", "security", "jwt", "fastapi", "nextjs"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - .specify/memory/constitution.md
  - history/prompts/constitution/0001-initial-constitution-ratification.constitution.prompt.md
tests:
  - null
---

## Prompt

Project: AI-Native Todo Full-Stack Web Application

Objective:
Transform a basic console-based todo application into a secure, multi-user, full-stack web application using a spec-driven, agentic development workflow.

Core principles:
- Security by default (JWT-based authentication and user isolation)
- Clear separation of concerns (frontend, backend, database)
- API correctness and RESTful design
- Data integrity and ownership enforcement
- Scalability and maintainability

Key standards:
- All features must map directly to the defined Basic Level requirements
- Every API endpoint must:
  - Be RESTful
  - Require JWT authentication
  - Enforce task ownership by authenticated user
- Authentication must be implemented using:
  - Better Auth on the Next.js frontend
  - JWT token verification on the FastAPI backend
- Shared JWT secret must be read from environment variable:
  - BETTER_AUTH_SECRET
- Backend must never trust client-provided user_id without JWT validation
- All database queries must be filtered by authenticated user ID
- No business logic in frontend beyond UI state handling

Technology constraints:
- Frontend: Next.js 16+ using App Router
- Backend: Python FastAPI
- ORM: SQLModel
- Database: Neon Serverless PostgreSQL
- Authentication: Better Auth (JWT-based)
- Spec-driven workflow: Claude Code + Spec-Kit Plus

API standards:
- Base path: /api
- Required endpoints:
  - GET    /api/{user_id}/tasks
  - POST   /api/{user_id}/tasks
  - GET    /api/{user_id}/tasks/{id}
  - PUT    /api/{user_id}/tasks/{id}
  - DELETE /api/{user_id}/tasks/{id}
  - PATCH  /api/{user_id}/tasks/{id}/complete
- Authorization:
  - All requests must include:
    Authorization: Bearer <JWT_TOKEN>
  - Requests without valid JWT must return 401 Unauthorized
- User ID in route must match JWT user ID

Security rules:
- JWT signature must be verified on every request
- JWT expiry must be enforced
- Users may only create, read, update, or delete their own tasks
- No cross-user data access under any condition
- Backend must be stateless (no shared session storage)

Data rules:
- Tasks must persist in Neon PostgreSQL
- Each task must be associated with exactly one user
- Deleting a task must not affect other users' data
- Completion status toggling must be idempotent

Frontend rules:
- Frontend must attach JWT token to every API request
- UI must be responsive and mobile-friendly
- Frontend must never directly access the database
- All data must come from backend APIs only

Error handling:
- Authentication errors → 401
- Authorization errors → 403
- Missing resources → 404
- Validation errors → 422
- Server errors → 500 with safe error messages

Success criteria:
- All 5 Basic Level features fully implemented
- Multi-user task isolation verified
- JWT authentication working end-to-end
- Backend rejects unauthorized and cross-user requests
- Responsive UI functioning across screen sizes
- Clean, readable, spec-compliant codebase

## Response snapshot

Created constitution v1.0.0 for AI-Native Todo Full-Stack Web Application with 7 core principles:

1. **Security by Default**: JWT auth, user isolation, no hardcoded secrets
2. **Separation of Concerns**: Next.js frontend, FastAPI backend, Neon PostgreSQL
3. **RESTful API Design**: User-scoped endpoints with proper status codes
4. **Data Integrity and Ownership**: User ID foreign key, filtered queries
5. **Error Handling Standards**: 401/403/404/422/500 status codes
6. **Frontend Standards**: Responsive UI, API-only data access
7. **Spec-Driven Development**: Small testable changes, spec traceability

Technology stack defined: Next.js 16+, Better Auth, FastAPI, SQLModel, Neon PostgreSQL.
Project structure established with backend/ and frontend/ directories.
Quality gates and governance process documented.

## Outcome

- ✅ Impact: High - established foundational governance for entire project
- 🧪 Tests: N/A - governance document, no code tests
- 📁 Files: 1 created (.specify/memory/constitution.md)
- 🔁 Next prompts: /sp.specify to create feature specs, /sp.plan for architecture
- 🧠 Reflection: Constitution captures all user requirements; 7 principles provide comprehensive coverage without over-engineering

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): N/A - initial document creation
- Prompt variant (if applicable): Standard /sp.constitution
- Next experiment (smallest change to try): Validate constitution during first feature spec
