# Tasks: MCP Stateless Tool Layer

**Input**: Design documents from `/specs/007-mcp-stateless-tools/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: Not explicitly requested in specification - implementation tasks only

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

This is a web application with backend in Python:
- Backend: `backend/src/`
- Tests: `backend/tests/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and MCP module structure

- [x] T001 Install Official MCP SDK Python package via `uv add mcp` in backend/
- [x] T002 [P] Create MCP module directory structure at backend/src/mcp/
- [x] T003 [P] Create MCP tools subdirectory at backend/src/mcp/tools/
- [x] T004 [P] Create MCP test directory at backend/tests/mcp/
- [x] T005 [P] Create __init__.py files for backend/src/mcp/ and backend/src/mcp/tools/

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core MCP infrastructure that MUST be complete before ANY user story implementation

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T006 Create Pydantic schemas module at backend/src/mcp/schemas.py with base schema classes (AddTaskInput, ListTasksInput, CompleteTaskInput, DeleteTaskInput, UpdateTaskInput, TaskOutput, ListTasksOutput, DeleteTaskOutput)
- [x] T007 Create MCP error handling module at backend/src/mcp/errors.py with MCPToolError base class and specific error types (TaskNotFoundError, ValidationError, AuthorizationError, DatabaseError)
- [x] T008 Create error response handler function in backend/src/mcp/errors.py to convert exceptions to structured error responses
- [x] T009 Create MCP server initialization file at backend/src/mcp/server.py with Server instance and configuration from environment variables
- [x] T010 Add database session context manager integration in backend/src/mcp/server.py using existing get_db_session from backend/src/database.py

**Checkpoint**: Foundation ready - user story tool implementation can now begin in parallel

---

## Phase 3: User Story 1 - AI Agent Task Creation (Priority: P1) 🎯 MVP

**Goal**: Enable AI agents to create tasks through MCP tool and persist to database

**Independent Test**: Invoke `add_task` MCP tool with valid task data (title, description, user_id) and verify (1) task persisted in database, (2) task ID returned, (3) operation is stateless and repeatable

### Implementation for User Story 1

- [x] T011 [US1] Implement AddTaskInput Pydantic schema in backend/src/mcp/schemas.py with user_id (UUID), title (str, 1-200 chars), description (optional str, max 1000 chars)
- [x] T012 [US1] Implement TaskOutput Pydantic schema in backend/src/mcp/schemas.py with task_id, user_id, title, description, is_completed, created_at, updated_at fields and from_task() class method
- [x] T013 [US1] Create add_task tool implementation in backend/src/mcp/tools/add_task.py with @server.tool() decorator
- [x] T014 [US1] Implement add_task tool logic: validate input using AddTaskInput schema
- [x] T015 [US1] Implement add_task tool logic: create database session using get_db_session context manager
- [x] T016 [US1] Implement add_task tool logic: delegate to existing create_task service function from backend/src/services/task_service.py
- [x] T017 [US1] Implement add_task tool logic: convert Task model to TaskOutput schema and return as dict
- [x] T018 [US1] Implement add_task tool error handling: catch exceptions and return structured error responses using handle_tool_error
- [x] T019 [US1] Add add_task tool registration in backend/src/mcp/server.py main() function
- [x] T020 [US1] Create test file backend/tests/mcp/test_add_task.py with test fixtures for database and user
- [x] T021 [US1] Add test_add_task_success test case: verify successful task creation with valid inputs
- [x] T022 [US1] Add test_add_task_minimal test case: verify task creation with only required fields (title, user_id)
- [x] T023 [US1] Add test_add_task_validation_error test case: verify error response for missing title
- [x] T024 [US1] Add test_add_task_empty_title_error test case: verify error response for empty string title
- [x] T025 [US1] Add test_add_task_title_too_long_error test case: verify error response for title exceeding 200 characters
- [x] T026 [US1] Add test_add_task_invalid_uuid_error test case: verify error response for invalid user_id format
- [x] T027 [US1] Add logging for add_task tool invocations in backend/src/mcp/tools/add_task.py with structlog (tool name, user_id, success/error)

