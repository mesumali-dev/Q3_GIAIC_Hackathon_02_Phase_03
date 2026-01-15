# Implementation Plan: Stateless Chat API & Conversation Persistence

**Branch**: `009-stateless-chat-api` | **Date**: 2026-01-08 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/009-stateless-chat-api/spec.md`

## Summary

Implement a stateless chat API endpoint (`POST /api/{user_id}/chat`) that connects frontend clients to the AI agent from Phase 3, persists all conversation state to the database, and returns AI responses with tool call metadata. The API reconstructs conversation context from the database on every request, enabling horizontal scaling and zero-downtime deployments.

## Technical Context

**Language/Version**: Python 3.11+ (existing backend)
**Primary Dependencies**: FastAPI (existing), OpenAI Agents SDK (existing), SQLModel (existing), Pydantic (existing)
**Storage**: Neon PostgreSQL via SQLModel ORM (existing connection, existing Conversation/Message models)
**Testing**: pytest with pytest-asyncio (existing test setup)
**Target Platform**: Linux server (Docker deployment)
**Project Type**: Web application (backend API)
**Performance Goals**: < 10 seconds response time for standard operations (includes LLM inference)
**Constraints**: Zero in-memory state, database-only persistence, synchronous responses (no streaming)
**Scale/Scope**: Single endpoint, builds on existing infrastructure

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Evidence |
|-----------|--------|----------|
| I. Security by Default | ✅ PASS | JWT required, user_id validated from JWT, scoped queries |
| II. Separation of Concerns | ✅ PASS | API route → Service → Repository layers maintained |
| III. RESTful API Design | ✅ PASS | Follows `/api/{user_id}/chat` pattern with proper status codes |
| IV. Data Integrity and Ownership | ✅ PASS | All queries filtered by user_id, foreign key relationships |
| V. Error Handling Standards | ✅ PASS | 401/403/404/422/500/502/504 codes mapped |
| VI. Frontend Standards | N/A | Backend-only feature |
| VII. Spec-Driven Development | ✅ PASS | Feature maps to spec requirements FR-001 through FR-019 |

**Gate Result**: PASS - No violations. Proceed to implementation.

## Project Structure

### Documentation (this feature)

```text
specs/009-stateless-chat-api/
├── spec.md              # Feature specification
├── plan.md              # This file
├── research.md          # Phase 0 research findings
├── data-model.md        # Entity and schema definitions
├── quickstart.md        # API usage guide
├── contracts/
│   └── openapi.yaml     # OpenAPI specification
└── tasks.md             # Phase 2 output (created by /sp.tasks)
```

### Source Code (repository root)

```text
backend/
├── src/
│   ├── api/
│   │   ├── chat.py          # NEW: Chat endpoint router
│   │   └── __init__.py      # Updated: Register chat router
│   ├── services/
│   │   ├── chat_service.py  # NEW: Chat business logic
│   │   └── __init__.py      # Updated: Export chat functions
│   ├── schemas/
│   │   ├── chat.py          # NEW: ChatRequest/ChatResponse
│   │   └── __init__.py      # Updated: Export chat schemas
│   └── agent/
│       └── runner.py        # NEW: Agent execution helper
└── tests/
    ├── test_chat_api.py     # NEW: Chat endpoint tests
    └── test_chat_service.py # NEW: Service unit tests
```

**Structure Decision**: Follows existing web application pattern with `backend/src/api`, `backend/src/services`, and `backend/src/schemas` directories. New files integrate with existing module exports.

## Architecture Overview

### Request Flow

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Client    │───▶│  FastAPI    │───▶│  Chat       │───▶│  Agent      │
│             │    │  Router     │    │  Service    │    │  Runner     │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
                          │                  │                  │
                          │                  │                  │
                          ▼                  ▼                  ▼
                   ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
                   │  JWT Auth   │    │  Postgres   │    │  OpenAI     │
                   │  Middleware │    │  (SQLModel) │    │  API        │
                   └─────────────┘    └─────────────┘    └─────────────┘
```

### Sequence Diagram

```
Client          Router          Service         DB              Agent
  │                │                │            │                 │
  │ POST /chat     │                │            │                 │
  ├───────────────▶│                │            │                 │
  │                │ validate JWT   │            │                 │
  │                ├───────────────▶│            │                 │
  │                │                │ get/create │                 │
  │                │                │ conversation                 │
  │                │                ├───────────▶│                 │
  │                │                │◀───────────┤                 │
  │                │                │            │                 │
  │                │                │ get msgs   │                 │
  │                │                ├───────────▶│                 │
  │                │                │◀───────────┤                 │
  │                │                │            │                 │
  │                │                │ add user   │                 │
  │                │                │ message    │                 │
  │                │                ├───────────▶│                 │
  │                │                │◀───────────┤                 │
  │                │                │            │                 │
  │                │                │ run agent  │                 │
  │                │                ├────────────────────────────▶│
  │                │                │◀────────────────────────────┤
  │                │                │            │                 │
  │                │                │ add asst   │                 │
  │                │                │ message    │                 │
  │                │                ├───────────▶│                 │
  │                │                │◀───────────┤                 │
  │                │◀───────────────┤            │                 │
  │◀───────────────┤                │            │                 │
  │ ChatResponse   │                │            │                 │
```

