# Implementation Plan: AI-Native Todo Core Foundation (Phase 1)

**Branch**: `006-ai-todo-core-foundation` | **Date**: 2026-01-04 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/006-ai-todo-core-foundation/spec.md`

## Summary

Extend the existing FastAPI backend with new SQLModel entities (Conversation, Message) and their CRUD operations to establish the stateless foundation for AI-native task management. This phase focuses on reliable data persistence without any AI or conversational logic.

**Primary Deliverables**:
- Conversation and Message SQLModel models
- Repository/service layer for conversation management
- RESTful API endpoints for conversation CRUD
- Integration with existing JWT authentication

---

## Technical Context

**Language/Version**: Python 3.11+ (existing)
**Primary Dependencies**: FastAPI, SQLModel, uvicorn, PyJWT (existing)
**Storage**: Neon Serverless PostgreSQL via SQLModel (existing connection)
**Testing**: pytest with httpx TestClient (existing setup)
**Target Platform**: Linux server (Docker-ready)
**Project Type**: Web application (backend-only for this phase)
**Performance Goals**: Standard web API (<500ms p95 for CRUD operations)
**Constraints**: Stateless backend, no in-memory business state, user-scoped queries
**Scale/Scope**: Multi-user, up to 1000+ messages per conversation

---

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Pre-Design Check

| Principle | Status | Evidence |
|-----------|--------|----------|
| I. Security by Default | PASS | All new endpoints require JWT auth; user_id validated on every route |
| II. Separation of Concerns | PASS | New models in models/, services in services/, routes in api/ |
| III. RESTful API Design | PASS | New endpoints follow existing `/api/{user_id}/...` pattern |
| IV. Data Integrity and Ownership | PASS | Foreign keys enforce relationships; user_id required on all queries |
| V. Error Handling Standards | PASS | Using existing 401/403/404/422 patterns |
| VI. Frontend Standards | N/A | Backend-only phase |
| VII. Spec-Driven Development | PASS | Implementation follows spec.md requirements FR-008 through FR-022 |

### Post-Design Check

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Security by Default | PASS | Conversation endpoints verify user ownership same as tasks |
| II. Separation of Concerns | PASS | Models, services, schemas, routes all separate |
| III. RESTful API Design | PASS | OpenAPI contract defined in contracts/openapi.yaml |
| IV. Data Integrity and Ownership | PASS | CASCADE delete for conversation→messages |
| V. Error Handling Standards | PASS | Same patterns as existing task endpoints |
| VII. Spec-Driven Development | PASS | All FRs mapped to implementation tasks |

---

## Project Structure

### Documentation (this feature)

```text
specs/006-ai-todo-core-foundation/
├── plan.md              # This file
├── spec.md              # Feature specification
├── research.md          # Phase 0 research decisions
├── data-model.md        # Entity definitions
├── quickstart.md        # Developer guide
├── contracts/
│   └── openapi.yaml     # API contract
├── checklists/
│   └── requirements.md  # Quality checklist
└── tasks.md             # Implementation tasks (created by /sp.tasks)
```

### Source Code (repository root)

```text
backend/
├── src/
│   ├── models/
│   │   ├── __init__.py       # Export all models
│   │   ├── user.py           # Existing
│   │   ├── task.py           # Existing
│   │   ├── reminder.py       # Existing
│   │   ├── conversation.py   # NEW - Phase 1
│   │   └── message.py        # NEW - Phase 1
│   ├── services/
│   │   ├── __init__.py       # Export all services
│   │   ├── auth_service.py   # Existing
│   │   ├── task_service.py   # Existing
│   │   ├── reminder_service.py # Existing
│   │   └── conversation_service.py # NEW - Phase 1
│   ├── schemas/
│   │   ├── __init__.py       # Export all schemas
│   │   ├── auth.py           # Existing
│   │   ├── task.py           # Existing
│   │   ├── reminder.py       # Existing
│   │   └── conversation.py   # NEW - Phase 1
│   ├── api/
│   │   ├── __init__.py       # Package marker
│   │   ├── auth.py           # Existing
│   │   ├── tasks.py          # Existing
│   │   ├── reminders.py      # Existing
│   │   └── conversations.py  # NEW - Phase 1
│   ├── middleware/
│   │   └── auth.py           # Existing - no changes
│   ├── main.py               # Add new router
│   ├── database.py           # Import new models
│   └── config.py             # Existing - no changes
└── tests/
    ├── __init__.py           # Existing
    ├── test_health.py        # Existing
    ├── test_auth.py          # Existing
    ├── test_tasks.py         # Existing
    └── test_conversations.py # NEW - Phase 1
