---
id: 0001
title: Backend Authentication Refactor Specification
stage: spec
date: 2025-12-30
surface: agent
model: claude-opus-4-5-20251101
feature: 003-backend-auth-refactor
branch: 003-backend-auth-refactor
user: mesumali
command: /sp.specify
labels: ["authentication", "backend", "sqlmodel", "refactor", "specification"]
links:
  spec: specs/003-backend-auth-refactor/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/003-backend-auth-refactor/spec.md
  - specs/003-backend-auth-refactor/checklists/requirements.md
tests:
  - null
---

## Prompt

/sp.specify Yes do it option:2 write a specification as per our above discussions

Context from discussion:
- User clarified project requirements specify SQLModel as ONLY ORM (not Prisma)
- User stated: "but my project requirement is not prisma"
- User wants: Backend handles registration, login, JWT issuance; Frontend only has forms that call backend APIs
- Two options were presented:
  - Option 1: Better Auth with Drizzle
  - Option 2: Move ALL authentication to backend (recommended)
- User chose Option 2: Move ALL authentication to FastAPI backend using SQLModel

## Response snapshot

Created comprehensive specification for backend authentication refactor:

**Feature**: 003-backend-auth-refactor
**Branch**: 003-backend-auth-refactor

**User Stories** (5 total):
1. US1: User Registration (P1) - MVP entry point
2. US2: User Login (P1) - Primary auth flow
3. US3: JWT Token Verification (P1) - Protected API calls
4. US4: User Logout (P2) - Session termination
5. US5: Protected Route Access (P2) - Route protection

**Functional Requirements** (25 total):
- FR-001 to FR-007: Backend Authentication API (register, login, verify, bcrypt, JWT)
- FR-008 to FR-011: Backend Validation (email, password, duplicates)
- FR-012 to FR-014: Backend Storage with SQLModel
- FR-015 to FR-022: Frontend Requirements (API calls, JWT storage, redirects)
- FR-023 to FR-025: Cleanup Requirements (remove Better Auth, Prisma)

**Key Entities**:
- User: id, email, hashed_password, created_at, updated_at
- JWT Token: sub, email, exp (stateless)

**Success Criteria** (12 total):
- Zero Prisma/Better Auth dependencies
- All auth handled by FastAPI backend
- Performance targets for auth flows
- Manual E2E test validation

## Outcome

- ✅ Impact: High - Specification defines complete architecture refactor to align with project requirements
- 🧪 Tests: None (specification phase)
- 📁 Files: 2 files created (spec.md, requirements.md checklist)
- 🔁 Next prompts: /sp.plan to create implementation plan, /sp.tasks to generate tasks
- 🧠 Reflection: User clarified architecture early, preventing wasted implementation effort

## Evaluation notes (flywheel)

- Failure modes observed: Initial implementation used wrong ORM (Prisma instead of SQLModel per requirements)
- Graders run and results (PASS/FAIL): Requirements checklist - PASS (all criteria met)
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Proceed to planning phase with /sp.plan
