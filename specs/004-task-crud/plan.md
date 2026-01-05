# Implementation Plan: Task CRUD

**Branch**: `004-task-crud` | **Date**: 2026-01-01 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/004-task-crud/spec.md`

## Summary

Implement complete task management (CRUD + toggle completion) for multi-user todo app. Backend provides RESTful API with JWT authentication and user ownership validation. Frontend provides responsive UI with task list, create, edit, and delete functionality using existing auth infrastructure.

## Technical Context

**Language/Version**: Python 3.11+ (backend), TypeScript 5.x (frontend)
**Primary Dependencies**: FastAPI, SQLModel, PyJWT (backend); Next.js 16+, Tailwind CSS (frontend)
**Storage**: Neon PostgreSQL via SQLModel ORM
**Testing**: pytest (backend), manual E2E (frontend)
**Target Platform**: Linux server (backend), Web browsers (frontend)
**Project Type**: Web application (frontend + backend)
**Performance Goals**: <2s page load, <1s operations
**Constraints**: JWT auth required, user isolation enforced
**Scale/Scope**: Single-user testing, ~100 tasks per user

## Constitution Check

*GATE: All checks passed*

| Principle | Status | Evidence |
|-----------|--------|----------|
| I. Security by Default | ✅ PASS | JWT required on all endpoints, user_id validation, no hardcoded secrets |
| II. Separation of Concerns | ✅ PASS | Backend handles business logic, frontend is pure UI, no direct DB access |
| III. RESTful API Design | ✅ PASS | Endpoints match constitution contract exactly |
| IV. Data Integrity | ✅ PASS | FK to users, queries filtered by user_id from JWT |
| V. Error Handling | ✅ PASS | Proper status codes: 401, 403, 404, 422, 500 |
| VI. Frontend Standards | ✅ PASS | JWT attached to requests, responsive Tailwind UI, API-only data access |
| VII. Spec-Driven Development | ✅ PASS | All requirements trace to spec, smallest viable diff |

## Project Structure

### Documentation (this feature)

```text
specs/004-task-crud/
├── spec.md              # Feature specification
├── plan.md              # This file
├── research.md          # Research decisions
├── data-model.md        # Entity definitions
├── quickstart.md        # Implementation guide
├── contracts/
│   └── openapi.yaml     # API contract
└── checklists/
    └── requirements.md  # Validation checklist
```

### Source Code (repository root)

```text
backend/
├── src/
│   ├── models/
│   │   ├── __init__.py      # Export Task (modify)
│   │   ├── user.py          # Existing User model
│   │   └── task.py          # NEW: Task SQLModel
│   ├── schemas/
│   │   ├── __init__.py      # Export schemas (modify)
│   │   ├── auth.py          # Existing auth schemas
│   │   └── task.py          # NEW: Task Pydantic schemas
│   ├── services/
│   │   ├── __init__.py      # Export services (modify)
│   │   ├── auth.py          # Existing auth service
│   │   └── task.py          # NEW: Task business logic
│   ├── api/
│   │   ├── __init__.py      # Export routers
│   │   ├── auth.py          # Existing auth routes
│   │   └── tasks.py         # NEW: Task routes
│   ├── middleware/
│   │   └── auth.py          # Existing JWT middleware (reuse)
│   ├── main.py              # Register tasks router (modify)
│   ├── database.py          # Import Task for tables (modify)
│   └── config.py            # Existing config
└── tests/
    ├── test_health.py       # Existing
    └── test_tasks.py        # NEW: Task endpoint tests