```

**Structure Decision**: Web application with backend-only changes. Following the established pattern from existing task implementation.

---

## Implementation Phases

### Phase 1: Models and Database

**Objective**: Create Conversation and Message SQLModel entities

**Tasks**:
1. Create `backend/src/models/conversation.py`
2. Create `backend/src/models/message.py`
3. Update `backend/src/models/__init__.py` to export new models
4. Update `backend/src/database.py` to import new models in `create_tables()`
5. Verify tables are created on server start

**Acceptance Criteria**:
- Tables `conversations` and `messages` exist in database
- Foreign key constraints enforced
- Indexes created on user_id and conversation_id

### Phase 2: Schemas

**Objective**: Create Pydantic schemas for API request/response

**Tasks**:
1. Create `backend/src/schemas/conversation.py` with:
   - ConversationCreate
   - ConversationResponse
   - ConversationListResponse
   - ConversationWithMessagesResponse
   - MessageCreate
   - MessageResponse
2. Update `backend/src/schemas/__init__.py` to export new schemas

**Acceptance Criteria**:
- Schemas validate according to spec (max lengths, required fields)
- Response schemas use `model_validate()` for SQLModel compatibility

### Phase 3: Services

**Objective**: Create conversation service layer with business logic

**Tasks**:
1. Create `backend/src/services/conversation_service.py` with:
   - `create_conversation(db, user_id, data)` → Conversation
   - `get_conversations(db, user_id)` → List[Conversation]
   - `get_conversation(db, user_id, conversation_id)` → Conversation | None
   - `get_conversation_with_messages(db, user_id, conversation_id)` → tuple
   - `delete_conversation(db, user_id, conversation_id)` → bool
   - `add_message(db, conversation_id, data)` → Message
   - `get_messages(db, conversation_id)` → List[Message]
2. Update `backend/src/services/__init__.py` to export new functions

**Acceptance Criteria**:
- All queries filter by user_id where applicable
- Delete cascade works (messages deleted with conversation)
- Messages returned in chronological order

### Phase 4: API Routes

**Objective**: Create REST endpoints for conversation management

**Tasks**:
1. Create `backend/src/api/conversations.py` with routes:
   - GET `/{user_id}/conversations` - List conversations
   - POST `/{user_id}/conversations` - Create conversation
   - GET `/{user_id}/conversations/{id}` - Get with messages
   - DELETE `/{user_id}/conversations/{id}` - Delete conversation
   - POST `/{user_id}/conversations/{id}/messages` - Add message
2. Update `backend/src/main.py` to include new router
3. Verify Swagger documentation shows new endpoints

**Acceptance Criteria**:
- All endpoints require JWT authentication
- User ownership verified on all operations
- Correct HTTP status codes (201, 204, 401, 403, 404, 422)

### Phase 5: Tests

**Objective**: Verify all functionality with automated tests

**Tasks**:
1. Create `backend/tests/test_conversations.py` with tests for:
   - Create conversation
   - List conversations (user-scoped)
   - Get conversation with messages
   - Add message to conversation
   - Delete conversation (cascade)
   - Cross-user access denied (404)
   - Validation errors (422)
2. Run full test suite and ensure 100% pass

**Acceptance Criteria**:
- All new endpoints have test coverage
- User isolation tested (User A cannot access User B's data)
- Edge cases tested (empty content, max length, invalid role)

---

## Complexity Tracking

No constitution violations requiring justification. The implementation follows existing patterns and introduces no new architectural complexity.

---

## Risk Analysis

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Message content too large | Low | Medium | Enforce 50,000 char limit at schema level |
| Cascade delete fails | Low | High | Test explicitly; use service-layer delete |
| Performance with 1000+ messages | Low | Medium | Pagination can be added later if needed |

---

## Definition of Done

- [ ] Conversation and Message models created and verified in database
- [ ] All CRUD operations working via API
- [ ] User isolation enforced (404 for cross-user access)
- [ ] All tests passing
- [ ] API documentation updated in Swagger UI
- [ ] No in-memory business state introduced
- [ ] Ready for MCP tool exposure in Phase 2

---

## Generated Artifacts

| Artifact | Path | Description |
|----------|------|-------------|
| Research | `specs/006-ai-todo-core-foundation/research.md` | Technical decisions |
| Data Model | `specs/006-ai-todo-core-foundation/data-model.md` | Entity definitions |
| API Contract | `specs/006-ai-todo-core-foundation/contracts/openapi.yaml` | OpenAPI 3.1 spec |
| Quickstart | `specs/006-ai-todo-core-foundation/quickstart.md` | Developer guide |

---

## Next Steps

1. Run `/sp.tasks` to generate detailed implementation tasks
2. Implement in order: Models → Schemas → Services → Routes → Tests
3. After Phase 1 complete, proceed to Phase 2 (MCP tool exposure)
