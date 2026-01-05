# Quickstart Guide: MCP Server Setup and Testing

**Feature**: 007-mcp-stateless-tools
**Phase**: Phase 1 - Design
**Date**: 2026-01-05

## Overview

This guide explains how to set up, run, and test the MCP server for the AI-Native Todo application. The MCP server exposes five stateless tools for task management operations.

## Prerequisites

- Python 3.11+
- uv package manager installed
- Neon PostgreSQL database configured (from Phase 1)
- Backend dependencies installed (`uv sync`)

## Installation

### 1. Install MCP SDK

```bash
cd backend
uv add mcp
```

### 2. Verify Installation

```bash
uv run python -c "import mcp; print(mcp.__version__)"
```

## Project Structure

```
backend/
├── src/
│   ├── mcp/
│   │   ├── __init__.py          # MCP module init
│   │   ├── server.py            # MCP server entry point
│   │   ├── tools/               # Tool implementations
│   │   │   ├── __init__.py
│   │   │   ├── add_task.py
│   │   │   ├── list_tasks.py
│   │   │   ├── complete_task.py
│   │   │   ├── delete_task.py
│   │   │   └── update_task.py
│   │   ├── schemas.py           # Pydantic input/output models
│   │   └── errors.py            # Error handling
│   ├── services/                # Existing service layer
│   ├── models/                  # Existing data models
│   └── database.py              # Existing DB connection
```

## Running the MCP Server

### Development Mode

```bash
# From backend directory
uv run python -m src.mcp.server
```

The server runs in stdio mode (reads from stdin, writes to stdout).

### Production Mode

```bash
# Run as subprocess (typically launched by AI agent/client)
python -m src.mcp.server
```

## Testing the MCP Tools

### Unit Tests

Run the MCP tool test suite:

```bash
# From backend directory
uv run pytest tests/mcp/ -v
```

### Test Individual Tools

```bash
# Test add_task tool
uv run pytest tests/mcp/test_add_task.py -v

# Test list_tasks tool
uv run pytest tests/mcp/test_list_tasks.py -v

# Test complete_task tool
uv run pytest tests/mcp/test_complete_task.py -v

# Test delete_task tool
uv run pytest tests/mcp/test_delete_task.py -v

# Test update_task tool
uv run pytest tests/mcp/test_update_task.py -v
```

### Manual Tool Invocation (Python REPL)

For manual testing, you can invoke tools directly:

```python
# Start Python REPL
uv run python

# Import tool functions
from src.mcp.tools.add_task import add_task
from src.mcp.tools.list_tasks import list_tasks

# Test add_task
result = add_task(
    user_id="550e8400-e29b-41d4-a716-446655440000",
    title="Test task",
    description="Testing MCP tool"
)
print(result)

# Test list_tasks
tasks = list_tasks(user_id="550e8400-e29b-41d4-a716-446655440000")
print(tasks)
```

## Tool Usage Examples

### 1. add_task - Create New Task

**Input**:
```python
{
    "user_id": "550e8400-e29b-41d4-a716-446655440000",
    "title": "Buy groceries",
    "description": "Milk, eggs, bread"
}
```

**Output (Success)**:
```python
{
    "success": True,
    "task_id": "7c9e6679-7425-40de-944b-e07fc1f90ae7",
    "user_id": "550e8400-e29b-41d4-a716-446655440000",
    "title": "Buy groceries",
    "description": "Milk, eggs, bread",
    "is_completed": False,
    "created_at": "2026-01-05T14:30:00.123456Z",
    "updated_at": "2026-01-05T14:30:00.123456Z"
}
```

**Output (Validation Error)**:
```python
{
    "success": False,
    "error": {
        "code": "VALIDATION_ERROR",
        "message": "Title is required and must be 1-200 characters"
    }
}
```

### 2. list_tasks - Retrieve All Tasks