frontend/
├── src/
│   ├── app/
│   │   ├── tasks/
│   │   │   ├── page.tsx         # NEW: Task list page
│   │   │   ├── new/
│   │   │   │   └── page.tsx     # NEW: Create task page
│   │   │   └── [id]/
│   │   │       └── page.tsx     # NEW: Task detail/edit page
│   │   ├── login/               # Existing
│   │   ├── register/            # Existing
│   │   └── page.tsx             # Modify: add link to /tasks
│   ├── components/
│   │   ├── TaskCard.tsx         # NEW: Task display
│   │   ├── TaskForm.tsx         # NEW: Create/edit form
│   │   ├── TaskList.tsx         # NEW: List container
│   │   └── ConfirmDialog.tsx    # NEW: Delete confirmation
│   └── lib/
│       ├── api.ts               # Modify: implement task methods
│       └── auth-helper.ts       # Existing (reuse)
├── middleware.ts                # Modify: protect /tasks routes
└── package.json                 # No changes expected
```

**Structure Decision**: Web application pattern with separate backend and frontend directories, following existing project structure from 003-backend-auth-refactor.

## Complexity Tracking

> No violations - all implementations follow constitution principles

| Decision | Justification |
|----------|---------------|
| Separate service layer | Matches existing auth.py pattern, enables testability |
| Pydantic schemas | Required for FastAPI request validation |
| Component-based UI | Matches Next.js patterns, enables reuse |

## Implementation Phases

### Phase 1: Backend Task Model & Schema

**Goal**: Define database entity and request/response types

**Files**:
- `backend/src/models/task.py` (create)
- `backend/src/models/__init__.py` (modify)
- `backend/src/schemas/task.py` (create)
- `backend/src/schemas/__init__.py` (create or modify)
- `backend/src/database.py` (modify - import Task)

**Acceptance**:
- [ ] Task table created in database on startup
- [ ] Task model has all fields from data-model.md
- [ ] Schemas validate title length (1-200) and description length (0-1000)

### Phase 2: Backend Task Service

**Goal**: Business logic for task operations

**Files**:
- `backend/src/services/task.py` (create)
- `backend/src/services/__init__.py` (create or modify)

**Methods**:
```python
create_task(db: Session, user_id: UUID, data: TaskCreate) -> Task
get_tasks(db: Session, user_id: UUID) -> list[Task]
get_task(db: Session, user_id: UUID, task_id: UUID) -> Task | None
update_task(db: Session, user_id: UUID, task_id: UUID, data: TaskUpdate) -> Task | None
delete_task(db: Session, user_id: UUID, task_id: UUID) -> bool
toggle_complete(db: Session, user_id: UUID, task_id: UUID) -> Task | None
```

**Acceptance**:
- [ ] All methods filter by user_id
- [ ] update_task sets updated_at timestamp
- [ ] toggle_complete inverts is_completed

### Phase 3: Backend Task Routes

**Goal**: RESTful API endpoints

**Files**:
- `backend/src/api/tasks.py` (create)
- `backend/src/main.py` (modify)

**Endpoints** (per constitution):
```
GET    /api/{user_id}/tasks           → listTasks
POST   /api/{user_id}/tasks           → createTask
GET    /api/{user_id}/tasks/{id}      → getTask
PUT    /api/{user_id}/tasks/{id}      → updateTask
DELETE /api/{user_id}/tasks/{id}      → deleteTask
PATCH  /api/{user_id}/tasks/{id}/complete → toggleComplete
```

**Acceptance**:
- [ ] All endpoints require JWT (verify_jwt dependency)
- [ ] user_id in route validated against JWT (verify_user_ownership)
- [ ] Correct HTTP status codes returned
- [ ] Swagger docs show all endpoints at /docs

### Phase 4: Backend Tests

**Goal**: Verify backend API works correctly

**Files**:
- `backend/tests/test_tasks.py` (create)

**Test Cases**:
- [ ] Create task returns 201
- [ ] List tasks returns only user's tasks
- [ ] Get task returns 404 for non-existent
- [ ] Update task changes title/description
- [ ] Delete task returns 204
- [ ] Toggle changes is_completed
- [ ] Wrong user_id returns 403
- [ ] Missing token returns 401

**Acceptance**:
- [ ] All tests pass: `uv run pytest tests/test_tasks.py`

### Phase 5: Frontend API Client

**Goal**: Connect frontend to backend task API

**Files**:
- `frontend/src/lib/api.ts` (modify)

**Changes**:
- Replace placeholder `getTasks()` with real implementation
- Replace placeholder `createTask()` with real implementation
- Replace placeholder `updateTask()` with real implementation
- Replace placeholder `deleteTask()` with real implementation
- Replace placeholder `toggleTaskComplete()` with real implementation
- Add `getTask(userId, taskId)` method

**Acceptance**:
- [ ] All methods use `apiRequest<T>()` helper
- [ ] TypeScript types match backend schemas
- [ ] 401 responses trigger redirect to login

### Phase 6: Frontend Task Components

**Goal**: Reusable UI components

**Files**:
- `frontend/src/components/TaskCard.tsx` (create)
- `frontend/src/components/TaskForm.tsx` (create)
- `frontend/src/components/TaskList.tsx` (create)
- `frontend/src/components/ConfirmDialog.tsx` (create)

**Component Specs**:

**TaskCard**:
- Props: task, onToggle, onEdit, onDelete
- Displays: title, description (truncated), completion checkbox, created date
- Styling: completed tasks have strikethrough title

**TaskForm**:
- Props: initialData?, onSubmit, onCancel, isLoading
- Fields: title (required), description (optional)
- Client-side validation before submit

**TaskList**:
- Props: tasks, isLoading, onToggle, onEdit, onDelete
- Empty state when no tasks
- Loading skeleton during fetch

**ConfirmDialog**:
- Props: isOpen, title, message, onConfirm, onCancel
- Modal overlay with confirm/cancel buttons

**Acceptance**:
- [ ] Components render without errors
- [ ] Tailwind responsive classes applied
- [ ] Proper accessibility (labels, button types)

### Phase 7: Frontend Task Pages

**Goal**: Complete task management UI

**Files**:
- `frontend/src/app/tasks/page.tsx` (create)
- `frontend/src/app/tasks/new/page.tsx` (create)
- `frontend/src/app/tasks/[id]/page.tsx` (create)
- `frontend/src/app/page.tsx` (modify - add tasks link)
- `frontend/middleware.ts` (modify - protect /tasks routes)

**Page Specs**:

**/tasks** (TaskListPage):
- Fetch and display user's tasks
- "Add Task" button → /tasks/new
- Task cards with toggle, edit, delete actions
- Delete triggers confirmation dialog
- Loading and error states

**/tasks/new** (CreateTaskPage):
- TaskForm for new task creation
- On success: redirect to /tasks
- Cancel button → /tasks

**/tasks/[id]** (TaskDetailPage):
- Fetch single task by ID
- Display full task details
- Edit mode with TaskForm
- Save and Cancel buttons
- Delete button with confirmation

**Acceptance**:
- [ ] All pages protected by auth middleware
- [ ] Navigation between pages works
- [ ] Forms show loading states
- [ ] Errors displayed to user
- [ ] Responsive layout (320px+)

### Phase 8: Integration Testing

**Goal**: End-to-end verification

**Manual Test Checklist**:

1. **Authentication Flow**
   - [ ] Unauthenticated user visiting /tasks → redirected to /login
   - [ ] After login → can access /tasks

2. **Task CRUD Flow**
   - [ ] Create task with title only → appears in list
   - [ ] Create task with title and description → both displayed
   - [ ] Toggle task complete → visual indicator, persists on reload
   - [ ] Edit task title → change saved
   - [ ] Edit task description → change saved
   - [ ] Delete task with confirmation → removed from list

3. **Multi-User Isolation**
   - [ ] Login as User A, create task
   - [ ] Logout, login as User B
   - [ ] User B cannot see User A's task
   - [ ] User B cannot access User A's task via URL

4. **Responsive Design**
   - [ ] Task list at 320px width → single column
   - [ ] Task list at 768px width → proper layout
   - [ ] Task list at 1024px width → proper layout

5. **Error Handling**
   - [ ] Create with empty title → validation error
   - [ ] API error → user-friendly message displayed

**Acceptance**:
- [ ] All manual tests pass
- [ ] No console errors in browser

## API Contract Summary

From `contracts/openapi.yaml`:

| Method | Endpoint | Success | Auth | Description |
|--------|----------|---------|------|-------------|
| GET | /api/{user_id}/tasks | 200 | JWT | List user's tasks |
| POST | /api/{user_id}/tasks | 201 | JWT | Create task |
| GET | /api/{user_id}/tasks/{id} | 200 | JWT | Get single task |
| PUT | /api/{user_id}/tasks/{id} | 200 | JWT | Update task |
| DELETE | /api/{user_id}/tasks/{id} | 204 | JWT | Delete task |
| PATCH | /api/{user_id}/tasks/{id}/complete | 200 | JWT | Toggle completion |

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| Database migration issues | Use SQLModel `create_all()` for automatic table creation |
| Token expiry during editing | Frontend handles 401 with redirect to login |
| Race condition on toggle | Backend toggle is atomic (single query) |
| Large task lists | Future: add pagination (out of scope for MVP) |

## Definition of Done

- [ ] All 30 functional requirements from spec implemented
- [ ] All 4 non-functional requirements verified
- [ ] All 11 success criteria passed
- [ ] Backend tests pass
- [ ] Manual E2E tests pass
- [ ] No security vulnerabilities (JWT required, user isolation)
- [ ] Responsive UI works on mobile and desktop
