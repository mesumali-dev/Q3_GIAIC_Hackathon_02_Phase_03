# Tasks: Stateless Chat API & Conversation Persistence

**Input**: Design documents from `/specs/009-stateless-chat-api/`
**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, contracts/openapi.yaml

**Tests**: Tests are NOT explicitly requested in the specification. Tasks focus on implementation only.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3, US4, US5)
- Include exact file paths in descriptions

## User Story Mapping

| Story | Title | Priority | Spec Section |
|-------|-------|----------|--------------|
| US1 | Send Message to New Conversation | P1 | User Story 1 |
| US2 | Continue Existing Conversation | P2 | User Story 2 |
| US3 | Resume Conversation After Server Restart | P3 | User Story 3 |
| US4 | Receive Tool Call Information | P4 | User Story 4 |
| US5 | Handle Agent Errors Gracefully | P5 | User Story 5 |

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Create new files and prepare project structure for chat API feature

- [x] T001 Create chat schemas file structure in backend/src/schemas/chat.py
- [x] T002 [P] Create agent runner helper file in backend/src/agent/runner.py
- [x] T003 [P] Create chat service file in backend/src/services/chat_service.py
- [x] T004 [P] Create chat router file in backend/src/api/chat.py

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**These tasks establish the complete data flow from request to response.**

### Schemas (Data Contracts)

- [x] T005 Implement ChatRequest schema with message and conversation_id fields in backend/src/schemas/chat.py
- [x] T006 [P] Implement ToolCall schema with tool_name, parameters, result, success in backend/src/schemas/chat.py
- [x] T007 [P] Implement ChatResponse schema with conversation_id, assistant_message, tool_calls, created_at in backend/src/schemas/chat.py
- [x] T008 Export chat schemas from backend/src/schemas/__init__.py

### Agent Runner (Context Reconstruction)

- [x] T009 Implement messages_to_input_list() function to convert DB messages to SDK format in backend/src/agent/runner.py
- [x] T010 Implement extract_tool_calls() function to filter ToolCallItem from RunResult.new_items in backend/src/agent/runner.py
- [x] T011 Implement run_agent_with_history() function that executes agent with message list in backend/src/agent/runner.py

### Chat Router Registration

- [x] T012 Register chat router in FastAPI app in backend/src/main.py

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - Send Message to New Conversation (Priority: P1) MVP

**Goal**: A user can send a message without conversation_id, system creates conversation, executes agent, persists messages, and returns response with new conversation_id.

**Independent Test**: POST to `/api/{user_id}/chat` with message only (no conversation_id), verify:
1. New conversation created in database
2. User message persisted
3. Agent executed successfully
4. Assistant response persisted
5. Response includes conversation_id and assistant_message

### Implementation for User Story 1

- [x] T013 [US1] Implement get_or_create_conversation() helper in backend/src/services/chat_service.py that creates new conversation when id is None
- [x] T014 [US1] Implement process_chat_message() core function skeleton in backend/src/services/chat_service.py
- [x] T015 [US1] Add user message persistence BEFORE agent execution in process_chat_message() in backend/src/services/chat_service.py
- [x] T016 [US1] Add agent execution with message history in process_chat_message() in backend/src/services/chat_service.py
- [x] T017 [US1] Add assistant message persistence AFTER agent execution in process_chat_message() in backend/src/services/chat_service.py
- [x] T018 [US1] Build and return ChatResponse with conversation_id and assistant_message in backend/src/services/chat_service.py
- [x] T019 [US1] Export chat service functions from backend/src/services/__init__.py
- [x] T020 [US1] Implement POST /api/{user_id}/chat endpoint in backend/src/api/chat.py with JWT validation
- [x] T021 [US1] Add user_id path parameter validation against JWT user_id in backend/src/api/chat.py
- [x] T022 [US1] Add 401 error handler for missing/invalid JWT in backend/src/api/chat.py
- [x] T023 [US1] Add 422 validation error for empty message in backend/src/api/chat.py

**Checkpoint**: User Story 1 complete - users can start new conversations and receive AI responses

---

## Phase 4: User Story 2 - Continue Existing Conversation (Priority: P2)

**Goal**: A user can send a message with conversation_id, system loads history, provides context to agent, persists new messages, and returns contextual response.

