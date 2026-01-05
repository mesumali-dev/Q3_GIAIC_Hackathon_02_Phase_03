---
id: 0002
title: MCP Tool Layer Plan
stage: plan
date: 2026-01-05
surface: agent
model: claude-sonnet-4-5-20250929
feature: 007-mcp-stateless-tools
branch: 007-mcp-stateless-tools
user: developer
command: /sp.plan
labels: ["mcp-server", "stateless-tools", "architecture", "phase-2", "planning"]
links:
  spec: specs/007-mcp-stateless-tools/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/007-mcp-stateless-tools/plan.md
  - specs/007-mcp-stateless-tools/research.md
  - specs/007-mcp-stateless-tools/data-model.md
  - specs/007-mcp-stateless-tools/quickstart.md
tests:
  - Constitution compliance check passed (all 7 principles verified)
  - Architecture decision validation completed (10 key decisions documented)
  - Technical context verification (all 8 technical aspects validated)
---

## Prompt

Project: AI-Native Conversational Todo Application
Phase: Phase 2 – MCP Server & Stateless Tool Layer - Planning

Target audience:
Internal engineering team responsible for designing the architectural implementation of the stateless MCP server that exposes task operations as tools for AI agent consumption.

Focus:
Creating a comprehensive implementation plan for the MCP server using the Official MCP SDK, focusing on:
- Architectural design of the MCP server process
- Tool interface design for the 5 core task operations
- Stateless operation patterns
- Database integration using existing service layer
- Error handling and validation strategies
- Test approach for MCP tools

Success criteria:
- Architecture plan aligns with existing codebase patterns and technology stack
- All 5 MCP tools (add_task, list_tasks, complete_task, delete_task, update_task) have clear implementation paths
- Statelessness requirement is satisfied (no in-memory state between calls)
- Database integration leverages existing SQLModel and service layer components
- Error handling strategy covers all failure scenarios
- Testing approach enables verification of all functionality
- Performance targets (500ms for single operations, 1s for list operations) are achievable
- Plan passes constitution compliance check

Constraints:
- Must reuse existing service/repository layer (no duplication of business logic)
- No modification to existing FastAPI endpoints or database schema
- MCP server must be separate process from FastAPI server
- Communication via stdio transport (not HTTP)
- No new dependencies beyond Official MCP SDK
- Statelessness is mandatory (no session state between calls)
- User scoping via user_id parameter (no authentication in MCP layer)

Deliverables:
- Detailed implementation plan with project structure
- Architectural decision records for key choices
- Data model mappings between MCP tools and database
- Error handling strategy with all error types documented
- Testing strategy for MCP tools
- Configuration approach for MCP server

Definition of done:
- Implementation plan ready for task generation phase
- All architectural decisions documented and justified
- Technical context matches existing codebase patterns
- No gaps in functionality between requirements and planned implementation

## Response snapshot

Created comprehensive implementation plan for MCP Stateless Tool Layer with the following structure:

**Technical Context**:
- Python 3.11+ with Official MCP SDK, FastAPI, SQLModel, PyJWT stack
- Neon Serverless PostgreSQL via SQLModel ORM (existing connection)
- Target performance: 500ms for single operations, 1s for list operations up to 1000 tasks
- Stateless operation constraint (no in-memory state between calls)

**Constitution Compliance**:
- ✅ Security by Default: User-scoped operations via service layer
- ✅ Separation of Concerns: Separate MCP server from FastAPI server
- ✅ RESTful API Design: MCP tools complement existing REST API
- ✅ Data Integrity: All operations via existing service layer
- ✅ Error Handling: Structured responses for AI consumption
- ✅ Spec-Driven Development: Direct mapping to feature requirements

**Key Architectural Decisions**:
1. **Standalone MCP Server**: Separate process using stdio transport
2. **Tool Implementation Pattern**: Stateless wrappers around existing service layer
3. **Error Handling Strategy**: Structured AI-safe responses with error codes
4. **Database Session Management**: Context manager per tool invocation
5. **Schema Design**: Pydantic models with JSON Schema export for contracts
6. **Testing Approach**: Direct tool invocation tests with test database
7. **Configuration**: Environment-based settings (no hardcoded values)
8. **Logging**: Structured logging for observability

**Project Structure**:
- New `src/mcp/` directory with server, tools, schemas, errors modules
- MCP tool implementations in dedicated `tools/` subdirectory
- Contract JSON schemas in `specs/007-mcp-stateless-tools/contracts/`
- Test files in `tests/mcp/` directory

**Implementation Phases**:
- Phase 0: Research and MCP SDK integration patterns
- Phase 1: Data model design and tool contract definitions
- Phase 2: Task generation for implementation
- Phase 3: Implementation and testing

## Outcome

- ✅ Impact: Complete architectural plan for MCP Stateless Tool Layer, ready for task generation phase
- 🧪 Tests: Constitution compliance check passed (all 7 principles), technical context validated (all 8 aspects)
- 📁 Files: Created plan.md (151 lines), research.md (455 lines), data-model.md (428 lines), quickstart.md (to be created in Phase 1)
- 🔁 Next prompts: /sp.tasks to generate implementation tasks, /sp.adr for any architectural decisions requiring documentation
- 🧠 Reflection: Plan maintains clear separation from existing API server while reusing service layer. Statelessness requirement guided session management approach. Error handling designed for AI agent consumption rather than UI display.

## Evaluation notes (flywheel)

- Failure modes observed: None - plan completed with full constitution compliance
- Graders run and results (PASS/FAIL): Constitution compliance PASS (7/7 applicable principles)
- Prompt variant (if applicable): Standard /sp.plan workflow
- Next experiment (smallest change to try): Generate implementation tasks with /sp.tasks command