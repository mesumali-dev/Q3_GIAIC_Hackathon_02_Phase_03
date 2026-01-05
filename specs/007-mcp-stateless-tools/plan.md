# Implementation Plan: MCP Stateless Tool Layer

**Branch**: `007-mcp-stateless-tools` | **Date**: 2026-01-05 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/007-mcp-stateless-tools/spec.md`

**Note**: This template is filled in by the `/sp.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Build a stateless MCP server using the Official MCP SDK that exposes five task operation tools (`add_task`, `list_tasks`, `complete_task`, `delete_task`, `update_task`) to enable AI agents to interact with task data safely and deterministically. All tools will be stateless, persist changes directly to the Neon PostgreSQL database via the existing SQLModel service layer, and enforce user-scoped access. This layer prepares the foundation for Phase 3 AI agent integration without implementing any conversational or natural language processing logic.

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**: Official MCP SDK (Python), FastAPI (existing), SQLModel (existing), PyJWT (existing)
**Storage**: Neon Serverless PostgreSQL via SQLModel ORM (existing connection)
**Testing**: pytest, MCP tool invocation testing (direct tool calls)
**Target Platform**: Linux server (development), compatible with MCP client applications
**Project Type**: Backend extension (MCP server alongside existing FastAPI server)
**Performance Goals**: 500ms for standard tool operations (single task CRUD), 1 second for list operations with up to 1000 tasks
**Constraints**: Stateless operation (no in-memory state), all persistence to database, user-scoped operations only, no side effects beyond database writes
**Scale/Scope**: 5 MCP tools, single MCP server, reuses existing service/repository layer (task_service.py)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Core Principles Compliance

✅ **I. Security by Default**
- MCP tools receive authenticated user_id as parameter (authentication handled externally by calling agent/client)
- All tool operations filter by user_id via existing task service
- No hardcoded secrets (MCP SDK configuration uses environment variables if needed)
- User-scoped access enforced at service layer

✅ **II. Separation of Concerns**
- MCP server is separate process from FastAPI server (clean boundary)
- Tool layer delegates to existing service/repository layer (no business logic duplication)
- Database access only via SQLModel ORM (existing pattern)
- MCP tools are stateless presentation layer for AI agent consumption

✅ **III. RESTful API Design**
- MCP tools complement (not replace) existing REST API
- MCP tool naming follows task operation semantics (add_task, list_tasks, etc.)
- Idempotent operations where applicable (complete_task)
- User ownership enforced through user_id parameter

✅ **IV. Data Integrity and Ownership**
- All tool operations use existing service layer that enforces user_id filtering
- Database operations via SQLModel ORM (existing)
- Task ownership verified through service layer

✅ **V. Error Handling Standards**
- MCP tools return structured error responses suitable for AI consumption
- Error types: TaskNotFoundError, ValidationError, AuthorizationError, DatabaseError
- No internal implementation details exposed in error messages

⚠️ **VI. Frontend Standards**
- Not applicable (MCP tools consumed by AI agents, not frontend)

✅ **VII. Spec-Driven Development**
- Implementation directly follows spec.md requirements
- All 19 functional requirements mapped to implementation tasks
- No feature invention beyond specification

### Quality Gates

1. ✅ **Security Review**: User-scoped operations via service layer, no secrets in code
2. ✅ **API Compliance**: MCP tool schemas defined with input/output contracts
3. ✅ **Data Isolation**: Service layer filters by user_id
4. N/A **Responsive Check**: Not applicable (no UI)
5. ✅ **Error Handling**: Structured error responses for all failure paths

### Constitution Compliance Summary

**Status**: ✅ PASS (all applicable principles satisfied)

No constitution violations. MCP tool layer aligns with existing architecture by:
- Reusing service/repository layer (no duplication)
- Maintaining stateless operation (principle II)
- Enforcing user-scoped access (principles I, IV)
- Providing clean AI-consumable interface (principle II)

## Project Structure

### Documentation (this feature)

```text
specs/007-mcp-stateless-tools/
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output - MCP SDK integration research
├── data-model.md        # Phase 1 output - MCP tool schemas and data contracts
├── quickstart.md        # Phase 1 output - MCP server setup and testing guide
├── contracts/           # Phase 1 output - MCP tool JSON schemas
│   ├── add_task.json
│   ├── list_tasks.json
│   ├── complete_task.json
│   ├── delete_task.json
│   └── update_task.json
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
backend/
├── src/
│   ├── mcp/                    # NEW: MCP server implementation
│   │   ├── __init__.py
│   │   ├── server.py           # MCP server initialization and configuration
│   │   ├── tools/              # MCP tool implementations
│   │   │   ├── __init__.py
│   │   │   ├── add_task.py     # add_task tool implementation
│   │   │   ├── list_tasks.py   # list_tasks tool implementation
│   │   │   ├── complete_task.py # complete_task tool implementation
│   │   │   ├── delete_task.py  # delete_task tool implementation
│   │   │   └── update_task.py  # update_task tool implementation
│   │   ├── schemas.py          # MCP tool input/output schemas (Pydantic models)
│   │   └── errors.py           # MCP-specific error types and handlers
│   ├── services/               # EXISTING: Business logic layer
│   │   └── task_service.py     # EXISTING: Reused by MCP tools
│   ├── models/                 # EXISTING: SQLModel entities
│   │   └── task.py             # EXISTING: Task model
│   └── database.py             # EXISTING: Database connection
└── tests/
    └── mcp/                    # NEW: MCP tool tests
        ├── __init__.py
        ├── test_add_task.py
        ├── test_list_tasks.py
        ├── test_complete_task.py
        ├── test_delete_task.py
        └── test_update_task.py
```

**Structure Decision**: Backend extension with dedicated `src/mcp/` directory

The MCP server is implemented as a separate module within the existing backend codebase. This approach:
- Maintains separation from the FastAPI server (different entry point)
- Reuses existing service/repository/model layers (no duplication)
- Allows independent testing and deployment of MCP tools
- Keeps MCP-specific code isolated in `src/mcp/` directory

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

No complexity violations. Implementation follows minimal viable approach:
- Reuses existing service layer (no new business logic)
- Single MCP server process (no distributed complexity)
- Standard MCP SDK patterns (no custom protocols)
