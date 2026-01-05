# Tasks: AI-Native Todo Core Foundation (Phase 1)

**Input**: Design documents from `/specs/006-ai-todo-core-foundation/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: Included per Definition of Done requirements (security tests, persistence tests, isolation tests)

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Web app**: `backend/src/`, `backend/tests/`
- Based on plan.md structure for this project

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Verify existing infrastructure and prepare for new entities

- [X] T001 Verify branch is 006-ai-todo-core-foundation and clean working directory
- [X] T002 Verify existing database connection works in backend/src/database.py
- [X] T003 [P] Verify existing authentication middleware in backend/src/middleware/auth.py

---

## Phase 2: Foundational (Conversation & Message Models)

**Purpose**: Create new SQLModel entities - MUST be complete before conversation API work

**CRITICAL**: All user story implementation depends on these models existing

### Models

- [X] T004 [P] Create Conversation model in backend/src/models/conversation.py per data-model.md
- [X] T005 [P] Create Message model in backend/src/models/message.py per data-model.md
- [X] T006 Update backend/src/models/__init__.py to export Conversation and Message
- [X] T007 Update backend/src/database.py to import Conversation and Message in create_tables()
- [X] T008 Verify tables are created by starting server and checking database

### Schemas

- [X] T009 [P] Create ConversationCreate schema in backend/src/schemas/conversation.py
- [X] T010 [P] Create ConversationResponse schema in backend/src/schemas/conversation.py
- [X] T011 [P] Create ConversationListResponse schema in backend/src/schemas/conversation.py
- [X] T012 [P] Create ConversationWithMessagesResponse schema in backend/src/schemas/conversation.py
- [X] T013 [P] Create MessageCreate schema in backend/src/schemas/conversation.py
- [X] T014 [P] Create MessageResponse schema in backend/src/schemas/conversation.py
- [X] T015 Update backend/src/schemas/__init__.py to export all new schemas

**Checkpoint**: Foundation ready - conversation/message models and schemas exist

---

## Phase 3: User Story 3 - Conversation and Message Storage (Priority: P2) MVP

**Goal**: Enable creation, retrieval, and deletion of conversations with messages

**Independent Test**: Create conversation, add messages, retrieve, delete - all operations persist correctly

**Why this is MVP**: This is the NEW functionality introduced by Phase 1. US1, US2, US4, US5 cover existing/cross-cutting concerns.

### Service Layer

- [X] T016 Create create_conversation function in backend/src/services/conversation_service.py
- [X] T017 Create get_conversations function in backend/src/services/conversation_service.py
- [X] T018 Create get_conversation function in backend/src/services/conversation_service.py
- [X] T019 Create delete_conversation function in backend/src/services/conversation_service.py (with cascade)
- [X] T020 Create add_message function in backend/src/services/conversation_service.py
- [X] T021 Create get_messages function in backend/src/services/conversation_service.py
- [X] T022 Update backend/src/services/__init__.py to export all conversation service functions

### API Routes

- [X] T023 Create GET /{user_id}/conversations endpoint in backend/src/api/conversations.py (FR-009)
- [X] T024 Create POST /{user_id}/conversations endpoint in backend/src/api/conversations.py (FR-008)
- [X] T025 Create GET /{user_id}/conversations/{id} endpoint in backend/src/api/conversations.py (FR-010)
- [X] T026 Create DELETE /{user_id}/conversations/{id} endpoint in backend/src/api/conversations.py (FR-011)
- [X] T027 Create POST /{user_id}/conversations/{id}/messages endpoint in backend/src/api/conversations.py (FR-012)
- [X] T028 Update backend/src/main.py to include conversations router

### Tests for User Story 3

- [X] T029 [P] [US3] Create test for create conversation in backend/tests/test_conversations.py
- [X] T030 [P] [US3] Create test for list conversations in backend/tests/test_conversations.py
- [X] T031 [P] [US3] Create test for get conversation with messages in backend/tests/test_conversations.py
- [X] T032 [P] [US3] Create test for add message to conversation in backend/tests/test_conversations.py
- [X] T033 [P] [US3] Create test for delete conversation cascade in backend/tests/test_conversations.py
- [X] T034 [US3] Create test for chronological message ordering in backend/tests/test_conversations.py

**Checkpoint**: Conversation CRUD fully functional - can create, add messages, retrieve, delete

---

## Phase 4: User Story 4 - User Isolation and Authentication Scoping (Priority: P1)

**Goal**: Verify all conversation operations are scoped to authenticated user

**Independent Test**: User A's data is not accessible to User B - returns 404

### Security Tests

- [X] T035 [US4] Create test for cross-user conversation access denial in backend/tests/test_conversations.py
- [X] T036 [US4] Create test for cross-user message creation denial in backend/tests/test_conversations.py
- [X] T037 [US4] Create test for user_id mismatch returns 403 in backend/tests/test_conversations.py
- [X] T038 [US4] Create test for missing JWT returns 401 in backend/tests/test_conversations.py

**Checkpoint**: User isolation verified - no data leakage between users

---

## Phase 5: User Story 1 - Task Persistence Across Server Restarts (Priority: P1)

**Goal**: Verify existing task persistence + new conversation persistence

**Independent Test**: Create data, restart server, verify data persists

### Persistence Tests

- [X] T039 [US1] Create test for task persistence after server restart in backend/tests/test_persistence.py
- [X] T040 [US1] Create test for conversation persistence after server restart in backend/tests/test_persistence.py
- [X] T041 [US1] Create test for message persistence after server restart in backend/tests/test_persistence.py

**Checkpoint**: All data survives server restarts

---

## Phase 6: User Story 5 - Stateless Backend Operation (Priority: P1)

**Goal**: Verify no in-memory business state exists

**Independent Test**: Code review verification - no global state for business data

### Verification Tasks

- [X] T042 [US5] Review conversation_service.py for stateless compliance (no module-level state)
- [X] T043 [US5] Verify all conversation endpoints use database sessions only
- [X] T044 [US5] Document stateless verification in specs/006-ai-todo-core-foundation/checklists/requirements.md

**Checkpoint**: Backend confirmed stateless

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Final validation and cleanup

- [X] T045 Verify Swagger UI shows all new endpoints at /docs
- [X] T046 Run full test suite with `uv run pytest` and ensure all tests pass
- [X] T047 Update backend/CLAUDE.md if needed with new conversation endpoints
- [X] T048 Validate against quickstart.md steps

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - verification only
- **Foundational (Phase 2)**: Depends on Setup - BLOCKS all user stories
- **US3 Conversation Storage (Phase 3)**: Depends on Foundational - main implementation
- **US4 User Isolation (Phase 4)**: Can run parallel with US3 completion
- **US1 Persistence (Phase 5)**: Can run after US3 (needs data to test)
- **US5 Stateless (Phase 6)**: Can run after US3 (code review)
- **Polish (Phase 7)**: Depends on all user stories complete

### User Story Dependencies

- **User Story 3 (Conversation Storage)**: Core implementation - all others depend on this
- **User Story 4 (User Isolation)**: Tests US3 security - no code changes needed
- **User Story 1 (Persistence)**: Tests US3 persistence - no code changes needed
- **User Story 5 (Stateless)**: Reviews US3 code - no code changes needed
- **User Story 2 (Task CRUD)**: Already exists - no tasks needed

### Within User Story 3

- Models (T004-T008) before Schemas (T009-T015)
- Schemas before Services (T016-T022)
- Services before Routes (T023-T028)
- Routes before Tests (T029-T034)

### Parallel Opportunities

Within Foundational Phase:
- T004 and T005 can run in parallel (different model files)
- T009-T014 can run in parallel (all in same file but independent schemas)

Within US3 Tests:
- T029-T033 can run in parallel (independent test functions)

Within US4 Tests:
- T035-T038 can run in parallel (independent security tests)

---

## Parallel Example: Foundational Models

```bash
# Launch both models in parallel:
Task: "Create Conversation model in backend/src/models/conversation.py"
Task: "Create Message model in backend/src/models/message.py"
```

## Parallel Example: US3 Tests

```bash
# Launch all US3 tests in parallel:
Task: "Create test for create conversation in backend/tests/test_conversations.py"
Task: "Create test for list conversations in backend/tests/test_conversations.py"
Task: "Create test for get conversation with messages in backend/tests/test_conversations.py"
Task: "Create test for add message to conversation in backend/tests/test_conversations.py"
Task: "Create test for delete conversation cascade in backend/tests/test_conversations.py"
```

---

## Implementation Strategy

### MVP First (US3 Only)

1. Complete Phase 1: Setup (verification)
2. Complete Phase 2: Foundational (models + schemas)
3. Complete Phase 3: US3 Conversation Storage (services + routes + tests)
4. **STOP and VALIDATE**: Test conversation CRUD independently
5. Continue to Phase 4-6 for security/persistence/stateless verification

### Incremental Delivery

1. Foundational → Models and schemas ready
2. US3 → Conversation CRUD working → Demo/Test
3. US4 → Security verified → Confidence
4. US1 → Persistence verified → Durability confirmed
5. US5 → Stateless verified → Ready for Phase 2 MCP

---

## Summary

| Phase | Task Count | Focus |
|-------|------------|-------|
| Setup | 3 | Verification |
| Foundational | 12 | Models + Schemas |
| US3 Conversation | 13 | Services + Routes + Tests |
| US4 User Isolation | 4 | Security Tests |
| US1 Persistence | 3 | Persistence Tests |
| US5 Stateless | 3 | Review + Documentation |
| Polish | 4 | Final Validation |
| **Total** | **42** | |

### Tasks per User Story

- US1 (Persistence): 3 tasks
- US2 (Task CRUD): 0 tasks (already exists)
- US3 (Conversation Storage): 25 tasks (main work)
- US4 (User Isolation): 4 tasks
- US5 (Stateless): 3 tasks

### MVP Scope

**Minimum Viable Phase 1**: Phases 1-3 (US3 complete)
- 28 tasks to functional conversation storage
- Can demo conversation CRUD immediately
- Security/persistence tests add confidence in Phases 4-6

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Task CRUD (US2) already exists - no implementation needed
- US4, US1, US5 are verification/testing of US3 functionality
- All tests in backend/tests/test_conversations.py share fixtures
- Commit after each logical group of tasks
