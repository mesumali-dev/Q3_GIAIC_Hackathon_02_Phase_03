# Tasks: AI Agent & MCP Tool Orchestration

**Input**: Design documents from `/specs/008-ai-agent-mcp-orchestration/`
**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, quickstart.md

**Tests**: Tests are included as they support the validation requirements in the spec (SC-001 through SC-010).

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Web app backend**: `backend/src/agent/`, `backend/tests/agent/`
- Uses existing MCP tools from `backend/src/mcp/tools/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and agent module structure

- [X] T001 Add openai-agents dependency to backend/pyproject.toml
- [X] T002 Run `uv sync` to install OpenAI Agents SDK
- [X] T003 [P] Create agent module directory structure at backend/src/agent/
- [X] T004 [P] Create agent module __init__.py at backend/src/agent/__init__.py
- [X] T005 [P] Create test directory at backend/tests/agent/__init__.py
- [X] T006 Add OPENAI_API_KEY and OPENAI_DEFAULT_MODEL to backend/.env.example

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**CRITICAL**: No user story work can begin until this phase is complete

- [X] T007 Create UserContext dataclass in backend/src/agent/context.py
- [X] T008 Add UUID validation to UserContext in backend/src/agent/context.py
- [X] T009 [P] Create test fixtures in backend/tests/agent/conftest.py
- [X] T010 [P] Write UserContext validation tests in backend/tests/agent/test_context.py
- [X] T011 Create system prompt constants in backend/src/agent/prompts.py
- [X] T012 Define TASK_MANAGER_PROMPT with role, capabilities, and rules in backend/src/agent/prompts.py
- [X] T013 Export UserContext and prompts from backend/src/agent/__init__.py

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - Natural Language Task Creation (Priority: P1)

**Goal**: Agent interprets "Add a task called X" and invokes add_task MCP tool

**Independent Test**: Provide natural language input for task creation, verify add_task tool is invoked with correct parameters

### Tests for User Story 1

- [X] T014 [P] [US1] Write add_task_tool unit tests in backend/tests/agent/test_tools.py
- [X] T015 [P] [US1] Write task creation intent tests in backend/tests/agent/test_agent.py

### Implementation for User Story 1

- [X] T016 [US1] Implement add_task_tool function with @function_tool decorator in backend/src/agent/tools.py
- [X] T017 [US1] Add MCP add_task import to backend/src/agent/tools.py
- [X] T018 [US1] Implement title/description extraction in add_task_tool in backend/src/agent/tools.py
- [X] T019 [US1] Add success/error response formatting in add_task_tool in backend/src/agent/tools.py
- [X] T020 [US1] Create TaskManager agent definition in backend/src/agent/agent.py
- [X] T021 [US1] Register add_task_tool with agent in backend/src/agent/agent.py
- [X] T022 [US1] Create run_agent function in backend/src/agent/runner.py
- [X] T023 [US1] Export agent and runner from backend/src/agent/__init__.py
- [X] T024 [US1] Run tests and verify add_task_tool works with agent

**Checkpoint**: User Story 1 complete - agent can create tasks via natural language

---

## Phase 4: User Story 2 - Natural Language Task Listing (Priority: P2)

**Goal**: Agent interprets "Show my tasks" and invokes list_tasks MCP tool

**Independent Test**: Provide natural language query, verify list_tasks tool is invoked and results formatted

### Tests for User Story 2

- [X] T025 [P] [US2] Write list_tasks_tool unit tests in backend/tests/agent/test_tools.py
- [X] T026 [P] [US2] Write task listing intent tests in backend/tests/agent/test_agent.py

### Implementation for User Story 2

- [X] T027 [US2] Implement list_tasks_tool function in backend/src/agent/tools.py
- [X] T028 [US2] Add MCP list_tasks import to backend/src/agent/tools.py
- [X] T029 [US2] Implement task list formatting (checkbox, title, ID) in list_tasks_tool in backend/src/agent/tools.py
- [X] T030 [US2] Handle empty task list case in list_tasks_tool in backend/src/agent/tools.py
- [X] T031 [US2] Register list_tasks_tool with agent in backend/src/agent/agent.py
- [X] T032 [US2] Run tests and verify list_tasks_tool works with agent

**Checkpoint**: User Stories 1 AND 2 complete - agent can create and list tasks

---

## Phase 5: User Story 3 - Natural Language Task Completion (Priority: P3)

**Goal**: Agent interprets "Mark X as done" and invokes complete_task MCP tool

**Independent Test**: Create task, then provide completion command, verify complete_task tool invoked with correct task_id

### Tests for User Story 3

- [X] T033 [P] [US3] Write complete_task_tool unit tests in backend/tests/agent/test_tools.py
- [X] T034 [P] [US3] Write task completion intent tests in backend/tests/agent/test_agent.py

### Implementation for User Story 3

- [X] T035 [US3] Implement complete_task_tool function in backend/src/agent/tools.py
- [X] T036 [US3] Add MCP complete_task import to backend/src/agent/tools.py
- [X] T037 [US3] Implement task_id parameter handling in complete_task_tool in backend/src/agent/tools.py
- [X] T038 [US3] Add completion confirmation message formatting in backend/src/agent/tools.py
- [X] T039 [US3] Register complete_task_tool with agent in backend/src/agent/agent.py
- [X] T040 [US3] Run tests and verify complete_task_tool works with agent

**Checkpoint**: User Stories 1-3 complete - agent can create, list, and complete tasks

---

## Phase 6: User Story 4 - Natural Language Task Deletion (Priority: P4)

**Goal**: Agent interprets "Delete the X task" and invokes delete_task MCP tool

**Independent Test**: Create task, then provide deletion command, verify delete_task tool invoked

### Tests for User Story 4

- [X] T041 [P] [US4] Write delete_task_tool unit tests in backend/tests/agent/test_tools.py
- [X] T042 [P] [US4] Write task deletion intent tests in backend/tests/agent/test_agent.py

### Implementation for User Story 4

- [X] T043 [US4] Implement delete_task_tool function in backend/src/agent/tools.py
- [X] T044 [US4] Add MCP delete_task import to backend/src/agent/tools.py
- [X] T045 [US4] Implement task_id parameter handling in delete_task_tool in backend/src/agent/tools.py
- [X] T046 [US4] Add deletion confirmation message formatting in backend/src/agent/tools.py
- [X] T047 [US4] Register delete_task_tool with agent in backend/src/agent/agent.py
- [X] T048 [US4] Run tests and verify delete_task_tool works with agent

**Checkpoint**: User Stories 1-4 complete - agent can create, list, complete, and delete tasks

---

## Phase 7: User Story 5 - Natural Language Task Update (Priority: P5)

**Goal**: Agent interprets "Change X title to Y" and invokes update_task MCP tool

**Independent Test**: Create task, then provide update command, verify update_task tool invoked with correct fields

### Tests for User Story 5

- [X] T049 [P] [US5] Write update_task_tool unit tests in backend/tests/agent/test_tools.py
- [X] T050 [P] [US5] Write task update intent tests in backend/tests/agent/test_agent.py

### Implementation for User Story 5

- [X] T051 [US5] Implement update_task_tool function in backend/src/agent/tools.py
- [X] T052 [US5] Add MCP update_task import to backend/src/agent/tools.py
- [X] T053 [US5] Implement optional title/description parameter handling in backend/src/agent/tools.py
- [X] T054 [US5] Add update confirmation message formatting in backend/src/agent/tools.py
- [X] T055 [US5] Register update_task_tool with agent in backend/src/agent/agent.py
- [X] T056 [US5] Run tests and verify update_task_tool works with agent

**Checkpoint**: User Stories 1-5 complete - agent can perform all CRUD operations

---

## Phase 8: User Story 6 - Error Handling and Graceful Responses (Priority: P6)

**Goal**: Agent communicates MCP tool errors clearly without exposing internal details

**Independent Test**: Trigger various error conditions, verify agent returns user-friendly error messages

### Tests for User Story 6

- [X] T057 [P] [US6] Write error handling tests for validation errors in backend/tests/agent/test_tools.py
- [X] T058 [P] [US6] Write error handling tests for not found errors in backend/tests/agent/test_tools.py
- [X] T059 [P] [US6] Write error handling tests for database errors in backend/tests/agent/test_tools.py

### Implementation for User Story 6

- [X] T060 [US6] Add error response translation helper in backend/src/agent/tools.py
- [X] T061 [US6] Update all tools to use error translation helper in backend/src/agent/tools.py
- [X] T062 [US6] Add validation error handling (VALIDATION_ERROR) in all tools in backend/src/agent/tools.py
- [X] T063 [US6] Add not found error handling (TASK_NOT_FOUND) in complete/delete/update tools in backend/src/agent/tools.py
- [X] T064 [US6] Add generic database error handling in all tools in backend/src/agent/tools.py
- [X] T065 [US6] Update system prompt to include error handling instructions in backend/src/agent/prompts.py
- [X] T066 [US6] Run tests and verify error handling works correctly

**Checkpoint**: User Stories 1-6 complete - agent handles all CRUD operations and errors gracefully

---

## Phase 9: User Story 7 - Natural Language Reminder Scheduling (Priority: P7)

**Goal**: Agent interprets "Remind me about X tomorrow at 9am" and invokes schedule_reminder MCP tool

**Independent Test**: Create task, then provide reminder command, verify schedule_reminder tool invoked with correct parameters

### Tests for User Story 7

- [X] T067 [P] [US7] Write schedule_reminder_tool unit tests in backend/tests/agent/test_tools.py
- [X] T068 [P] [US7] Write reminder scheduling intent tests in backend/tests/agent/test_agent.py

### Implementation for User Story 7

- [X] T069 [US7] Implement schedule_reminder_tool function with @function_tool decorator in backend/src/agent/tools.py
- [X] T070 [US7] Add MCP schedule_reminder import to backend/src/agent/tools.py
- [X] T071 [US7] Implement task_id and remind_at parameter handling in schedule_reminder_tool in backend/src/agent/tools.py
- [X] T072 [US7] Implement optional repeat_interval_minutes and repeat_count parameters in backend/src/agent/tools.py
- [X] T073 [US7] Add reminder confirmation message formatting in backend/src/agent/tools.py
- [X] T074 [US7] Register schedule_reminder_tool with agent in backend/src/agent/agent.py
- [X] T075 [US7] Update system prompt to include reminder scheduling rules in backend/src/agent/prompts.py
- [X] T076 [US7] Run tests and verify schedule_reminder_tool works with agent

**Checkpoint**: All user stories complete - agent handles all CRUD operations, reminders, and errors gracefully

---

## Phase 10: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [X] T077 [P] Add comprehensive docstrings to all functions in backend/src/agent/tools.py
- [X] T078 [P] Add comprehensive docstrings to agent definition in backend/src/agent/agent.py
- [X] T079 [P] Add comprehensive docstrings to runner in backend/src/agent/runner.py
- [X] T080 Write integration tests with real MCP tools in backend/tests/agent/test_integration.py
- [X] T081 [P] Add structlog logging to all tool invocations in backend/src/agent/tools.py
- [X] T082 [P] Create example usage script in backend/examples/agent_demo.py
- [X] T083 Update quickstart.md with actual code examples from implementation
- [X] T084 Run full test suite and verify all tests pass
- [X] T085 Verify agent never accesses database directly (code review)
- [X] T086 Verify all tools pass user_id from context to MCP tools

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-9)**: All depend on Foundational phase completion
  - User stories can proceed sequentially in priority order (P1 → P2 → P3 → P4 → P5 → P6 → P7)
  - Later stories build on tools from earlier stories
- **Polish (Phase 10)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational - Creates agent and runner infrastructure
- **User Story 2 (P2)**: Can start after US1 - Adds list_tasks_tool to existing agent
- **User Story 3 (P3)**: Can start after US2 - Adds complete_task_tool (may need list_tasks for task lookup)
- **User Story 4 (P4)**: Can start after US3 - Adds delete_task_tool
- **User Story 5 (P5)**: Can start after US4 - Adds update_task_tool
- **User Story 6 (P6)**: Can start after US5 - Adds error handling across all tools
- **User Story 7 (P7)**: Can start after US6 - Adds schedule_reminder_tool (uses existing reminder MCP tool)

### Within Each User Story

- Tests written FIRST (if included)
- Tool implementation before agent registration
- Agent registration before testing with agent
- All tests pass before moving to next story

### Parallel Opportunities

- Setup tasks T003, T004, T005 can run in parallel
- Foundational T009, T010 can run in parallel
- Test tasks within each story marked [P] can run in parallel
- Polish tasks T077, T078, T079, T081, T082 can run in parallel

---

## Parallel Example: User Story 1

```bash
# Launch tests for User Story 1 together:
Task: "Write add_task_tool unit tests in backend/tests/agent/test_tools.py"
Task: "Write task creation intent tests in backend/tests/agent/test_agent.py"