**Input**:
```python
{
    "user_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

**Output**:
```python
{
    "success": True,
    "tasks": [
        {
            "task_id": "7c9e6679-7425-40de-944b-e07fc1f90ae7",
            "user_id": "550e8400-e29b-41d4-a716-446655440000",
            "title": "Buy groceries",
            "description": "Milk, eggs, bread",
            "is_completed": False,
            "created_at": "2026-01-05T14:30:00.123456Z",
            "updated_at": "2026-01-05T14:30:00.123456Z"
        }
    ],
    "count": 1
}
```

### 3. complete_task - Mark Task Complete

**Input**:
```python
{
    "user_id": "550e8400-e29b-41d4-a716-446655440000",
    "task_id": "7c9e6679-7425-40de-944b-e07fc1f90ae7"
}
```

**Output (Success)**:
```python
{
    "success": True,
    "task_id": "7c9e6679-7425-40de-944b-e07fc1f90ae7",
    "user_id": "550e8400-e29b-41d4-a716-446655440000",
    "title": "Buy groceries",
    "description": "Milk, eggs, bread",
    "is_completed": True,
    "created_at": "2026-01-05T14:30:00.123456Z",
    "updated_at": "2026-01-05T15:45:00.789012Z"
}
```

**Output (Not Found)**:
```python
{
    "success": False,
    "error": {
        "code": "TASK_NOT_FOUND",
        "message": "Task not found or access denied"
    }
}
```

### 4. delete_task - Delete Task

**Input**:
```python
{
    "user_id": "550e8400-e29b-41d4-a716-446655440000",
    "task_id": "7c9e6679-7425-40de-944b-e07fc1f90ae7"
}
```

**Output**:
```python
{
    "success": True,
    "task_id": "7c9e6679-7425-40de-944b-e07fc1f90ae7",
    "message": "Task deleted successfully"
}
```

### 5. update_task - Update Task

**Input**:
```python
{
    "user_id": "550e8400-e29b-41d4-a716-446655440000",
    "task_id": "7c9e6679-7425-40de-944b-e07fc1f90ae7",
    "title": "Buy groceries and supplies",
    "description": "Milk, eggs, bread, paper towels"
}
```

**Output**:
```python
{
    "success": True,
    "task_id": "7c9e6679-7425-40de-944b-e07fc1f90ae7",
    "user_id": "550e8400-e29b-41d4-a716-446655440000",
    "title": "Buy groceries and supplies",
    "description": "Milk, eggs, bread, paper towels",
    "is_completed": False,
    "created_at": "2026-01-05T14:30:00.123456Z",
    "updated_at": "2026-01-05T16:00:00.456789Z"
}
```

## Validation Testing

### Test Valid Inputs

```bash
# All tools should succeed with valid inputs
uv run pytest tests/mcp/ -k "test_success" -v
```

### Test Invalid Inputs

```bash
# Test validation error handling
uv run pytest tests/mcp/ -k "test_validation" -v
```

### Test Error Handling

```bash
# Test task not found, authorization errors
uv run pytest tests/mcp/ -k "test_error" -v
```

## Database Persistence Verification

After each tool invocation, verify database changes:

```python
# Connect to database
from src.database import get_db_session
from src.models import Task
from sqlmodel import select

with get_db_session() as db:
    # Verify task created
    task = db.exec(
        select(Task).where(Task.id == "7c9e6679-7425-40de-944b-e07fc1f90ae7")
    ).first()
    print(task)
```

## Stateless Operation Verification

### Test 1: Restart MCP Server

```bash
# 1. Start MCP server, create a task
# 2. Stop MCP server
# 3. Restart MCP server
# 4. List tasks - should retrieve previously created task
```

### Test 2: Concurrent Invocations

```bash
# Run multiple tool invocations in parallel
# Each should get independent database session
# No state should leak between calls
```

### Test 3: Execution Order Independence

```bash
# Tools can be called in any order
# No dependencies on previous calls
# Each call is self-contained
```

## Common Issues and Troubleshooting

### Issue: ModuleNotFoundError: No module named 'mcp'

**Solution**: Install MCP SDK
```bash
uv add mcp
```

### Issue: Database connection error

**Solution**: Verify `.env` file has correct database credentials
```bash
# Check .env file
cat .env | grep DATABASE_URL
```

### Issue: Validation errors for valid inputs

**Solution**: Check Pydantic schema definitions in `src/mcp/schemas.py`

### Issue: Task not found for valid task_id

**Solution**: Verify user_id matches task owner
```python
# Check task ownership
from src.database import get_db_session
from src.models import Task
from sqlmodel import select

with get_db_session() as db:
    task = db.exec(select(Task).where(Task.id == task_id)).first()
    print(f"Task owner: {task.user_id}")
```

## Performance Benchmarks

Expected performance (development environment):

- **add_task**: < 100ms
- **list_tasks** (10 tasks): < 100ms
- **list_tasks** (1000 tasks): < 1000ms
- **complete_task**: < 100ms
- **delete_task**: < 100ms
- **update_task**: < 100ms

Run performance tests:

```bash
uv run pytest tests/mcp/ -k "test_performance" -v
```

## AI Agent Integration (Phase 3 Preview)

In Phase 3, AI agents will invoke MCP tools like this:

```python
# OpenAI Agents SDK (Phase 3)
from openai import Agent

agent = Agent(
    tools=[
        MCPTool(server_command="python -m src.mcp.server"),
    ]
)

# Natural language request
response = agent.run("Add a task to buy groceries")

# Agent automatically:
# 1. Interprets user intent
# 2. Selects add_task tool
# 3. Extracts parameters (user_id from context, title from request)
# 4. Invokes add_task tool via MCP
# 5. Formats response for user
```

## Next Steps

1. ✅ Complete Phase 1: MCP tool implementation
2. ⏳ Run `/sp.tasks` to generate implementation tasks
3. ⏳ Implement MCP server and tools
4. ⏳ Run validation and performance tests
5. ⏳ Phase 3: Integrate with AI agents using OpenAI Agents SDK

## Documentation

- **Spec**: [spec.md](./spec.md)
- **Plan**: [plan.md](./plan.md)
- **Research**: [research.md](./research.md)
- **Data Model**: [data-model.md](./data-model.md)
- **Contracts**: [contracts/](./contracts/)

## Support

For issues or questions:
1. Check this quickstart guide
2. Review contract schemas in `contracts/`
3. Examine test cases in `tests/mcp/`
4. Consult spec and plan documents
