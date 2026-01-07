# Implementation Plan: AI Agent & MCP Tool Orchestration

**Branch**: `008-ai-agent-mcp-orchestration` | **Date**: 2026-01-08 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/008-ai-agent-mcp-orchestration/spec.md`

## Summary

Implement a single task-management AI agent using the OpenAI Agents SDK that interprets natural language commands and orchestrates MCP tools (add_task, list_tasks, complete_task, delete_task, update_task, schedule_reminder) to manage user tasks and reminders. The agent operates statelessly per invocation, receiving user_id through context, and is designed to be wrapped by a stateless chat API in Phase 4.

## Technical Context

**Language/Version**: Python 3.11+ (existing backend)
**Primary Dependencies**: OpenAI Agents SDK (`openai-agents`), existing MCP tools, FastAPI (existing)
**Storage**: Neon PostgreSQL via SQLModel ORM (no new schema - uses existing Task and Reminder entities)
**Testing**: pytest with mocked OpenAI API calls
**Target Platform**: Linux server (existing backend infrastructure)
**Project Type**: Web application - backend extension
**Performance Goals**: <5 seconds response time per agent invocation
**Constraints**: Stateless per invocation, no conversation persistence, no frontend integration
**Scale/Scope**: Single agent, 6 function tools, ~550 lines new code

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Implementation |
|-----------|--------|----------------|
| I. Security by Default | ✅ PASS | user_id passed via context, tools scope by user |
| II. Separation of Concerns | ✅ PASS | Agent → Tools → MCP → Database layers |
| III. RESTful API Design | ⬜ N/A | No API endpoint in this phase |
| IV. Data Integrity and Ownership | ✅ PASS | All operations via MCP tools with user scoping |
| V. Error Handling Standards | ✅ PASS | Tool errors translated to user-friendly messages |
| VI. Frontend Standards | ⬜ N/A | No frontend in this phase |
| VII. Spec-Driven Development | ✅ PASS | Implementation follows spec requirements |

**Gate Status**: ✅ PASSED - All applicable principles satisfied

## Project Structure

### Documentation (this feature)

```text
specs/008-ai-agent-mcp-orchestration/
├── plan.md              # This file
├── research.md          # Phase 0 output (completed)
├── data-model.md        # Phase 1 output (completed)
├── quickstart.md        # Phase 1 output (completed)
└── tasks.md             # Phase 2 output (via /sp.tasks command)
```

### Source Code (repository root)

```text
backend/
├── src/
│   ├── agent/                    # NEW: AI Agent layer
│   │   ├── __init__.py          # Module exports
│   │   ├── context.py           # UserContext dataclass
│   │   ├── tools.py             # Function tool wrappers for MCP tools
│   │   ├── prompts.py           # System prompt constants
│   │   ├── agent.py             # Task management agent definition
│   │   └── runner.py            # Agent execution utilities
│   └── mcp/                      # EXISTING: MCP tools (from Phase 2)
│       ├── tools/
│       │   ├── add_task.py
│       │   ├── list_tasks.py
│       │   ├── complete_task.py
│       │   ├── delete_task.py
│       │   └── update_task.py
│       ├── schemas.py
│       ├── errors.py
│       └── server.py
└── tests/
    └── agent/                    # NEW: Agent test suite
        ├── __init__.py
        ├── conftest.py          # Fixtures for agent testing
        ├── test_context.py      # UserContext tests
        ├── test_tools.py        # Function tool tests
        ├── test_agent.py        # Agent definition tests
        └── test_integration.py  # End-to-end agent tests