**Checkpoint**: At this point, User Story 1 (add_task tool) should be fully functional and testable independently

---

## Phase 4: User Story 2 - AI Agent Task Retrieval (Priority: P2)

**Goal**: Enable AI agents to retrieve all tasks for a specific user through MCP tool

**Independent Test**: Create several tasks for a user, invoke `list_tasks` with user_id, verify (1) all user's tasks returned, (2) other users' tasks excluded, (3) operation is stateless

### Implementation for User Story 2

- [x] T028 [US2] Implement ListTasksInput Pydantic schema in backend/src/mcp/schemas.py with user_id (UUID) field
- [x] T029 [US2] Implement ListTasksOutput Pydantic schema in backend/src/mcp/schemas.py with success, tasks (list of task dicts), count fields
- [x] T030 [US2] Create list_tasks tool implementation in backend/src/mcp/tools/list_tasks.py with @server.tool() decorator
- [x] T031 [US2] Implement list_tasks tool logic: validate input using ListTasksInput schema
- [x] T032 [US2] Implement list_tasks tool logic: create database session using get_db_session context manager
- [x] T033 [US2] Implement list_tasks tool logic: delegate to existing get_tasks service function from backend/src/services/task_service.py
- [x] T034 [US2] Implement list_tasks tool logic: convert list of Task models to ListTasksOutput schema with task count
- [x] T035 [US2] Implement list_tasks tool error handling: catch exceptions and return structured error responses
- [x] T036 [US2] Add list_tasks tool registration in backend/src/mcp/server.py main() function
- [x] T037 [US2] Create test file backend/tests/mcp/test_list_tasks.py with test fixtures
- [x] T038 [US2] Add test_list_tasks_success test case: verify retrieval of multiple tasks for a user
- [x] T039 [US2] Add test_list_tasks_empty test case: verify empty list returned for user with no tasks
- [x] T040 [US2] Add test_list_tasks_user_isolation test case: verify only requesting user's tasks returned, not other users' tasks
- [x] T041 [US2] Add test_list_tasks_invalid_uuid_error test case: verify error response for invalid user_id format
- [x] T042 [US2] Add logging for list_tasks tool invocations in backend/src/mcp/tools/list_tasks.py with structlog

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase 5: User Story 3 - AI Agent Task Completion (Priority: P3)

**Goal**: Enable AI agents to mark tasks as complete through MCP tool

**Independent Test**: Create a task, invoke `complete_task` with task_id and user_id, verify (1) task status updated in database, (2) completion timestamp recorded, (3) subsequent retrievals show completed status

### Implementation for User Story 3

- [x] T043 [US3] Implement CompleteTaskInput Pydantic schema in backend/src/mcp/schemas.py with user_id (UUID) and task_id (UUID) fields
- [x] T044 [US3] Create complete_task tool implementation in backend/src/mcp/tools/complete_task.py with @server.tool() decorator
- [x] T045 [US3] Implement complete_task tool logic: validate input using CompleteTaskInput schema
- [x] T046 [US3] Implement complete_task tool logic: create database session using get_db_session context manager
- [x] T047 [US3] Implement complete_task tool logic: retrieve task using get_task service function from backend/src/services/task_service.py
- [x] T048 [US3] Implement complete_task tool logic: verify task exists and belongs to user (authorization check)
- [x] T049 [US3] Implement complete_task tool logic: toggle task completion status using update_task service function
- [x] T050 [US3] Implement complete_task tool logic: return updated task as TaskOutput schema
- [x] T051 [US3] Implement complete_task tool error handling: TaskNotFoundError for missing tasks
- [x] T052 [US3] Implement complete_task tool error handling: AuthorizationError for user mismatch
- [x] T053 [US3] Add complete_task tool registration in backend/src/mcp/server.py main() function
- [x] T054 [US3] Create test file backend/tests/mcp/test_complete_task.py with test fixtures
- [x] T055 [US3] Add test_complete_task_success test case: verify task marked as complete
- [x] T056 [US3] Add test_complete_task_toggle test case: verify completion status can be toggled on/off
- [x] T057 [US3] Add test_complete_task_not_found_error test case: verify error for non-existent task_id
- [x] T058 [US3] Add test_complete_task_authorization_error test case: verify error when user attempts to complete another user's task
- [x] T059 [US3] Add test_complete_task_invalid_uuid_error test case: verify error for invalid task_id or user_id format
- [x] T060 [US3] Add logging for complete_task tool invocations in backend/src/mcp/tools/complete_task.py with structlog