**Independent Test**: Create conversation with messages, send follow-up with conversation_id, verify:
1. Conversation history loaded from database
2. Agent receives full context
3. New messages persisted in order
4. Response reflects awareness of prior messages

**Depends on**: US1 foundation (T013-T023)

### Implementation for User Story 2

- [x] T024 [US2] Implement verify_conversation_ownership() helper in backend/src/services/chat_service.py that validates user owns conversation
- [x] T025 [US2] Add conversation_id validation branch to process_chat_message() in backend/src/services/chat_service.py
- [x] T026 [US2] Add message history loading with get_messages() in process_chat_message() in backend/src/services/chat_service.py
- [x] T027 [US2] Pass full history to run_agent_with_history() in backend/src/services/chat_service.py
- [x] T028 [US2] Add 404 error handler for conversation not found in backend/src/api/chat.py
- [x] T029 [US2] Add 403 error handler for conversation ownership mismatch in backend/src/api/chat.py

**Checkpoint**: User Story 2 complete - users can continue existing conversations with full context

---

## Phase 5: User Story 3 - Resume Conversation After Server Restart (Priority: P3)

**Goal**: Validate stateless architecture - conversations resume correctly after server restart with no in-memory state.

**Independent Test**:
1. Create conversation and add messages
2. Restart server (or clear any caches)
3. Send follow-up message with conversation_id
4. Verify agent has full historical context

**Depends on**: US2 (T024-T029) - this validates the stateless design, not new functionality

### Implementation for User Story 3

- [x] T030 [US3] Audit process_chat_message() for any module-level state variables in backend/src/services/chat_service.py
- [x] T031 [US3] Audit run_agent_with_history() for any cached state in backend/src/agent/runner.py
- [x] T032 [US3] Add docstring to chat_service confirming stateless design in backend/src/services/chat_service.py
- [x] T033 [US3] Verify conversation.updated_at timestamp updates after each message in backend/src/services/chat_service.py

**Checkpoint**: User Story 3 complete - stateless design validated, conversations survive restarts

---

## Phase 6: User Story 4 - Receive Tool Call Information (Priority: P4)

**Goal**: Chat API response includes tool_calls array with information about MCP tools invoked by the agent.

**Independent Test**: Send task-related command, verify response includes:
1. tool_calls array with at least one entry
2. Each entry has tool_name, parameters, result, success
3. Greeting messages return empty tool_calls array

**Depends on**: US1 foundation for basic chat flow

### Implementation for User Story 4

- [x] T034 [US4] Enhance extract_tool_calls() to extract tool_name from raw_item in backend/src/agent/runner.py
- [x] T035 [US4] Enhance extract_tool_calls() to extract parameters from raw_item in backend/src/agent/runner.py
- [x] T036 [US4] Add result extraction from ToolCallOutputItem if available in backend/src/agent/runner.py
- [x] T037 [US4] Add success flag determination based on result in backend/src/agent/runner.py
- [x] T038 [US4] Integrate tool_calls into ChatResponse in process_chat_message() in backend/src/services/chat_service.py

**Checkpoint**: User Story 4 complete - frontend can display tool call transparency

---

## Phase 7: User Story 5 - Handle Agent Errors Gracefully (Priority: P5)

**Goal**: System handles agent errors (tool failures, timeout, model errors) gracefully with user-friendly responses.

**Independent Test**: Trigger various error conditions, verify:
1. Tool errors return user-friendly message without internal details
2. Timeout returns 504 with appropriate message
3. API errors return 502 without exposing keys

**Depends on**: US1-US4 for complete chat flow

### Implementation for User Story 5

- [x] T039 [US5] Add try/except wrapper around agent execution in process_chat_message() in backend/src/services/chat_service.py
- [x] T040 [US5] Add MaxTurnsExceeded exception handler mapping to 504 in backend/src/api/chat.py
- [x] T041 [US5] Add GuardrailTripwireTriggered exception handler mapping to 422 in backend/src/api/chat.py
- [x] T042 [US5] Add OpenAI API error handler mapping to 502 in backend/src/api/chat.py
- [x] T043 [US5] Add generic exception handler mapping to 500 in backend/src/api/chat.py
- [x] T044 [US5] Ensure error messages are user-friendly and don't expose internal details in backend/src/api/chat.py

