# Implementation Plan: Task Reminders & Notifications

**Branch**: `005-task-reminders` | **Date**: 2026-01-02 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `specs/005-task-reminders/spec.md`

## Summary

Implement a reminder and notification system that allows users to schedule task reminders at specific dates and times, with optional repeating intervals. The system evaluates reminders on-demand (login, page load, refresh) without background workers, displaying in-app notifications for due reminders.

**Technical Approach**:
- Backend: SQLModel database schema for reminders, FastAPI endpoints for CRUD operations, on-request reminder evaluation logic
- Frontend: Reminder creation UI, navbar notification badge with count, notification dropdown/list, popup modal for reminder details
- Integration: Leverage existing JWT auth and task CRUD system, sync reminder state between frontend and backend

## Technical Context

**Language/Version**: Python 3.11+ (backend), TypeScript 5.x (frontend)
**Primary Dependencies**: FastAPI, SQLModel, PyJWT (backend); Next.js 16+, Better Auth, Tailwind CSS (frontend)
**Storage**: Neon PostgreSQL via SQLModel ORM
**Testing**: pytest (backend), Jest/React Testing Library (frontend)
**Target Platform**: Web application (server-side API + client-side Next.js)
**Project Type**: Web (backend + frontend)
**Performance Goals**:
- Support 50+ concurrent due reminders per user
- Reminder evaluation completes within 200ms
- Notification popup appears within 5 seconds of page load
**Constraints**:
- No background workers or cron jobs (on-demand evaluation only)
- Stateless backend (each request independently evaluates reminders)
- Use server time for all reminder calculations
- Reminders must persist across sessions
**Scale/Scope**:
- Multi-user system (user-scoped reminders via JWT)
- Support up to 100 repeats per reminder
- Handle hundreds of overdue reminders gracefully

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Security by Default
- ✅ All reminder API endpoints MUST require JWT authentication
- ✅ JWT signatures verified using `BETTER_AUTH_SECRET` environment variable
- ✅ Reminders MUST be user-scoped; users can only access their own reminders
- ✅ Backend validates `user_id` in route matches JWT claim
- ✅ No secrets hardcoded; all sensitive values use environment variables

**Status**: PASS - All reminder endpoints will enforce JWT auth and user ownership validation

### Separation of Concerns
- ✅ Frontend: Reminder UI components, client-side state, API request orchestration
- ✅ Backend: Reminder evaluation logic, authentication verification, database access
- ✅ Database: Reminder persistence via SQLModel ORM
- ✅ No business logic in frontend (reminder evaluation server-side only)
- ✅ Backend stateless (no shared session storage)
- ✅ All database queries filtered by authenticated user ID

**Status**: PASS - Clear separation maintained across all layers

### RESTful API Design
- ✅ Base path: `/api`
- ✅ User-scoped routes:
  - `POST /api/{user_id}/reminders` - Create reminder
  - `GET /api/{user_id}/reminders/due` - Fetch due reminders
  - `DELETE /api/{user_id}/reminders/{id}` - Delete reminder
- ✅ JWT validation required on all endpoints
- ✅ Route `user_id` must match JWT user ID (403 on mismatch)
- ✅ Appropriate HTTP status codes (401, 403, 404, 422, 500)

**Status**: PASS - Follows established API patterns from task CRUD system

### Data Integrity and Ownership
- ✅ Each reminder associated with exactly one user and one task via foreign keys
- ✅ Reminders persist in Neon PostgreSQL with SQLModel ORM
- ✅ All queries include user ID filter from authenticated JWT
- ✅ Backend never trusts client-provided user_id without JWT validation
- ✅ Cascade delete or prevent task deletion with active reminders

**Status**: PASS - Referential integrity enforced via foreign keys

### Error Handling Standards
- ✅ 401 Unauthorized: Missing or invalid JWT token
- ✅ 403 Forbidden: Valid JWT but wrong user_id
- ✅ 404 Not Found: Reminder/task does not exist or user lacks access
- ✅ 422 Unprocessable Entity: Invalid reminder data (bad date, negative interval, etc.)
- ✅ 500 Internal Server Error: Safe messages without stack traces

**Status**: PASS - Consistent with existing error handling patterns

### Frontend Standards
- ✅ JWT token attached to every reminder API request via Authorization header
- ✅ Responsive UI across mobile and desktop (Tailwind CSS)
- ✅ No direct database access (all data via backend APIs)
- ✅ Better Auth used for authentication flow
- ✅ Client-side state handles UI only (notification count, popup visibility)

**Status**: PASS - Aligns with existing frontend architecture

### Spec-Driven Development
- ✅ Feature maps directly to defined requirements in spec.md
- ✅ Implementation guided by specs, plan, and tasks artifacts
- ✅ Changes are small and testable (incremental rollout: schema → API → UI)
- ✅ No invented APIs or contracts (all defined in spec and this plan)

**Status**: PASS - Follows spec-driven workflow

## Project Structure

### Documentation (this feature)

```text
specs/005-task-reminders/
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output (/sp.plan command)
├── data-model.md        # Phase 1 output (/sp.plan command)
├── quickstart.md        # Phase 1 output (/sp.plan command)
├── contracts/           # Phase 1 output (/sp.plan command)
│   ├── reminders.openapi.yaml
│   └── reminder-schemas.json
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
backend/
├── src/
│   ├── models/
│   │   ├── reminder.py           # NEW: Reminder SQLModel entity
│   │   ├── task.py               # EXISTING: Task model (may need FK update)
│   │   └── user.py               # EXISTING: User model
│   ├── services/
│   │   └── reminder_service.py   # NEW: Reminder evaluation logic
│   ├── api/
│   │   └── reminders.py          # NEW: Reminder CRUD endpoints
│   ├── database.py               # UPDATE: Import Reminder model
│   └── main.py                   # UPDATE: Include reminder routes
└── tests/
    ├── test_reminder_model.py    # NEW: Reminder model tests
    ├── test_reminder_service.py  # NEW: Reminder evaluation tests
    └── test_reminder_api.py      # NEW: Reminder API tests

frontend/
├── src/
│   ├── components/
│   │   ├── reminders/
│   │   │   ├── ReminderForm.tsx           # NEW: Reminder creation UI
│   │   │   ├── NotificationBadge.tsx      # NEW: Navbar notification count
│   │   │   ├── NotificationDropdown.tsx   # NEW: Notification list
│   │   │   └── NotificationModal.tsx      # NEW: Reminder detail popup
│   │   └── navbar/
│   │       └── Navbar.tsx                 # UPDATE: Add notification badge
│   ├── app/
│   │   └── (protected)/
│   │       └── tasks/
│   │           └── page.tsx               # UPDATE: Integrate reminder UI
│   └── lib/
│       └── api/
│           └── reminders.ts               # NEW: Reminder API client
└── tests/
    └── components/
        └── reminders/
            ├── ReminderForm.test.tsx
            └── NotificationModal.test.tsx
```

**Structure Decision**: Web application structure (Option 2). The existing backend/ and frontend/ directories are used. New reminder functionality integrates with existing task and auth systems.

**Key Integration Points**:
- backend/src/models/reminder.py references existing Task and User models via foreign keys
- backend/src/api/reminders.py reuses existing JWT auth middleware
- frontend/src/lib/api/reminders.ts follows existing API client patterns
- frontend/src/components/navbar updates to show notification badge

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

**No violations detected.** All Constitution Check items passed without requiring exceptions.