```

**Structure Decision**: Extend existing web application backend structure with new `agent/` module that sits above the MCP layer and orchestrates tool invocations.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                     Agent Orchestration Layer                        │
│                        (NEW - This Feature)                          │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│   User Input          ┌───────────────────────┐                     │
│   (natural language)  │   Task Management     │                     │
│         │             │       Agent           │                     │
│         │             │   (OpenAI Agents SDK) │                     │
│         ▼             └───────────┬───────────┘                     │
│   ┌───────────┐                   │                                 │
│   │  User     │◀──────────────────┤                                 │
│   │  Context  │                   │                                 │
│   │ (user_id) │                   ▼                                 │
│   └───────────┘       ┌───────────────────────┐                     │
│                       │    Function Tools     │                     │
│                       │ ┌─────┬─────┬─────┐   │                     │
│                       │ │add  │list │compl│   │                     │
│                       │ ├─────┼─────┼─────┤   │                     │
│                       │ │del  │updt │     │   │                     │
│                       │ └─────┴─────┴─────┘   │                     │
│                       └───────────┬───────────┘                     │
│                                   │                                 │
├───────────────────────────────────┼─────────────────────────────────┤
│                                   ▼                                 │
│   ┌───────────────────────────────────────────────────────────────┐ │
│   │                    MCP Tool Layer (EXISTING)                  │ │
│   │   add_task | list_tasks | complete_task | delete_task | ...   │ │
│   └───────────────────────────────────────────────────────────────┘ │
│                                   │                                 │
│                                   ▼                                 │
│   ┌───────────────────────────────────────────────────────────────┐ │
│   │              Database Layer (EXISTING - Neon PostgreSQL)       │ │
│   └───────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────┘
```

## Implementation Phases

### Phase 1: Core Agent Infrastructure

**Goal**: Set up agent module structure and context management

**Deliverables**:
1. `src/agent/__init__.py` - Module exports
2. `src/agent/context.py` - UserContext dataclass
3. Basic test fixtures in `tests/agent/conftest.py`

### Phase 2: Function Tool Implementation

**Goal**: Create wrapper tools that invoke MCP tools

**Deliverables**:
1. `src/agent/tools.py` - Six function tools wrapping MCP tools
2. `tests/agent/test_tools.py` - Tool unit tests

**Tool Mapping**:

| Function Tool | MCP Tool Called | Description |
|---------------|-----------------|-------------|
| add_task_tool | add_task | Create new task |
| list_tasks_tool | list_tasks | Retrieve all user tasks |
| complete_task_tool | complete_task | Mark task as complete |
| delete_task_tool | delete_task | Remove task |
| update_task_tool | update_task | Modify task fields |
| schedule_reminder_tool | schedule_reminder | Schedule task reminder |

### Phase 3: Agent Definition

**Goal**: Define the Task Management Agent with system prompt

**Deliverables**:
1. `src/agent/prompts.py` - System prompt constants
2. `src/agent/agent.py` - Agent instantiation with tools
3. `tests/agent/test_agent.py` - Agent definition tests

**System Prompt Structure**:
```
Role: Task management assistant
Capabilities: Create, list, complete, delete, update tasks, schedule reminders
Rules:
  - Always use tools for operations
  - Ask for clarification when ambiguous
  - Confirm actions with relevant details
  - Handle errors gracefully
  - Decline non-task requests politely
```

### Phase 4: Agent Runner

**Goal**: Provide utilities for executing the agent

**Deliverables**:
1. `src/agent/runner.py` - Run function wrapper
2. `tests/agent/test_integration.py` - End-to-end tests

### Phase 5: Documentation and Examples

**Goal**: Document agent usage and provide examples

**Deliverables**:
1. Update quickstart.md with real code examples
2. Add docstrings to all modules
3. Create example script demonstrating agent usage

## Key Design Decisions

### Decision 1: Single-Agent Architecture

**Choice**: One task-management agent (no multi-agent handoffs)

**Rationale**:
- Feature scope limited to 5 CRUD operations
- All operations share same context (user_id)
- Multi-agent adds complexity without benefit
- Spec explicitly excludes multi-agent workflows

**Alternative Rejected**: Specialist agents per operation

### Decision 2: Tool-First Reasoning

**Choice**: Agent uses LLM to select tools; no prompt-based logic execution

**Rationale**:
- OpenAI Agents SDK optimized for tool selection
- Business logic lives in MCP tools (separation of concerns)
- Agent focuses on intent interpretation, not business rules
- Consistent with spec requirement FR-008 (no direct DB access)

**Alternative Rejected**: Agent with inline business logic

