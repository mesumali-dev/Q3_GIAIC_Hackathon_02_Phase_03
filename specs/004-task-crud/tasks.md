# Tasks: Task Management CRUD

**Input**: Design documents from `/specs/004-task-crud/`
**Prerequisites**: plan.md, spec.md, data-model.md, contracts/openapi.yaml, research.md, quickstart.md

**Tests**: Backend pytest tests included per plan.md Phase 4 requirement.

**Organization**: Tasks grouped by user story to enable independent implementation and testing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Backend**: `backend/src/`, `backend/tests/`
- **Frontend**: `frontend/src/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Ensure project structure is ready for task CRUD implementation

- [x] T001 Verify backend dependencies are installed (SQLModel, FastAPI, PyJWT) in backend/pyproject.toml
- [x] T002 Verify frontend dependencies are installed (Next.js, Tailwind CSS) in frontend/package.json
- [x] T003 [P] Verify database connection works by checking backend startup logs

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core backend infrastructure that MUST be complete before ANY user story can be implemented

**CRITICAL**: No user story work can begin until this phase is complete

- [x] T004 Create Task SQLModel entity in backend/src/models/task.py per data-model.md
- [x] T005 Export Task from backend/src/models/__init__.py
- [x] T006 Import Task in backend/src/database.py to register for table creation
- [x] T007 [P] Create TaskCreate, TaskUpdate, TaskResponse, TaskListResponse schemas in backend/src/schemas/task.py
- [x] T008 [P] Create or update backend/src/schemas/__init__.py to export task schemas
- [x] T009 Create task service with all CRUD methods in backend/src/services/task_service.py
- [x] T010 Create or update backend/src/services/__init__.py to export task service
- [x] T011 Create tasks router with all 6 endpoints in backend/src/api/tasks.py
- [x] T012 Register tasks router in backend/src/main.py (include_router)
- [x] T013 Restart backend and verify tasks table created in database
- [x] T014 Verify all 6 endpoints visible in Swagger docs at /docs

**Checkpoint**: Backend API ready - user story implementation can now begin

---

## Phase 3: User Story 1 - Create a Task (Priority: P1)

**Goal**: Authenticated user can create a new task with title and optional description

**Independent Test**: Log in, navigate to /tasks/new, submit task with title "Buy groceries", verify it appears in task list

### Backend Tests for US1

- [x] T015 [US1] Write pytest test: POST /api/{user_id}/tasks returns 201 with valid data in backend/tests/test_tasks.py
- [x] T016 [US1] Write pytest test: POST returns 422 when title is empty in backend/tests/test_tasks.py
- [x] T017 [US1] Write pytest test: POST returns 422 when title exceeds 200 chars in backend/tests/test_tasks.py
- [x] T018 [US1] Write pytest test: POST returns 401 without JWT token in backend/tests/test_tasks.py
- [x] T019 [US1] Write pytest test: POST returns 403 when user_id doesn't match JWT in backend/tests/test_tasks.py

### Frontend Implementation for US1

- [x] T020 [P] [US1] Add Task TypeScript interface in frontend/src/lib/api.ts matching TaskResponse schema
- [x] T021 [P] [US1] Implement createTask() method in frontend/src/lib/api.ts using apiRequest helper
- [x] T022 [P] [US1] Create TaskForm component in frontend/src/components/tasks/TaskForm.tsx with title and description fields
- [x] T023 [US1] Create /tasks/new page in frontend/src/app/tasks/new/page.tsx using TaskForm
- [x] T024 [US1] Add client-side validation for title (required, max 200 chars) in TaskForm
- [x] T025 [US1] Handle loading and error states in create task page
- [x] T026 [US1] Redirect to /tasks after successful task creation

**Checkpoint**: User can create tasks via frontend form - core MVP functionality complete

---

## Phase 4: User Story 2 - View Task List (Priority: P1)

**Goal**: Authenticated user can view all their tasks in a list showing title, completion status, and creation date

**Independent Test**: Log in as user with tasks, navigate to /tasks, verify all personal tasks displayed

### Backend Tests for US2

- [x] T027 [US2] Write pytest test: GET /api/{user_id}/tasks returns 200 with user's tasks in backend/tests/test_tasks.py
- [x] T028 [US2] Write pytest test: GET returns empty list for user with no tasks in backend/tests/test_tasks.py
- [x] T029 [US2] Write pytest test: GET returns 401 without JWT token in backend/tests/test_tasks.py
- [x] T030 [US2] Write pytest test: User A cannot see User B's tasks in backend/tests/test_tasks.py

### Frontend Implementation for US2

- [x] T031 [P] [US2] Implement getTasks() method in frontend/src/lib/api.ts
- [x] T032 [P] [US2] Create TaskCard component in frontend/src/components/tasks/TaskCard.tsx showing title, status, date
- [x] T033 [P] [US2] Create TaskList component in frontend/src/components/tasks/TaskList.tsx with empty state
- [x] T034 [US2] Create /tasks page in frontend/src/app/tasks/page.tsx fetching and displaying tasks
- [x] T035 [US2] Add loading state to TaskList during API fetch
- [x] T036 [US2] Add "Add Task" button linking to /tasks/new on task list page
- [x] T037 [US2] Auth protection in /tasks page (redirect to /login if unauthenticated)

**Checkpoint**: User can view their task list with proper isolation between users

---

## Phase 5: User Story 3 - Toggle Task Completion (Priority: P1)

**Goal**: User can mark a task as complete or incomplete by clicking a checkbox

**Independent Test**: Create task, verify incomplete, click checkbox, verify complete, click again, verify incomplete

### Backend Tests for US3

- [x] T038 [US3] Write pytest test: PATCH /api/{user_id}/tasks/{id}/complete toggles is_completed in backend/tests/test_tasks.py
- [x] T039 [US3] Write pytest test: Toggle returns 404 for non-existent task in backend/tests/test_tasks.py
- [x] T040 [US3] Write pytest test: User A cannot toggle User B's task (403) - covered by user isolation test

### Frontend Implementation for US3

- [x] T041 [P] [US3] Implement toggleTaskComplete() method in frontend/src/lib/api.ts
- [x] T042 [US3] Add onClick handler to TaskCard checkbox calling toggleTaskComplete
- [x] T043 [US3] Add visual distinction for completed tasks (strikethrough title) in TaskCard
- [x] T044 [US3] Show loading state when toggling in TaskCard
- [x] T045 [US3] Ensure toggle state persists across page reload (via API)

**Checkpoint**: User can toggle task completion with visual feedback - core todo functionality complete

---

## Phase 6: User Story 4 - Edit a Task (Priority: P2)

**Goal**: User can edit the title and description of an existing task they own

**Independent Test**: Navigate to existing task, modify title, save, verify updated title in list

### Backend Tests for US4

- [x] T046 [US4] Write pytest test: PUT /api/{user_id}/tasks/{id} updates task in backend/tests/test_tasks.py
- [x] T047 [US4] Write pytest test: PUT partial update only updates provided fields in backend/tests/test_tasks.py
- [x] T048 [US4] Write pytest test: PUT returns 404 for non-existent task in backend/tests/test_tasks.py
- [x] T049 [US4] Write pytest test: User A cannot update User B's task - covered by user isolation

### Frontend Implementation for US4

- [x] T050 [P] [US4] Implement updateTask() method in frontend/src/lib/api.ts
- [x] T051 [P] [US4] Implement getTask() method in frontend/src/lib/api.ts for single task fetch
- [x] T052 [US4] Create /tasks/[id]/edit page in frontend/src/app/tasks/[id]/edit/page.tsx
- [x] T053 [US4] Add edit mode to TaskForm with initialData support
- [x] T054 [US4] Add Save and Cancel buttons on edit form
- [x] T055 [US4] Redirect to /tasks after successful update

**Checkpoint**: User can edit their tasks - editing functionality complete

---

## Phase 7: User Story 5 - Delete a Task (Priority: P2)

**Goal**: User can permanently delete a task they own with confirmation

**Independent Test**: Select task, click delete, confirm, verify task removed from list

### Backend Tests for US5

- [x] T056 [US5] Write pytest test: DELETE /api/{user_id}/tasks/{id} returns 204 in backend/tests/test_tasks.py
- [x] T057 [US5] Write pytest test: DELETE returns 404 for non-existent task in backend/tests/test_tasks.py
- [x] T058 [US5] Write pytest test: User A cannot delete User B's task - covered by user isolation

### Frontend Implementation for US5

- [x] T059 [P] [US5] Implement deleteTask() method in frontend/src/lib/api.ts
- [x] T060 [P] [US5] Create delete confirmation modal in TaskCard component
- [x] T061 [US5] Add delete button to TaskCard with onClick opening confirmation modal
- [x] T062 [US5] Wire confirm dialog to call deleteTask and update list
- [ ] T063 [US5] Add delete button to task edit page (/tasks/[id]/edit)
- [x] T064 [US5] List updates after successful deletion

**Checkpoint**: User can delete tasks with confirmation - delete functionality complete

---

## Phase 8: User Story 6 - View Single Task Details (Priority: P3)

**Goal**: User can view full details of a single task on a dedicated page

**Independent Test**: Click on task in list, navigate to detail page, verify all info displayed

### Backend Tests for US6

- [x] T065 [US6] Write pytest test: GET /api/{user_id}/tasks/{id} returns single task in backend/tests/test_tasks.py
- [x] T066 [US6] Write pytest test: GET returns 404 for non-existent task in backend/tests/test_tasks.py
- [x] T067 [US6] Write pytest test: User A cannot view User B's task - 404 for isolation

### Frontend Implementation for US6

- [x] T068 [US6] Task edit page shows full task details (title, description, status via form)
- [x] T069 [US6] Add edit link from TaskCard to task edit page (/tasks/[id]/edit)
- [x] T070 [US6] Handle 404 error when task not found with user-friendly message

**Checkpoint**: User can view individual task details - detail view complete

---

## Phase 9: User Story 7 - Responsive Mobile Experience (Priority: P3)

**Goal**: Task UI works on mobile devices with touch-friendly controls

**Independent Test**: Open task list on 320px viewport, verify layout adapts, all operations work

### Frontend Implementation for US7

- [x] T071 [P] [US7] Add responsive Tailwind classes to TaskCard for mobile layout
- [x] T072 [P] [US7] Add responsive Tailwind classes to TaskList for single-column on mobile
- [x] T073 [P] [US7] Add responsive Tailwind classes to TaskForm for mobile input sizing
- [x] T074 [P] [US7] Add responsive Tailwind classes to delete confirmation modal for mobile display
- [x] T075 [US7] Add responsive classes to /tasks page for mobile navigation
- [x] T076 [US7] Add responsive classes to /tasks/new page for mobile form
- [x] T077 [US7] Add responsive classes to /tasks/[id]/edit page for mobile edit view
- [ ] T078 [US7] Test all pages at 320px, 768px, and 1024px viewports

**Checkpoint**: All task UI responsive on mobile - mobile experience complete

---

## Phase 10: Polish & Cross-Cutting Concerns

**Purpose**: Integration, home page updates, and final validation

- [x] T079 Update frontend/src/app/page.tsx to add "View Tasks" link for authenticated users
- [x] T080 Run all backend tests: `cd backend && uv run pytest tests/test_tasks.py -v` (21 passed)
- [x] T081 Verify all 6 API endpoints work via route listing
- [ ] T082 Run E2E manual test: Create → View → Toggle → Edit → Delete flow
- [ ] T083 Run security test: User A cannot access User B's tasks via URL
- [ ] T084 Run responsive test: All pages at 320px, 768px, 1024px widths
- [ ] T085 Run quickstart.md validation checklist
- [ ] T086 Verify no console errors in browser during all operations

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: No dependencies - verify existing infrastructure
- **Phase 2 (Foundational)**: Depends on Phase 1 - BLOCKS all user stories
- **Phases 3-9 (User Stories)**: All depend on Phase 2 completion
  - US1, US2, US3 are P1 priority - implement first
  - US4, US5 are P2 priority - implement after P1 complete
  - US6, US7 are P3 priority - implement after P2 complete
- **Phase 10 (Polish)**: Depends on all user stories being complete

### User Story Dependencies

| Story | Priority | Depends On | Notes |
|-------|----------|------------|-------|
| US1 (Create) | P1 | Phase 2 | Can start immediately after foundation |
| US2 (List) | P1 | Phase 2 | Can run parallel with US1 |
| US3 (Toggle) | P1 | US2 (needs list to toggle) | Depends on task display |
| US4 (Edit) | P2 | US1, US2 | Needs tasks to exist |
| US5 (Delete) | P2 | US1, US2 | Needs tasks to exist |
| US6 (Details) | P3 | US2 (needs task display) | Extends task display |
| US7 (Mobile) | P3 | US2-US6 | Responsive styling on existing pages |

### Within Each User Story

1. Backend tests → verify they fail (no implementation yet)
2. Backend already implemented in Phase 2
3. Frontend API methods (parallel)
4. Frontend components (parallel where different files)
5. Frontend pages
6. Integration testing

### Parallel Opportunities

**Phase 2 (parallel):**
```
T007, T008 - Schemas can be created in parallel
```

**US1 (parallel):**
```
T020, T021, T022 - API types, method, and component
```

**US2 (parallel):**
```
T031, T032, T033 - API method and components
```

**US3 (parallel):**
```
T041 - API method while working on UI
```

**US4 (parallel):**
```
T050, T051 - API methods
```

**US5 (parallel):**
```
T059, T060 - API method and dialog component
```

**US7 (parallel):**
```
T071, T072, T073, T074 - All component styling can run in parallel
```

---

## Implementation Strategy

### MVP First (P1 Stories Only)

1. Complete Phase 1: Setup (verification)
2. Complete Phase 2: Foundational (backend API)
3. Complete Phase 3: US1 - Create Task
4. Complete Phase 4: US2 - View Task List
5. Complete Phase 5: US3 - Toggle Completion
6. **STOP and VALIDATE**: Test P1 stories independently
7. Deploy/demo if ready

### Incremental Delivery

1. **MVP (P1)**: Create + List + Toggle = working todo app
2. **Enhancement (P2)**: + Edit + Delete = full CRUD
3. **Polish (P3)**: + Details + Mobile = polished experience

### Parallel Team Strategy

With 2+ developers after Phase 2:
- Developer A: US1 (Create) → US4 (Edit)
- Developer B: US2 (List) → US3 (Toggle) → US5 (Delete)
- Then converge for US6, US7, Polish

---

## Summary

| Phase | Story | Tasks | Priority |
|-------|-------|-------|----------|
| 1 | Setup | 3 | - |
| 2 | Foundational | 11 | - |
| 3 | US1: Create | 12 | P1 |
| 4 | US2: List | 11 | P1 |
| 5 | US3: Toggle | 8 | P1 |
| 6 | US4: Edit | 10 | P2 |
| 7 | US5: Delete | 9 | P2 |
| 8 | US6: Details | 6 | P3 |
| 9 | US7: Mobile | 8 | P3 |
| 10 | Polish | 8 | - |
| **Total** | | **86** | |

**MVP Scope (P1 only)**: Phases 1-5 = 45 tasks
**Full Feature**: All phases = 86 tasks

---

## Notes

- [P] tasks = different files, no dependencies within phase
- [Story] label maps task to specific user story
- Each user story independently completable and testable
- Backend API fully implemented in Phase 2; user stories add tests + frontend
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