# After tests, implement sequentially:
Task: "Implement add_task_tool function in backend/src/agent/tools.py"
Task: "Create TaskManager agent definition in backend/src/agent/agent.py"
Task: "Create run_agent function in backend/src/agent/runner.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1 (add_task)
4. **STOP and VALIDATE**: Test agent can create tasks via natural language
5. This alone validates: SDK integration, tool invocation, context passing

### Incremental Delivery

1. Setup + Foundational → Foundation ready
2. Add User Story 1 (add_task) → Test independently (MVP!)
3. Add User Story 2 (list_tasks) → Test independently
4. Add User Story 3 (complete_task) → Test independently
5. Add User Story 4 (delete_task) → Test independently
6. Add User Story 5 (update_task) → Test independently
7. Add User Story 6 (error handling) → Test error scenarios
8. Add User Story 7 (schedule_reminder) → Test reminder scheduling
9. Each story adds value without breaking previous stories

### Success Criteria Mapping

| Task Range | Success Criteria Addressed |
|------------|---------------------------|
| T014-T024 | SC-001 (intent), SC-002 (tool selection), SC-008 (user_id) |
| T025-T032 | SC-001, SC-002, SC-003 (confirmation) |
| T033-T040 | SC-001, SC-002, SC-003 |
| T041-T048 | SC-001, SC-002, SC-003 |
| T049-T056 | SC-001, SC-002, SC-003 |
| T057-T066 | SC-004 (error handling), SC-005 (clarification) |
| T067-T076 | SC-001, SC-002, SC-003 (reminder scheduling) |
| T080-T086 | SC-006 (response time), SC-009 (no DB), SC-010 (Phase 4 ready) |

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Verify tests fail before implementing
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Agent is stateless - each invocation uses fresh context

---

## Summary

| Metric | Value |
|--------|-------|
| Total Tasks | 86 |
| Setup Tasks | 6 |
| Foundational Tasks | 7 |
| US1 Tasks (P1) | 11 |
| US2 Tasks (P2) | 8 |
| US3 Tasks (P3) | 8 |
| US4 Tasks (P4) | 8 |
| US5 Tasks (P5) | 8 |
| US6 Tasks (P6) | 10 |
| US7 Tasks (P7) | 10 |
| Polish Tasks | 10 |
| Parallel Opportunities | 27 tasks marked [P] |
| MVP Scope | Setup + Foundational + US1 (24 tasks) |