### Decision 3: Synchronous Execution

**Choice**: Use `Runner.run_sync()` for Phase 3

**Rationale**:
- No streaming requirements in spec
- Simplifies testing and debugging
- Phase 4 can switch to async if needed
- Operations complete within 5-second target

**Alternative Rejected**: Async from start

### Decision 4: List-First Task Resolution

**Choice**: For ambiguous task references, agent first lists tasks then matches

**Rationale**:
- Users reference tasks by title, not UUID
- Agent can use list_tasks result for matching
- Enables fuzzy matching via LLM reasoning
- Avoids need for search/filter MCP tool

**Alternative Rejected**: Require exact task IDs in commands

### Decision 5: Error Translation at Tool Level

**Choice**: Function tools translate MCP errors to user-friendly strings

**Rationale**:
- Agent receives string output, includes in response
- Hides internal error codes from users
- Consistent error format across all tools
- Agent can add context to error messages

**Alternative Rejected**: Pass structured errors to agent

## Dependencies

### New Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| openai-agents | Latest | OpenAI Agents SDK framework |

### Existing Dependencies (Used)

| Package | Purpose |
|---------|---------|
| structlog | Logging tool invocations |
| pydantic | Validation in context |

### Internal Dependencies

| Component | Location | Usage |
|-----------|----------|-------|
| add_task | src/mcp/tools/add_task.py | Called by add_task_tool |
| list_tasks | src/mcp/tools/list_tasks.py | Called by list_tasks_tool |
| complete_task | src/mcp/tools/complete_task.py | Called by complete_task_tool |
| delete_task | src/mcp/tools/delete_task.py | Called by delete_task_tool |
| update_task | src/mcp/tools/update_task.py | Called by update_task_tool |
| schedule_reminder | src/mcp/tools/schedule_reminder.py | Called by schedule_reminder_tool |

## Environment Configuration

```bash
# Required
OPENAI_API_KEY=sk-...           # OpenAI API access

# Optional
OPENAI_DEFAULT_MODEL=gpt-4o     # Model selection (default: gpt-4o)

# Existing (from prior phases)
DATABASE_URL=postgresql://...    # Database connection
BETTER_AUTH_SECRET=...           # JWT verification
```

## Testing Strategy

### Unit Tests

| Test File | Scope |
|-----------|-------|
| test_context.py | UserContext validation |
| test_tools.py | Each function tool with mocked MCP |

### Integration Tests

| Test File | Scope |
|-----------|-------|
| test_agent.py | Agent creation and tool registration |
| test_integration.py | End-to-end with real MCP tools |

### Test Categories

1. **Intent Classification**: Verify correct tool selected for each intent
2. **Parameter Extraction**: Verify title/description extracted correctly
3. **Error Handling**: Verify graceful responses for tool errors
4. **Ambiguity Handling**: Verify clarification requests

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| OpenAI API rate limits | Medium | High | Implement retry logic, document limits |
| LLM misinterprets intent | Medium | Medium | Clear system prompt, test extensively |
| Tool invocation failures | Low | Medium | Robust error handling in function tools |
| Context propagation bugs | Low | High | Unit tests for context passing |

## Success Metrics

Mapped from spec Success Criteria:

| Metric | Target | Measurement |
|--------|--------|-------------|
| Intent accuracy | 95% | Test suite pass rate |
| Tool selection | 100% | Test suite pass rate |
| Response time | <5s | Benchmarks |
| Error handling | 100% | Test coverage |
| Code coverage | >80% | pytest-cov |

## Complexity Tracking

> **No complexity violations identified**

This implementation:
- Uses existing MCP tools (no duplication)
- Single agent (no unnecessary multi-agent)
- Synchronous execution (simplest for requirements)
- Standard patterns from OpenAI Agents SDK

## Next Steps

1. Run `/sp.tasks` to generate tasks.md with implementation tasks
2. Implement Phase 1 (context module)
3. Implement Phase 2 (function tools)
4. Implement Phase 3 (agent definition)
5. Implement Phase 4 (runner utilities)
6. Write comprehensive tests
7. Document and create examples