**Checkpoint**: User Story 5 complete - production-ready error handling

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Final improvements and validation

- [x] T045 [P] Add structlog logging for chat operations in backend/src/services/chat_service.py
- [x] T046 [P] Add structlog logging for agent runner operations in backend/src/agent/runner.py
- [x] T047 Validate implementation against OpenAPI contract in specs/009-stateless-chat-api/contracts/openapi.yaml
- [ ] T048 Run manual test: Start new conversation per specs/009-stateless-chat-api/quickstart.md
- [ ] T049 Run manual test: Continue existing conversation per specs/009-stateless-chat-api/quickstart.md
- [ ] T050 Run manual test: Server restart resilience per specs/009-stateless-chat-api/quickstart.md

---

## Dependencies & Execution Order

### Phase Dependencies

```
Phase 1: Setup ──────────────────────────────────▶ Creates file structure
     │
     ▼
Phase 2: Foundational ───────────────────────────▶ Schemas + Runner + Router registration
     │
     ▼
Phase 3: US1 (P1 - MVP) ─────────────────────────▶ New conversation flow
     │
     ├──────▶ Phase 4: US2 (P2) ─────────────────▶ Continue conversation
     │              │
     │              ▼
     │        Phase 5: US3 (P3) ─────────────────▶ Stateless validation
     │
     └──────▶ Phase 6: US4 (P4) ─────────────────▶ Tool call extraction
                   │
                   ▼
             Phase 7: US5 (P5) ──────────────────▶ Error handling
                   │
                   ▼
             Phase 8: Polish ────────────────────▶ Logging + Validation
```

### User Story Dependencies

| Story | Can Start After | Independent Test |
|-------|-----------------|------------------|
| US1 | Phase 2 (Foundational) | Yes - New conversation works |
| US2 | US1 | Yes - History loads correctly |
| US3 | US2 | Yes - Survives restart |
| US4 | US1 | Yes - Tool calls visible |
| US5 | US1-US4 | Yes - Errors handled |

### Within Each User Story

1. Service layer functions first
2. Router/endpoint integration second
3. Error handling third
4. Story complete before next priority

### Parallel Opportunities

**Phase 1 - All parallel:**
```
T001, T002, T003, T004 - Different files, no dependencies
```

**Phase 2 - Schema tasks parallel:**
```
T005, T006, T007 - Different parts of same file, but independent sections
```

**Phase 8 - Logging parallel:**
```
T045, T046 - Different files
```

---

## Parallel Example: Phase 1 Setup

```bash
# Launch all setup tasks together:
Task: "Create chat schemas file in backend/src/schemas/chat.py"
Task: "Create agent runner file in backend/src/agent/runner.py"
Task: "Create chat service file in backend/src/services/chat_service.py"
Task: "Create chat router file in backend/src/api/chat.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T004)
2. Complete Phase 2: Foundational (T005-T012)
3. Complete Phase 3: User Story 1 (T013-T023)
4. **STOP and VALIDATE**: Send test message, verify response
5. Deploy/demo if ready - basic chat works

### Incremental Delivery

1. Setup + Foundational → Foundation ready
2. Add US1 → Test: New conversations work → **MVP Ready**
3. Add US2 → Test: Conversations continue → Multi-turn ready
4. Add US3 → Test: Restart resilience → Production ready
5. Add US4 → Test: Tool calls visible → Debug-friendly
6. Add US5 → Test: Errors graceful → Fully production ready
7. Polish → Test: Full validation → Frontend integration ready

### File Modification Summary

| File | Tasks |
|------|-------|
| backend/src/schemas/chat.py | T001, T005, T006, T007 |
| backend/src/schemas/__init__.py | T008 |
| backend/src/agent/runner.py | T002, T009, T010, T011, T031, T034-T037, T046 |
| backend/src/services/chat_service.py | T003, T013-T018, T024-T027, T030, T032, T033, T038, T039, T045 |
| backend/src/services/__init__.py | T019 |
| backend/src/api/chat.py | T004, T020-T023, T028, T029, T040-T044 |
| backend/src/main.py | T012 |

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence
- Total: 50 tasks across 8 phases
