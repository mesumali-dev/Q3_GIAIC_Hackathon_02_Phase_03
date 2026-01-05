# Feature Specification: Task Management CRUD

**Feature Branch**: `004-task-crud`
**Created**: 2026-01-01
**Status**: Draft
**Input**: User description: "Implement the complete task management functionality (Create, Read, Update, Delete, Toggle Completion) as a secure, multi-user web application using FastAPI, SQLModel, Neon PostgreSQL, and a responsive Next.js frontend."

## Context

This feature builds upon the authentication system established in 003-backend-auth-refactor. The goal is to provide complete task management capabilities where each authenticated user can manage their own personal tasks. Tasks are private to each user - no user can see or modify another user's tasks.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Create a Task (Priority: P1)

An authenticated user can create a new task by providing a title and optional description. The task is automatically associated with their account and starts in an incomplete state.

**Why this priority**: Creating tasks is the foundational capability - without this, no other task operations are possible.

**Independent Test**: Log in as a user, navigate to task creation, submit a task with title "Buy groceries", verify task appears in the task list.

**Acceptance Scenarios**:

1. **Given** an authenticated user on the create task page, **When** they submit a valid title (1-200 chars), **Then** the system creates the task and displays it in the user's task list.
2. **Given** an authenticated user, **When** they submit a task with title and description, **Then** both fields are saved and displayed correctly.
3. **Given** an authenticated user, **When** they submit a task with empty title, **Then** the system displays a validation error "Title is required".
4. **Given** an authenticated user, **When** they submit a task with title exceeding 200 characters, **Then** the system displays a validation error "Title must be 200 characters or less".
5. **Given** an unauthenticated user, **When** they attempt to create a task, **Then** they are redirected to the login page.

---

### User Story 2 - View Task List (Priority: P1)

An authenticated user can view all their tasks in a list format, showing title, completion status, and creation date.

**Why this priority**: Viewing tasks is essential to know what tasks exist - tied with creation as core MVP.

**Independent Test**: Log in as a user with existing tasks, navigate to task list, verify all personal tasks are displayed with correct information.

**Acceptance Scenarios**:

