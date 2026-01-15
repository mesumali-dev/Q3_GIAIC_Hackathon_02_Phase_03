---
id: "0002"
title: "Stateless Chat API Implementation Plan"
stage: plan
date: 2026-01-08
surface: agent
model: claude-opus-4-5-20251101
feature: 009-stateless-chat-api
branch: 009-stateless-chat-api
user: developer
command: /sp.plan
labels: ["chat-api", "implementation-plan", "phase-4", "stateless"]
links:
  spec: specs/009-stateless-chat-api/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/009-stateless-chat-api/plan.md
  - specs/009-stateless-chat-api/research.md
  - specs/009-stateless-chat-api/data-model.md
  - specs/009-stateless-chat-api/quickstart.md
  - specs/009-stateless-chat-api/contracts/openapi.yaml
  - CLAUDE.md
tests:
  - null
---

## Prompt

Phase: Phase 4 – Stateless Chat API & Conversation Persistence

Create:
- Chat API endpoint
- Conversation reconstruction logic
- Agent execution pipeline
- Message persistence workflow
- Response formatting with tool call metadata

Steps:
1. Define POST /api/{user_id}/chat endpoint
2. Accept input:
   - conversation_id (optional)
   - message (required)
3. If conversation_id not provided:
   - Create new Conversation record
4. Fetch conversation message history from database
5. Persist user message to Message table
6. Build agent message array (history + new message)
7. Execute agent via runner with MCP tools
8. Capture:
   - Assistant response
   - MCP tool calls
9. Persist assistant message to Message table
10. Return response payload to client

Decisions needing documentation:
- Conversation creation strategy
- Message ordering and pagination approach
- Why state is reconstructed per request
- Error handling during agent execution
- Tool call visibility in API responses

Testing strategy:
- Start new conversation and send message
- Resume existing conversation
- Kill server mid-conversation and retry
- Validate message ordering and integrity
- Test concurrent requests from same user
- Verify no memory leakage between users

Quality validation:
- Server holds zero conversational state
- Database is the single source of truth
- Agent always sees correct conversation context
- Tool calls reflect actual state changes
- API is deterministic and restart-safe

Technical details:
- Agent executed synchronously per request
- Context size limited by fetched message history
- Ready for frontend ChatKit integration
- Designed for horizontal scaling

## Response snapshot

Created comprehensive implementation plan for Phase 4 - Stateless Chat API:

**Generated Artifacts:**
1. `plan.md` - Full implementation plan with architecture, components, and requirement mapping
2. `research.md` - Resolved all technical unknowns (SDK patterns, tool call extraction, message format)
3. `data-model.md` - Entity definitions and Pydantic schemas
4. `quickstart.md` - API usage examples and testing guide
5. `contracts/openapi.yaml` - OpenAPI 3.1 specification

**Key Architectural Decisions:**
- Stateless context reconstruction from database per request
- User message persisted BEFORE agent execution, assistant AFTER
- Tool calls extracted from `RunResult.new_items` filtering by type
- `Runner.run()` async execution with conversation history as input list

**Implementation Components:**
- `backend/src/schemas/chat.py` - ChatRequest/ChatResponse/ToolCall
- `backend/src/agent/runner.py` - Agent execution helper
- `backend/src/services/chat_service.py` - Business logic orchestration
- `backend/src/api/chat.py` - FastAPI endpoint router

**Constitution Check:** All 7 principles pass (Security, Separation, RESTful, Data Integrity, Error Handling, Frontend N/A, Spec-Driven).

## Outcome

- ✅ Impact: Complete implementation plan ready for task generation
- 🧪 Tests: Test strategy defined (unit + integration + manual)
- 📁 Files: 6 files created/modified
- 🔁 Next prompts: /sp.tasks to generate implementation tasks
- 🧠 Reflection: Leveraged OpenAI Agents SDK documentation via skill for efficient research

## Evaluation notes (flywheel)

- Failure modes observed: None - all research questions resolved
- Graders run and results (PASS/FAIL): Constitution Check PASS (7/7 principles)
- Prompt variant (if applicable): Standard /sp.plan workflow
- Next experiment (smallest change to try): N/A - proceed to task generation