## Implementation Components

### 1. Chat Schemas (`backend/src/schemas/chat.py`)

New Pydantic models for request/response validation:

- `ChatRequest`: message (required), conversation_id (optional)
- `ToolCall`: tool_name, parameters, result, success
- `ChatResponse`: conversation_id, assistant_message, tool_calls[], created_at

### 2. Agent Runner Helper (`backend/src/agent/runner.py`)

Encapsulates agent execution with context reconstruction:

- `run_agent_with_history()`: Execute agent with message history
- `extract_tool_calls()`: Extract ToolCall objects from RunResult.new_items
- `messages_to_input_list()`: Convert DB messages to SDK format

### 3. Chat Service (`backend/src/services/chat_service.py`)

Business logic orchestration:

- `process_chat_message()`: Main entry point
  1. Get or create conversation
  2. Load message history
  3. Persist user message
  4. Run agent
  5. Persist assistant message
  6. Return ChatResponse

### 4. Chat Router (`backend/src/api/chat.py`)

FastAPI endpoint definition:

- `POST /api/{user_id}/chat` with JWT validation
- Error handling and status code mapping
- Integration with auth middleware

## Key Design Decisions

### 1. Stateless Context Reconstruction

Every request reconstructs conversation context from the database:
- Load all messages for conversation_id
- Convert to OpenAI message format
- Pass as `input` list to `Runner.run()`

**Rationale**: Enables horizontal scaling, zero-downtime deploys, server restart resilience.

### 2. Message Persistence Order

1. Persist user message BEFORE agent execution
2. Persist assistant message AFTER agent execution

**Rationale**: Ensures user message is never lost, even on agent failure.

### 3. Tool Call Extraction

Extract tool calls from `RunResult.new_items` by filtering for `type == "tool_call_item"`.

**Rationale**: Documented SDK approach, provides rich tool call metadata.

### 4. Synchronous Execution

Use `Runner.run()` async method within FastAPI async handler.

**Rationale**: FastAPI is async-native; keeps implementation simple without streaming complexity.

## Error Handling Strategy

| Exception | HTTP Status | User Message |
|-----------|-------------|--------------|
| JWT missing/invalid | 401 | "Not authenticated" |
| user_id mismatch | 403 | "Access denied" |
| conversation not found | 404 | "Conversation not found" |
| validation error | 422 | Pydantic validation details |
| MaxTurnsExceeded | 504 | "The assistant took too long to respond" |
| GuardrailTriggered | 422 | "Request was blocked by safety controls" |
| OpenAI API error | 502 | "AI service temporarily unavailable" |
| Database error | 500 | "An unexpected error occurred" |

## Testing Strategy

### Unit Tests

- `test_chat_schemas.py`: Validate request/response serialization
- `test_agent_runner.py`: Test context reconstruction and tool extraction
- `test_chat_service.py`: Test business logic with mocked dependencies

### Integration Tests

- `test_chat_api.py`: Full endpoint tests with real database
  - Test new conversation creation
  - Test conversation continuation
  - Test authentication errors
  - Test conversation ownership

### Manual Tests

- Server restart resilience test
- Concurrent request test
- Tool call visibility test

## Dependencies

### Existing (No Changes)

- FastAPI router infrastructure
- JWT authentication middleware
- SQLModel database connection
- Conversation and Message models
- Task agent (`task_agent`)
- MCP tools (add_task, list_tasks, etc.)

### New (None Required)

All dependencies already installed in the project.

## Complexity Tracking

No violations to justify - implementation follows existing patterns.

## Acceptance Criteria Mapping

| Requirement | Implementation |
|-------------|----------------|
| FR-001 | `POST /api/{user_id}/chat` endpoint in chat.py |
| FR-002 | ChatRequest schema with message + conversation_id |
| FR-003 | `get_or_create_conversation()` in chat_service |
| FR-004 | `verify_conversation_ownership()` in chat_service |
| FR-005 | `get_messages()` call in chat_service |
| FR-006 | User message persisted before `run_agent()` |
| FR-007 | `messages_to_input_list()` rebuilds context |
| FR-008 | `Runner.run()` with message history |
| FR-009 | `extract_tool_calls()` from RunResult |
| FR-010 | Assistant message persisted after `run_agent()` |
| FR-011 | `add_message()` updates conversation.updated_at |
| FR-012 | ChatResponse schema with all fields |
| FR-013 | JWT user_id used in all DB queries |
| FR-014 | Error mapping in router exception handlers |
| FR-015 | No module-level state variables |
| FR-016 | Try/except with safe error messages |
| FR-017 | `messages_to_input_list()` conversion |
| FR-018 | Pydantic validation on ChatRequest |
| FR-019 | MessageCreate with role validation |

## Next Steps

Run `/sp.tasks` to generate the task breakdown for implementation.
