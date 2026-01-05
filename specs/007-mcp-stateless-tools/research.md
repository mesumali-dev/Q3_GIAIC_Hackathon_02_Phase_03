# Research: MCP SDK Integration and Stateless Tool Implementation

**Feature**: 007-mcp-stateless-tools
**Phase**: Phase 0 - Research
**Date**: 2026-01-05

## Overview

This document consolidates research findings for implementing a stateless MCP server using the Official MCP SDK to expose task operations as tools for AI agent consumption.

## 1. MCP SDK Selection and Integration

### Decision: Use Official MCP Python SDK

**Package**: `mcp` (Official Model Context Protocol SDK for Python)

**Rationale**:
- Official implementation from Anthropic
- Native Python support (matches existing backend stack)
- Built-in support for tool definitions and execution
- Server/client architecture suitable for stateless operation
- Active maintenance and documentation

**Alternatives Considered**:
1. **Custom MCP Implementation**
   - **Rejected**: Higher complexity, maintenance burden, potential protocol drift
   - Would require implementing full MCP protocol specification
   - No benefit over official SDK for standard tool operations

2. **HTTP-based Custom API**
   - **Rejected**: MCP provides standardized protocol for AI agent interaction
   - MCP SDK handles protocol details, error formatting, and client compatibility
   - Custom API would require bespoke client implementations

**Installation**:
```bash
uv add mcp
```

**Version**: Latest stable (check pypi.org/project/mcp for current version)

## 2. MCP Server Architecture

### Decision: Standalone MCP Server Process

**Approach**: Separate MCP server from FastAPI server

**Rationale**:
- MCP server and FastAPI server serve different clients (AI agents vs web frontend/API consumers)
- Independent lifecycle management (can start/stop MCP server without affecting API)
- Clear separation of concerns (principle II from constitution)
- Different protocols (MCP vs HTTP REST)

**Implementation Pattern**:
```python
# backend/src/mcp/server.py
from mcp.server import Server
from mcp.server.stdio import stdio_server

async def main():
    server = Server("todo-mcp-server")

    # Register tools
    # ... tool registrations

    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream)
```

**Communication**: Standard input/output (stdio) transport
- MCP SDK provides `stdio_server()` for process-based communication
- AI agents/clients launch MCP server as subprocess and communicate via stdin/stdout
- No network ports required (simpler deployment, no port conflicts)

**Alternatives Considered**:
1. **Embedded in FastAPI Server**
   - **Rejected**: Mixing HTTP and MCP protocols in single process
   - Increases coupling between web API and MCP tool layer
   - Violates separation of concerns

2. **HTTP Transport for MCP**
   - **Rejected**: stdio transport is MCP standard for local tool servers
   - No need for network transport in Phase 2 (agent integration is Phase 3)
   - Can add HTTP transport later if needed for remote agents

## 3. Tool Implementation Pattern

### Decision: Stateless Tool Functions with Service Layer Delegation

**Pattern**: Each MCP tool is a thin wrapper around existing service layer

**Structure**:
```python
# backend/src/mcp/tools/add_task.py
from mcp.server import Server
from src.services.task_service import create_task
from src.mcp.schemas import AddTaskInput, AddTaskOutput
from src.mcp.errors import handle_tool_error

@server.tool()
async def add_task(user_id: str, title: str, description: str | None = None) -> dict:
    """
    Create a new task for a user.

    Args:
        user_id: Authenticated user UUID
        title: Task title (1-200 characters)
        description: Optional task description (max 1000 characters)

    Returns:
        dict with task_id, user_id, title, description, created_at
    """
    try:
        # Validate input
        input_data = AddTaskInput(user_id=user_id, title=title, description=description)

        # Delegate to service layer
        with get_db_session() as db:
            task = create_task(db, input_data.user_id, input_data)

        # Return structured output
        return AddTaskOutput.from_task(task).dict()

    except Exception as e:
        return handle_tool_error(e)
```

**Rationale**:
- Tools have no business logic (only validation, service delegation, output formatting)
- Reuses existing `task_service.py` functions (no duplication)
- Stateless: no tool-level state, all state in database
- Testable: can test tools independently with mocked service layer

**Key Principles**:
1. **Input Validation**: Pydantic schemas validate before service call
2. **Service Delegation**: All database operations via existing service layer
3. **Output Formatting**: Convert service results to MCP-compatible dicts
4. **Error Handling**: Structured error responses suitable for AI consumption

## 4. Error Handling Strategy

### Decision: Structured Error Responses with AI-Safe Messages