**Checkpoint**: All three priority user stories should now be independently functional

---

## Phase 6: User Story 4 - AI Agent Task Deletion (Priority: P4)

**Goal**: Enable AI agents to permanently delete tasks through MCP tool

**Independent Test**: Create a task, invoke `delete_task` with task_id and user_id, verify (1) task removed from database, (2) subsequent list operations exclude deleted task, (3) accessing deleted task returns error

### Implementation for User Story 4

- [x] T061 [US4] Implement DeleteTaskInput Pydantic schema in backend/src/mcp/schemas.py with user_id (UUID) and task_id (UUID) fields
- [x] T062 [US4] Implement DeleteTaskOutput Pydantic schema in backend/src/mcp/schemas.py with success, task_id, message fields
- [x] T063 [US4] Create delete_task tool implementation in backend/src/mcp/tools/delete_task.py with @server.tool() decorator
- [x] T064 [US4] Implement delete_task tool logic: validate input using DeleteTaskInput schema
- [x] T065 [US4] Implement delete_task tool logic: create database session using get_db_session context manager
- [x] T066 [US4] Implement delete_task tool logic: retrieve task using get_task service function to verify ownership
- [x] T067 [US4] Implement delete_task tool logic: verify task exists and belongs to user (authorization check)
- [x] T068 [US4] Implement delete_task tool logic: delete task using delete_task service function from backend/src/services/task_service.py
- [x] T069 [US4] Implement delete_task tool logic: return DeleteTaskOutput with success message
- [x] T070 [US4] Implement delete_task tool error handling: TaskNotFoundError and AuthorizationError
- [x] T071 [US4] Add delete_task tool registration in backend/src/mcp/server.py main() function
- [x] T072 [US4] Create test file backend/tests/mcp/test_delete_task.py with test fixtures
- [x] T073 [US4] Add test_delete_task_success test case: verify task permanently deleted from database
- [x] T074 [US4] Add test_delete_task_not_found_error test case: verify error for non-existent task
- [x] T075 [US4] Add test_delete_task_authorization_error test case: verify error when user attempts to delete another user's task
- [x] T076 [US4] Add test_delete_task_verify_persistence test case: verify deleted task not returned by list_tasks
- [x] T077 [US4] Add logging for delete_task tool invocations in backend/src/mcp/tools/delete_task.py with structlog

**Checkpoint**: All four user stories should now be independently functional

---

## Phase 7: User Story 5 - AI Agent Task Modification (Priority: P5)

**Goal**: Enable AI agents to update task details (title, description) through MCP tool

**Independent Test**: Create a task, invoke `update_task` with modified fields, verify (1) only specified fields updated in database, (2) unchanged fields remain intact, (3) operation is atomic and stateless

### Implementation for User Story 5

