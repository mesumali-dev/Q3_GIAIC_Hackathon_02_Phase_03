---
id: 0002
title: Create Implementation Plan for AI Todo Core Foundation
stage: plan
date: 2026-01-04
surface: agent
model: claude-opus-4-5-20251101
feature: 006-ai-todo-core-foundation
branch: 006-ai-todo-core-foundation
user: system
command: /sp.plan
labels: ["planning", "backend", "conversation", "message", "sqlmodel", "phase-1"]
links:
  spec: specs/006-ai-todo-core-foundation/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/006-ai-todo-core-foundation/plan.md
  - specs/006-ai-todo-core-foundation/research.md
  - specs/006-ai-todo-core-foundation/data-model.md
  - specs/006-ai-todo-core-foundation/quickstart.md
  - specs/006-ai-todo-core-foundation/contracts/openapi.yaml
tests:
  - N/A (planning phase - no code tests)
---

## Prompt

Phase: Phase 1 - Core Foundation (Stateless Backend & Persistence)

Create:
- Database schema and migrations
- SQLModel entities for Task, Conversation, Message
- Repository layer for database access
- FastAPI backend skeleton
- Internal services for task and conversation management

Steps:
1. Initialize backend project structure
2. Configure Neon PostgreSQL connection
3. Define SQLModel models: Task, Conversation, Message
4. Create migration scripts
5. Implement repository layer (CRUD operations)
6. Implement service layer enforcing business rules
7. Validate stateless behavior across requests
8. Add basic health and integrity checks

Decisions needing documentation:
- Why SQLModel over raw SQL or SQLAlchemy
- Why Neon Serverless PostgreSQL for stateless architecture
- Separation between repository and service layers
- Conversation persistence strategy vs in-memory context
- User scoping strategy for multi-tenant safety

Testing strategy:
- Verify task CRUD operations persist correctly
- Validate conversation and message storage
- Restart server and confirm data continuity
- Ensure no global or session state is retained
- Confirm all queries are user-scoped

Quality validation:
- Database is the single source of truth
- No logic depends on request memory
- Schema supports future MCP tool expansion
- Clean separation between data, service, and API layers

Technical details:
- No AI agents or MCP tools invoked in this phase
- Focus strictly on correctness and persistence
- Prepare interfaces needed by Phase 2 MCP server

## Response snapshot

Created comprehensive implementation plan with the following artifacts:

1. **research.md** - 7 technical decisions documented:
   - SQLModel selection (vs raw SQL, SQLAlchemy)
   - Neon PostgreSQL for stateless architecture
   - Combined service layer (no separate repository)
   - Database persistence for conversations (no in-memory)
   - User scoping at service layer
   - Message role as string literals (user/assistant/system)
   - Cascade delete for conversations

2. **data-model.md** - Entity definitions:
   - Conversation: id, user_id, title, created_at, updated_at
   - Message: id, conversation_id, role, content, created_at
   - Complete SQLModel implementations provided
   - Query patterns documented

3. **contracts/openapi.yaml** - OpenAPI 3.1 specification:
   - 5 new conversation/message endpoints
   - Request/response schemas
   - Error responses (401, 403, 404, 422)
   - JWT authentication requirements

4. **quickstart.md** - Developer guide:
   - Setup instructions
   - Development workflow
   - Key files reference
   - Troubleshooting guide

5. **plan.md** - Implementation phases:
   - Phase 1: Models and Database
   - Phase 2: Schemas
   - Phase 3: Services
   - Phase 4: API Routes
   - Phase 5: Tests

Constitution check passed all 7 principles.

## Outcome

- Impact: Complete implementation blueprint for Phase 1 - enables immediate development start
- Tests: N/A (planning phase)
- Files: 5 artifacts created (plan.md, research.md, data-model.md, quickstart.md, openapi.yaml)
- Next prompts: /sp.tasks (to generate detailed implementation tasks)
- Reflection: Existing codebase patterns (task CRUD) provide clear template for conversation implementation. No architectural changes needed.

## Evaluation notes (flywheel)

- Failure modes observed: None - planning completed successfully
- Graders run and results (PASS/FAIL): Constitution check - 7/7 PASS (pre-design and post-design)
- Prompt variant (if applicable): Standard /sp.plan command
- Next experiment (smallest change to try): Proceed to /sp.tasks for task breakdown