**Error Types**:
```python
# backend/src/mcp/errors.py

class MCPToolError(Exception):
    """Base class for MCP tool errors"""
    error_code: str
    user_message: str

class TaskNotFoundError(MCPToolError):
    error_code = "TASK_NOT_FOUND"
    user_message = "Task not found or access denied"

class ValidationError(MCPToolError):
    error_code = "VALIDATION_ERROR"
    user_message = "Invalid input parameters"

class AuthorizationError(MCPToolError):
    error_code = "AUTHORIZATION_ERROR"
    user_message = "User not authorized for this operation"

class DatabaseError(MCPToolError):
    error_code = "DATABASE_ERROR"
    user_message = "Database operation failed"
```

**Error Response Format**:
```json
{
  "success": false,
  "error": {
    "code": "TASK_NOT_FOUND",
    "message": "Task not found or access denied"
  }
}
```

**Rationale**:
- AI agents need structured, predictable error responses
- Error codes enable programmatic handling (retry logic, user messaging)
- User-safe messages (no stack traces, no internal details)
- Consistent format across all tools

**Error Mapping**:
- Service returns `None` → `TaskNotFoundError`
- Pydantic validation fails → `ValidationError`
- User mismatch → `AuthorizationError`
- Database exception → `DatabaseError`

## 5. Database Session Management

### Decision: Context Manager Per Tool Invocation

**Pattern**:
```python
from src.database import get_db_session

@server.tool()
async def list_tasks(user_id: str) -> dict:
    try:
        with get_db_session() as db:
            tasks = get_tasks(db, user_id)
        return {"success": True, "tasks": [task.dict() for task in tasks]}
    except Exception as e:
        return handle_tool_error(e)
```

**Rationale**:
- Each tool invocation gets fresh database session (stateless)
- Session automatically closed after tool execution
- Prevents session leakage and connection pool exhaustion
- Matches existing FastAPI endpoint pattern

**Alternatives Considered**:
1. **Long-lived Session**
   - **Rejected**: Violates stateless requirement
   - Risk of session state bleeding across tool calls
   - Connection pool exhaustion

2. **Dependency Injection**
   - **Rejected**: MCP SDK tool decorators don't support FastAPI-style dependencies
   - Would require custom middleware layer (unnecessary complexity)

## 6. Tool Schema Design

### Decision: Explicit Pydantic Schemas with JSON Schema Export

**Approach**: Define input/output schemas as Pydantic models, export to JSON Schema for MCP registration

**Example**:
```python
# backend/src/mcp/schemas.py
from pydantic import BaseModel, Field, UUID4

class AddTaskInput(BaseModel):
    user_id: UUID4 = Field(..., description="Authenticated user UUID")
    title: str = Field(..., min_length=1, max_length=200, description="Task title")
    description: str | None = Field(None, max_length=1000, description="Optional task description")

class AddTaskOutput(BaseModel):
    success: bool = True
    task_id: UUID4
    user_id: UUID4
    title: str
    description: str | None
    is_completed: bool
    created_at: str  # ISO 8601 format

    @classmethod
    def from_task(cls, task: Task):
        return cls(
            task_id=task.id,
            user_id=task.user_id,
            title=task.title,
            description=task.description,
            is_completed=task.is_completed,
            created_at=task.created_at.isoformat()
        )
```

**JSON Schema Export** (for `specs/007-mcp-stateless-tools/contracts/`):
```python
# Generate JSON schemas for documentation
AddTaskInput.schema_json(indent=2)  # → add_task.json
```

**Rationale**:
- Pydantic provides runtime validation (prevents invalid inputs)
- JSON Schema export documents tool contracts
- Type safety for tool implementations
- Consistent with existing FastAPI schema patterns

**Key Design Choices**:
1. **Explicit over Inferred**: All fields explicitly defined (no `**kwargs` or dynamic fields)
2. **UUID as String**: MCP tools receive UUIDs as strings, convert to UUID4 for validation
3. **ISO 8601 Dates**: Datetime fields serialized as ISO strings (AI-friendly, unambiguous)
4. **Flat Structures**: Avoid nested objects where possible (simpler for AI parsing)

## 7. Testing Strategy

### Decision: Direct Tool Invocation Tests

**Approach**: Test MCP tools by direct function calls with test database