- [x] T078 [US5] Implement UpdateTaskInput Pydantic schema in backend/src/mcp/schemas.py with user_id (UUID), task_id (UUID), title (optional str), description (optional str) fields
- [x] T079 [US5] Add validation to UpdateTaskInput: ensure at least one field (title or description) is provided
- [x] T080 [US5] Create update_task tool implementation in backend/src/mcp/tools/update_task.py with @server.tool() decorator
- [x] T081 [US5] Implement update_task tool logic: validate input using UpdateTaskInput schema
- [x] T082 [US5] Implement update_task tool logic: create database session using get_db_session context manager
- [x] T083 [US5] Implement update_task tool logic: retrieve task using get_task service function to verify ownership
- [x] T084 [US5] Implement update_task tool logic: verify task exists and belongs to user (authorization check)
- [x] T085 [US5] Implement update_task tool logic: update only specified fields using update_task service function from backend/src/services/task_service.py
- [x] T086 [US5] Implement update_task tool logic: return updated task as TaskOutput schema
- [x] T087 [US5] Implement update_task tool error handling: ValidationError for no fields provided, TaskNotFoundError, AuthorizationError
- [x] T088 [US5] Add update_task tool registration in backend/src/mcp/server.py main() function
- [x] T089 [US5] Create test file backend/tests/mcp/test_update_task.py with test fixtures
- [x] T090 [US5] Add test_update_task_title_only test case: verify only title updated, description unchanged
- [x] T091 [US5] Add test_update_task_description_only test case: verify only description updated, title unchanged
- [x] T092 [US5] Add test_update_task_both_fields test case: verify both title and description updated atomically
- [x] T093 [US5] Add test_update_task_clear_description test case: verify description can be cleared (set to null/empty)
- [x] T094 [US5] Add test_update_task_no_fields_error test case: verify error when no fields provided for update
- [x] T095 [US5] Add test_update_task_not_found_error test case: verify error for non-existent task
- [x] T096 [US5] Add test_update_task_authorization_error test case: verify error when user attempts to update another user's task
- [x] T097 [US5] Add test_update_task_invalid_title_error test case: verify error for empty title or title exceeding 200 characters
- [x] T098 [US5] Add logging for update_task tool invocations in backend/src/mcp/tools/update_task.py with structlog

**Checkpoint**: All five user stories should now be independently functional

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: MCP server finalization, testing, and documentation

- [X] T099 [P] Implement MCP server main() function entry point in backend/src/mcp/server.py with stdio transport using stdio_server()
- [X] T100 [P] Add server lifecycle logging in backend/src/mcp/server.py (startup, shutdown events)
- [X] T101 [P] Configure environment variables for MCP server in .env file (MCP_SERVER_NAME, MCP_SERVER_VERSION)
- [X] T102 [P] Add server.py __main__ block to enable running as python -m src.mcp.server
- [X] T103 [P] Create comprehensive test suite runner script at backend/tests/mcp/__init__.py
- [X] T104 Run all MCP tool tests using pytest backend/tests/mcp/ -v and verify 100% pass rate
- [X] T105 Verify stateless operation: restart MCP server and confirm tasks persist across restarts
- [X] T106 [P] Add MCP tool invocation examples to quickstart.md documentation
- [X] T107 [P] Update quickstart.md with testing instructions and expected performance benchmarks
- [X] T108 Validate all five tools against contract JSON schemas in specs/007-mcp-stateless-tools/contracts/
- [X] T109 Perform end-to-end validation: create task → list tasks → complete task → update task → delete task → verify persistence
- [X] T110 Verify user-scoped access: create tasks for multiple users and confirm no cross-user data leakage

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-7)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3 → P4 → P5)
- **Polish (Phase 8)**: Depends on all five user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - Independent, but may reuse US1 tests for setup
- **User Story 3 (P3)**: Can start after Foundational (Phase 2) - May use US1 (add_task) for test setup
- **User Story 4 (P4)**: Can start after Foundational (Phase 2) - May use US1 (add_task) for test setup
- **User Story 5 (P5)**: Can start after Foundational (Phase 2) - May use US1 (add_task) for test setup

### Within Each User Story

- Pydantic schemas before tool implementations
- Tool logic implementation before error handling
- Tool registration before testing
- Test setup before test cases
- Core functionality tests before edge case tests

### Parallel Opportunities