1. **Given** an authenticated user with tasks, **When** they visit the tasks page, **Then** they see all their tasks listed.
2. **Given** an authenticated user with no tasks, **When** they visit the tasks page, **Then** they see an empty state message encouraging them to create their first task.
3. **Given** two different users with tasks, **When** User A views their task list, **Then** they only see their own tasks (not User B's tasks).
4. **Given** an authenticated user, **When** viewing the task list, **Then** each task shows title, completion status (checkbox), and creation date.

---

### User Story 3 - Toggle Task Completion (Priority: P1)

An authenticated user can mark a task as complete or incomplete by clicking a checkbox or toggle button in the UI.

**Why this priority**: Tracking completion is the core value proposition of a todo app.

**Independent Test**: Create a task, verify it shows as incomplete, click the checkbox, verify it shows as complete, click again, verify it shows as incomplete.

**Acceptance Scenarios**:

1. **Given** an incomplete task, **When** the user clicks the completion toggle, **Then** the task is marked as complete with visual indication (strikethrough or checkmark).
2. **Given** a complete task, **When** the user clicks the completion toggle, **Then** the task is marked as incomplete.
3. **Given** a task, **When** toggling completion, **Then** the change persists across page reloads.
4. **Given** User A's task, **When** User B tries to toggle it via API, **Then** the system returns 403 Forbidden.

---

### User Story 4 - Edit a Task (Priority: P2)

An authenticated user can edit the title and description of an existing task they own.

**Why this priority**: Editing allows correcting mistakes - important but not critical for basic task tracking.

**Independent Test**: Navigate to an existing task's edit page, modify the title, save, verify the updated title appears in the task list.

**Acceptance Scenarios**:

1. **Given** an authenticated user viewing their task, **When** they navigate to edit and update the title, **Then** the task is updated with the new title.
2. **Given** an authenticated user, **When** they update the description, **Then** the new description is saved and displayed.
3. **Given** an authenticated user, **When** they try to save with an empty title, **Then** validation error is displayed.
4. **Given** User A, **When** they try to edit User B's task via URL manipulation, **Then** they receive a 404 Not Found or 403 Forbidden response.

---

### User Story 5 - Delete a Task (Priority: P2)

An authenticated user can permanently delete a task they own.

**Why this priority**: Deletion allows cleanup - important for organization but not critical for MVP.

**Independent Test**: Select a task, click delete, confirm deletion, verify task no longer appears in the task list.

**Acceptance Scenarios**:

1. **Given** an authenticated user viewing a task they own, **When** they click delete and confirm, **Then** the task is permanently removed.
2. **Given** a delete action, **When** initiated, **Then** a confirmation dialog appears before final deletion.
3. **Given** User A, **When** they try to delete User B's task, **Then** the system returns 403 Forbidden.
4. **Given** a deleted task, **When** the user refreshes the page, **Then** the task does not reappear.

---

### User Story 6 - View Single Task Details (Priority: P3)

An authenticated user can view the full details of a single task on a dedicated page.

**Why this priority**: Useful for long descriptions but not essential for basic task management.

**Independent Test**: Click on a task in the list, navigate to task detail page, verify all task information is displayed.

**Acceptance Scenarios**:

1. **Given** an authenticated user, **When** they click on a task in the list, **Then** they see the task detail page with full title, description, completion status, and timestamps.
2. **Given** User A, **When** they try to view User B's task via URL, **Then** they receive a 404 Not Found response.

---

### User Story 7 - Responsive Mobile Experience (Priority: P3)

The task management UI works seamlessly on mobile devices with touch-friendly controls.

**Why this priority**: Mobile support enhances accessibility but desktop-first is acceptable for MVP.

**Independent Test**: Open the task list on a mobile viewport, verify layout adapts, buttons are tappable, and all CRUD operations work.

**Acceptance Scenarios**:

1. **Given** a user on a mobile device (viewport < 768px), **When** viewing the task list, **Then** the layout adapts to single-column format with appropriately sized touch targets.
2. **Given** a user on a mobile device, **When** performing any task operation, **Then** the operation completes successfully.

---

### Edge Cases

- What happens when a user creates a task with exactly 200 characters? → Task is created successfully (200 is valid).
- What happens when a user creates a task with 201 characters? → Validation error displayed.
- What happens when a user creates a task with exactly 1000 character description? → Task is created successfully.
- What happens when a user creates a task with 1001 character description? → Validation error displayed.
- What happens when a user tries to access /tasks/[id] for a non-existent task? → 404 Not Found page.
- What happens when the database connection fails during task creation? → 500 error, user sees friendly error message.
- What happens when a user's token expires while on the task page? → Next API call returns 401, user is redirected to login.
- What happens when two users create tasks simultaneously? → Both tasks are created with unique IDs (no collision).

## Requirements *(mandatory)*

### Functional Requirements

#### Backend Task API

- **FR-001**: Backend MUST provide GET /api/{user_id}/tasks endpoint returning all tasks for the authenticated user.
- **FR-002**: Backend MUST provide POST /api/{user_id}/tasks endpoint creating a new task for the authenticated user.
- **FR-003**: Backend MUST provide GET /api/{user_id}/tasks/{id} endpoint returning a single task if owned by authenticated user.
- **FR-004**: Backend MUST provide PUT /api/{user_id}/tasks/{id} endpoint updating task title and/or description.
- **FR-005**: Backend MUST provide DELETE /api/{user_id}/tasks/{id} endpoint permanently removing the task.
- **FR-006**: Backend MUST provide PATCH /api/{user_id}/tasks/{id}/complete endpoint toggling completion status.

#### Backend Authorization

- **FR-007**: Backend MUST validate JWT token on all task endpoints.
- **FR-008**: Backend MUST verify that user_id in route matches the authenticated user from JWT.
- **FR-009**: Backend MUST filter all task queries by authenticated user's ID.
- **FR-010**: Backend MUST return 403 Forbidden when user attempts to access another user's task.
- **FR-011**: Backend MUST return 404 Not Found when task does not exist.
- **FR-012**: Backend MUST return 401 Unauthorized when no valid token is provided.

#### Backend Validation

- **FR-013**: Backend MUST validate task title is between 1 and 200 characters.
- **FR-014**: Backend MUST validate task description is 1000 characters or less (optional field).
- **FR-015**: Backend MUST return 400 Bad Request with clear error messages for validation failures.
- **FR-016**: Backend MUST return proper HTTP status codes (200, 201, 400, 401, 403, 404, 500).

#### Backend Storage

- **FR-017**: Backend MUST store tasks using SQLModel ORM with Neon PostgreSQL.
- **FR-018**: Task model MUST include: id (UUID), user_id (UUID foreign key), title (string 1-200), description (string 0-1000 nullable), is_completed (boolean default false), created_at, updated_at.
- **FR-019**: Backend MUST create database index on user_id column for query performance.
- **FR-020**: Backend MUST create database index on is_completed column for potential filtering.

#### Frontend Task UI

- **FR-021**: Frontend MUST provide /tasks page showing authenticated user's task list.
- **FR-022**: Frontend MUST provide /tasks/new page with form to create new task.
- **FR-023**: Frontend MUST provide /tasks/[id] page showing task details with edit capability.
- **FR-024**: Frontend MUST display loading states during API operations.
- **FR-025**: Frontend MUST display error messages from API responses.
- **FR-026**: Frontend MUST provide visual distinction between complete and incomplete tasks.
- **FR-027**: Frontend MUST provide confirmation dialog before task deletion.
- **FR-028**: Frontend MUST redirect unauthenticated users to /login.
- **FR-029**: Frontend MUST use responsive Tailwind CSS styling.
- **FR-030**: Frontend MUST provide immediate visual feedback when toggling task completion.

### Key Entities

- **Task**: Represents a user's todo item. Attributes: id (UUID primary key), user_id (UUID foreign key to User), title (required, 1-200 chars), description (optional, max 1000 chars), is_completed (boolean), created_at, updated_at. Belongs to exactly one User.
- **User**: (Existing from 003-backend-auth-refactor) Has many Tasks.

## Non-Functional Requirements

- **NFR-001**: Task list page MUST load within 2 seconds for up to 100 tasks.
- **NFR-002**: Individual task operations (create, update, delete, toggle) MUST complete within 1 second.
- **NFR-003**: UI MUST be usable on screens as small as 320px width.
- **NFR-004**: All user-facing error messages MUST be human-readable (no raw error codes).

## Assumptions

- Authentication is fully implemented per 003-backend-auth-refactor (JWT-based, FastAPI backend).
- User model exists with id (UUID), email, and hashed_password fields.
- Neon PostgreSQL database is configured and accessible.
- Frontend has existing auth context/hooks for accessing current user and JWT token.
- Soft delete is NOT required - tasks are permanently deleted.
- Task ordering is by creation date (newest first) - no drag-and-drop reordering required.
- No due dates, priorities, or categories for tasks in this feature (can be added in future iterations).
- No bulk operations (bulk delete, bulk complete) - single task operations only.

## Out of Scope

- Task sharing between users
- Task categories, tags, or labels
- Due dates and reminders
- Task priorities
- Drag-and-drop reordering
- Bulk operations
- Search and filter functionality
- Task attachments
- Subtasks or task hierarchies
- Recurring tasks

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Authenticated users can create tasks and see them immediately in their task list.
- **SC-002**: Users can complete all CRUD operations (Create, Read, Update, Delete) on their tasks.
- **SC-003**: Users cannot view, modify, or delete tasks belonging to other users.
- **SC-004**: Task data persists across browser sessions and page reloads.
- **SC-005**: Task list displays correctly on both desktop (1024px+) and mobile (320px+) viewports.
- **SC-006**: 100% of task operations complete within 2 seconds under normal network conditions.
- **SC-007**: All form validation errors are displayed clearly to users before API submission where possible.

### Verification Criteria

- **SC-008**: Manual E2E test: Create task → View list → Toggle complete → Edit task → Delete task - all succeed.
- **SC-009**: Manual security test: User A cannot access User B's tasks via URL manipulation.
- **SC-010**: Responsive test: All task UI pages render correctly at 320px, 768px, and 1024px widths.
- **SC-011**: Persistence test: Create task, close browser, reopen, task still exists.