**Test Structure**:
```python
# backend/tests/mcp/test_add_task.py
import pytest
from src.mcp.tools.add_task import add_task
from src.database import get_test_db_session

@pytest.fixture
def test_db():
    # Setup test database with test user
    with get_test_db_session() as db:
        yield db
    # Teardown

def test_add_task_success(test_db):
    """Test successful task creation"""
    result = add_task(
        user_id="550e8400-e29b-41d4-a716-446655440000",
        title="Test task",
        description="Test description"
    )

    assert result["success"] == True
    assert result["title"] == "Test task"
    assert "task_id" in result

def test_add_task_validation_error():
    """Test validation error for missing title"""
    result = add_task(
        user_id="550e8400-e29b-41d4-a716-446655440000",
        title="",  # Invalid: empty title
        description="Test"
    )

    assert result["success"] == False
    assert result["error"]["code"] == "VALIDATION_ERROR"
```

**Test Coverage**:
- ✅ Valid inputs (happy path)
- ✅ Invalid inputs (validation errors)
- ✅ Missing tasks (not found errors)
- ✅ Wrong user (authorization errors)
- ✅ Database errors (connection failures)

**Rationale**:
- Direct invocation simpler than full MCP client/server setup
- Tests business logic without protocol overhead
- Fast execution (no process spawning)
- Can add integration tests with MCP client later

## 8. MCP Server Configuration

### Decision: Environment-based Configuration

**Configuration**:
```python
# backend/src/mcp/server.py
import os

MCP_SERVER_NAME = os.getenv("MCP_SERVER_NAME", "todo-mcp-server")
MCP_SERVER_VERSION = os.getenv("MCP_SERVER_VERSION", "1.0.0")
```

**Environment Variables** (`.env`):
```bash
# MCP Server Configuration
MCP_SERVER_NAME=todo-mcp-server
MCP_SERVER_VERSION=1.0.0
```

**Rationale**:
- No hardcoded configuration (principle I: no secrets in code)
- Environment-specific settings (dev, staging, prod)
- Matches existing FastAPI configuration pattern

## 9. Logging and Observability

### Decision: Structured Logging for Tool Invocations

**Approach**: Log tool invocations with structured data

**Implementation**:
```python
import logging
import structlog

logger = structlog.get_logger(__name__)

@server.tool()
async def add_task(user_id: str, title: str, description: str | None = None) -> dict:
    logger.info(
        "mcp_tool_invocation",
        tool="add_task",
        user_id=user_id,
        title_length=len(title)
    )

    try:
        # ... tool logic
        logger.info("mcp_tool_success", tool="add_task", task_id=result["task_id"])
        return result
    except Exception as e:
        logger.error("mcp_tool_error", tool="add_task", error=str(e))
        raise
```

**Logged Data**:
- Tool name
- User ID (for scoping)
- Input parameters (excluding sensitive data)
- Execution outcome (success/error)
- Execution time

**Rationale**:
- Enables debugging of tool invocations
- Tracks usage patterns (which tools called most often)
- Identifies performance bottlenecks
- Structured logs parseable by log aggregation tools

## 10. Phase 3 Preparation

### Decision: Clean Tool Interfaces for Agent Integration

**Agent Integration Points** (Phase 3):
```python
# Future: OpenAI Agents SDK will invoke MCP tools like this
from openai import Agent

agent = Agent(
    tools=[
        MCPTool(server_command="python -m src.mcp.server"),
    ]
)

# Agent uses natural language to determine which tool to call
response = agent.run("Add a task to buy groceries")
# Agent invokes: add_task(user_id="...", title="Buy groceries")
```

**Interface Design Principles**:
1. **Descriptive Tool Names**: `add_task` not `create` (clear intent)
2. **Clear Parameter Names**: `user_id` not `uid` (unambiguous)
3. **Self-documenting**: Docstrings explain purpose and constraints
4. **Consistent Patterns**: All tools follow same input/output structure

**Preparation Work**:
- Tool contracts documented in JSON schemas
- Example invocation payloads in `quickstart.md`
- Error handling ready for agent consumption
- No agent-specific logic in Phase 2 (added in Phase 3)

## Research Summary

All Technical Context NEEDS CLARIFICATION items resolved:

1. ✅ **MCP SDK**: Official Python MCP SDK selected
2. ✅ **Server Architecture**: Standalone process with stdio transport
3. ✅ **Tool Pattern**: Stateless wrappers around service layer
4. ✅ **Error Handling**: Structured responses with AI-safe messages
5. ✅ **Database Sessions**: Context manager per invocation
6. ✅ **Schemas**: Explicit Pydantic models with JSON Schema export
7. ✅ **Testing**: Direct tool invocation with test database
8. ✅ **Configuration**: Environment-based settings
9. ✅ **Logging**: Structured logging for observability
10. ✅ **Agent Prep**: Clean interfaces for Phase 3 integration

**Next Phase**: Generate data-model.md and tool contracts (Phase 1)