- Phase 1 (Setup): Tasks T002, T003, T004, T005 can run in parallel (creating different directories)
- Phase 2 (Foundational): Once T006-T008 complete, T009-T010 can run in parallel
- Phase 3-7: All user stories can be implemented in parallel by different developers after Phase 2 completes
- Within each user story: Test cases (multiple test_ functions) can be written in parallel
- Phase 8 (Polish): Tasks T099-T103, T106-T107 can run in parallel

---

## Parallel Example: User Story 1 Implementation

```bash
# After foundational schemas (T006-T010) are complete:

# Step 1: Schemas can be implemented together
Task T011: "Implement AddTaskInput schema"
Task T012: "Implement TaskOutput schema"

# Step 2: Tool implementation (sequential within story)
Task T013: "Create add_task tool file"
Task T014-T018: "Implement tool logic and error handling"

# Step 3: All test cases can be written/run in parallel
Task T021: "test_add_task_success"
Task T022: "test_add_task_minimal"
Task T023: "test_add_task_validation_error"
Task T024: "test_add_task_empty_title_error"
Task T025: "test_add_task_title_too_long_error"
Task T026: "test_add_task_invalid_uuid_error"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T005)
2. Complete Phase 2: Foundational (T006-T010) ⚠️ CRITICAL
3. Complete Phase 3: User Story 1 - add_task tool (T011-T027)
4. **STOP and VALIDATE**: Test add_task independently, verify database persistence
5. Ready for Phase 3 AI agent integration

### Incremental Delivery

1. Complete Setup + Foundational → MCP infrastructure ready
2. Add User Story 1 (add_task) → Test independently → Minimum viable MCP server
3. Add User Story 2 (list_tasks) → Test independently → Task creation + retrieval working
4. Add User Story 3 (complete_task) → Test independently → Core task lifecycle complete
5. Add User Story 4 (delete_task) → Test independently → Full CRUD operations available
6. Add User Story 5 (update_task) → Test independently → Complete task management
7. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together (T001-T010)
2. Once Foundational is done:
   - Developer A: User Story 1 (add_task) - T011-T027
   - Developer B: User Story 2 (list_tasks) - T028-T042
   - Developer C: User Story 3 (complete_task) - T043-T060
   - Developer D: User Story 4 (delete_task) - T061-T077
   - Developer E: User Story 5 (update_task) - T078-T098
3. Stories complete and integrate independently
4. Team converges for Phase 8 (Polish) together

---

## Task Summary

**Total Tasks**: 110
**Tasks per Phase**:
- Phase 1 (Setup): 5 tasks
- Phase 2 (Foundational): 5 tasks (BLOCKING)
- Phase 3 (US1 - add_task): 17 tasks
- Phase 4 (US2 - list_tasks): 15 tasks
- Phase 5 (US3 - complete_task): 18 tasks
- Phase 6 (US4 - delete_task): 17 tasks
- Phase 7 (US5 - update_task): 21 tasks
- Phase 8 (Polish): 12 tasks

**Parallel Opportunities**: 25+ tasks can run in parallel across phases

**MVP Scope (Recommended)**: Phases 1-3 only (27 tasks) delivers add_task tool - minimum viable capability for Phase 3 AI agent integration

**Independent Test Criteria**:
- US1: Create task via add_task, verify in database
- US2: List tasks via list_tasks, verify user isolation
- US3: Complete task via complete_task, verify status change
- US4: Delete task via delete_task, verify removal
- US5: Update task via update_task, verify partial updates

---

## Notes

- All tasks follow strict checklist format: `- [ ] [TaskID] [P?] [Story?] Description with file path`
- [P] indicates parallelizable tasks (different files, no sequential dependencies)
- [Story] labels (US1-US5) map to user stories from spec.md for traceability
- Each user story is independently testable and deliverable
- Foundation (Phase 2) must complete before any tool implementation begins
- Stop at any checkpoint to validate independent story functionality
- All tools are stateless - no in-memory state between invocations
- All tools persist directly to Neon PostgreSQL via existing service layer
- All tools enforce user-scoped access for data isolation
