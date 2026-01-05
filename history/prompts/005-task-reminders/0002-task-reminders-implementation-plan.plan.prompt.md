---
id: 0002
title: task-reminders-implementation-plan
stage: plan
date: 2026-01-02
surface: agent
model: claude-sonnet-4-5-20250929
feature: 005-task-reminders
branch: 005-task-reminders
user: developer
command: /sp.plan
labels: ["task-reminders", "notifications", "implementation-plan", "architecture"]
links:
  spec: specs/005-task-reminders/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/005-task-reminders/plan.md
  - specs/005-task-reminders/research.md
  - specs/005-task-reminders/data-model.md
  - specs/005-task-reminders/quickstart.md
  - specs/005-task-reminders/contracts/reminders.openapi.yaml
  - CLAUDE.md
tests:
  - Constitution Check validation (all gates passed)
---

## Prompt

/sp.plan

Create:
- Reminder database schema
- Backend reminder evaluation logic
- Reminder CRUD APIs
- Frontend notification system

Execution phases:

1. Database design
   - Create reminders table
   - Fields: id, user_id, task_id, remind_at, repeat_interval_minutes, repeat_count, triggered_count, is_active, created_at
   - Index on user_id and remind_at

2. Backend reminder logic
   - On authenticated request: Check reminders where remind_at <= now, is_active = true
   - Increment triggered_count
   - Calculate next remind_at if repeats remain
   - Deactivate reminder when repeat_count reached

3. Backend APIs
   - POST   /api/{user_id}/reminders
   - GET    /api/{user_id}/reminders/due
   - DELETE /api/{user_id}/reminders/{id}
   - Enforce JWT and user ownership

4. Frontend reminder UI
   - Reminder creation form (date, time, interval, count)
   - Navbar notification icon with badge
   - Notification dropdown/list
   - Popup reminder modal
   - Reminder delete action

5. Integration & UX
   - On login: Fetch due reminders, show popup if any exist
   - Clicking notification icon: Show popup and list
   - Sync deletion with backend

Decisions needing documentation:
- Login-time evaluation instead of background jobs
- In-app notifications over OS-level alerts
- Repeat logic handled server-side
- Hard delete reminders when user deletes

Testing strategy:
- Set reminder → saved in DB
- Login after reminder time → popup appears
- Navbar shows correct count
- Repeat reminders trigger correct number of times
- Delete reminder → never appears again
- Other user cannot see reminder

Validation checks:
- Reminders are user-scoped
- Repeat logic stops correctly
- No duplicate notifications
- UI state matches backend state
- No reminders fire after deletion

Technical details:
- Use server time for reminder evaluation
- Convert frontend local time to ISO datetime
- Use SQLModel for reminder persistence
- Reuse existing API client and auth middleware

## Response snapshot

Created comprehensive implementation plan for Task Reminders & Notifications feature (005-task-reminders).

**Planning Artifacts Generated**:

1. **plan.md**: Complete technical context, constitution check, and project structure
   - All constitution gates PASS (no violations)
   - Performance goals: 50+ concurrent reminders, <200ms evaluation, <5s notification display
   - Constraints: No background workers, stateless backend, on-demand evaluation only
   - Source structure defined for backend (models, services, API) and frontend (components, lib)

2. **research.md**: 6 key technical decisions with implementation patterns
   - On-demand reminder evaluation (no background workers)
   - Server-side repeat logic calculation
   - Ephemeral notification model (API response, not database table)
   - Hard delete strategy
   - UTC timezone handling
   - Cascade delete for task removal

3. **data-model.md**: Complete Reminder entity schema
   - 9 fields with constraints and validation rules
   - 4 indexes (including composite index for optimal query performance)
   - State transition diagram
   - SQLModel implementation with example queries
   - Performance estimates: 10-50ms for due reminder queries

4. **contracts/reminders.openapi.yaml**: OpenAPI 3.1 specification
   - 3 endpoints: POST create, GET due reminders, DELETE reminder
   - Full request/response schemas with examples
   - Error response definitions (401, 403, 404, 422, 500)
   - Security scheme: JWT Bearer authentication

5. **quickstart.md**: 7-phase implementation guide
   - Phase 1: Database schema (30 min)
   - Phase 2: Reminder service logic (45 min)
   - Phase 3: API endpoints (60 min)
   - Phase 4: Frontend API client (30 min)
   - Phase 5: Reminder creation UI (60 min)
   - Phase 6: Notification UI (90 min)
   - Phase 7: Integration (45 min)
   - Total estimate: ~6 hours

6. **CLAUDE.md**: Updated agent context with reminder feature technologies

**Architecture Highlights**:
- Web application structure (backend + frontend)
- Reminder table with foreign keys to User and Task (cascade delete)
- On-demand evaluation during API requests (login, page load, refresh)
- Server-side repeat calculation (atomic updates)
- JWT auth enforcement on all endpoints
- Responsive UI with Tailwind CSS

**Key Design Patterns**:
- User-scoped queries (all reminders filtered by authenticated user_id)
- Stateless backend (each request independently evaluates due reminders)
- UTC storage with local display (timezone-safe)
- Composite index optimization (user_id + is_active + remind_at)

## Outcome

- ✅ Impact: Complete implementation plan with 5 artifacts (plan, research, data-model, contracts, quickstart) ready for /sp.tasks
- 🧪 Tests: Constitution Check - PASS (all 6 principles validated)
- 📁 Files: 5 planning artifacts created + 1 agent context updated
- 🔁 Next prompts: /sp.tasks (generate actionable tasks from plan)
- 🧠 Reflection: Plan is comprehensive with no architectural ambiguities. All technical decisions documented with rationale and alternatives. Ready for task breakdown.

## Evaluation notes (flywheel)

- Failure modes observed: None - all constitution gates passed, no design conflicts identified
- Graders run and results (PASS/FAIL): Constitution Check - PASS (Security, Separation, REST, Data Integrity, Errors, Frontend, Spec-Driven all validated)
- Prompt variant (if applicable): Standard /sp.plan workflow with user-provided execution phases
- Next experiment (smallest change to try): Proceed to /sp.tasks to generate task breakdown
