# Research: Task CRUD Implementation

**Feature**: 004-task-crud
**Date**: 2026-01-01
**Status**: Complete

## Overview

Research completed for implementing Task CRUD functionality. All technical decisions align with existing codebase patterns established in 003-backend-auth-refactor.

## Decisions

### 1. Task Model Structure

**Decision**: SQLModel entity with UUID primary key, foreign key to User

**Rationale**:
- Follows existing User model pattern in `backend/src/models/user.py`
- UUID provides secure, non-guessable identifiers
- SQLModel provides type-safe ORM with Pydantic validation

**Alternatives Considered**:
- Integer auto-increment IDs: Rejected (predictable, security concern)
- String IDs: Rejected (UUID provides standardized format)

### 2. API Route Pattern

**Decision**: `/api/{user_id}/tasks` with user ownership validation

**Rationale**:
- Matches constitution requirement (Principle III)
- User ID in route enables explicit ownership verification
- Existing `verify_user_ownership()` middleware supports this pattern

**Alternatives Considered**:
- `/api/tasks` with user from JWT only: Rejected (less explicit, harder to audit)
- `/api/users/{user_id}/tasks`: Rejected (nested resources add complexity)

### 3. Frontend Task API Client

**Decision**: Extend existing `api.ts` with typed Task methods

**Rationale**:
- Placeholder methods already exist in `frontend/src/lib/api.ts`
- Reuses `apiRequest<T>()` helper with automatic JWT attachment
- TypeScript types ensure compile-time safety

**Alternatives Considered**:
- Separate task-api.ts file: Rejected (adds fragmentation)
- React Query/SWR: Out of scope for MVP (simple fetch sufficient)

### 4. Task Pages Structure

**Decision**: Separate pages for list, create, and detail/edit

**Rationale**:
- Follows Next.js App Router conventions
- Enables deep linking to individual tasks
- Server-side rendering support for better UX

**Alternatives Considered**:
- Modal-heavy SPA approach: Rejected (less accessible, harder to deep link)
- Single page with tabs: Rejected (state management complexity)

### 5. Delete Behavior

**Decision**: Hard delete with confirmation dialog

**Rationale**:
- Simpler implementation for MVP
- User explicitly asked for permanent deletion
- No audit trail requirement in spec

**Alternatives Considered**:
- Soft delete with `deleted_at`: Rejected (adds complexity, no requirement)
- Trash/restore flow: Rejected (out of scope)

### 6. Database Indexes

**Decision**: Indexes on `user_id` and `is_completed`

**Rationale**:
- `user_id` index required for query performance (FR-019)
- `is_completed` index enables future filtering optimization (FR-020)
- SQLModel Field `index=True` provides this

**Alternatives Considered**:
- Composite index on (user_id, is_completed): Can be added later if needed
- No indexes: Rejected (performance requirement)

### 7. Completion Toggle Endpoint

**Decision**: PATCH `/api/{user_id}/tasks/{id}/complete` toggles current state

**Rationale**:
- Idempotent from server perspective (current state → opposite)
- Simpler than PUT with explicit is_completed value
- Matches constitution endpoint pattern

**Alternatives Considered**:
- PUT with `is_completed: true/false`: More explicit but requires extra client logic
- POST to `/complete` or `/uncomplete`: Adds endpoint sprawl

## Dependencies Verified

| Dependency | Status | Notes |
|------------|--------|-------|
| SQLModel | ✅ Installed | Version in pyproject.toml |
| FastAPI | ✅ Installed | Already used for auth |
| PyJWT | ✅ Installed | JWT verification working |
| Neon PostgreSQL | ✅ Configured | DATABASE_URL in .env |
| Next.js App Router | ✅ Working | Login/register pages exist |
| Tailwind CSS | ✅ Installed | Used in existing pages |

## Existing Code to Leverage

### Backend

- `src/models/user.py`: Pattern for SQLModel entity
- `src/middleware/auth.py`: JWT verification, `CurrentUser` type, `verify_user_ownership()`
- `src/database.py`: Session management with `get_db()` dependency
- `src/api/auth.py`: FastAPI router pattern

### Frontend

- `src/lib/api.ts`: `apiRequest<T>()` helper, placeholder task methods
- `src/lib/auth-helper.ts`: `getToken()`, `getStoredUser()` for user ID
- `src/app/login/page.tsx`: Form pattern with loading/error states
- `src/app/register/page.tsx`: Form validation pattern
- `middleware.ts`: Route protection pattern

## No Outstanding Clarifications

All technical decisions are resolved based on:
1. Constitution requirements
2. Existing codebase patterns
3. Feature specification constraints
