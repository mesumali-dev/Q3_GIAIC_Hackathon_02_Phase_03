# Quickstart: AI Agent & MCP Tool Orchestration

**Feature**: 008-ai-agent-mcp-orchestration
**Phase**: Implementation Complete
**Created**: 2026-01-08
**Status**: ✅ Implemented with 68 passing tests

## Overview

This guide walks through setting up and running the Task Management AI Agent for development and testing.

---

## Prerequisites

- Python 3.11+ installed
- Backend from Phase 2 running with MCP tools
- OpenAI API key with access to GPT-4 models
- `uv` package manager installed

---

## 1. Install Dependencies

```bash
cd backend

# Add OpenAI Agents SDK
uv add openai-agents

# Sync all dependencies
uv sync
```

---

## 2. Configure Environment

Add to your `.env` file:

```bash
# OpenAI Configuration
OPENAI_API_KEY=sk-your-api-key-here
OPENAI_DEFAULT_MODEL=gpt-4o  # Optional, defaults to gpt-4o

# Existing variables (should already be configured)
DATABASE_URL=postgresql://...
BETTER_AUTH_SECRET=...
```

---

## 3. Project Structure

After implementation, the agent code will be organized as:

```
backend/
├── src/
│   ├── agent/                    # NEW: Agent layer
│   │   ├── __init__.py
│   │   ├── context.py           # UserContext dataclass
│   │   ├── tools.py             # Function tool wrappers
│   │   ├── prompts.py           # System prompt constants
│   │   ├── agent.py             # Agent definition
│   │   └── runner.py            # Agent execution utilities
│   └── mcp/                      # EXISTING: MCP tools
│       ├── tools/
│       │   ├── add_task.py
│       │   ├── list_tasks.py
│       │   ├── complete_task.py
│       │   ├── delete_task.py
│       │   └── update_task.py
│       └── ...
└── tests/
    └── agent/                    # NEW: Agent tests
        ├── test_tools.py
        ├── test_agent.py
        └── test_integration.py
```

---

## 4. Basic Usage

### Running the Agent Programmatically

**Method 1: Using the runner helper (recommended)**

```python
from src.agent import run_agent

# Synchronous version
response = run_agent(
    user_input="Add a task called 'Buy groceries' with description 'Milk, eggs, bread'",
    user_id="550e8400-e29b-41d4-a716-446655440000"
)
print(response)
# Output: Created task 'Buy groceries' (ID: abc123-...)
```

**Method 2: Using async runner**

```python
from src.agent import run_agent_async
import asyncio

async def main():
    response = await run_agent_async(
        user_input="Show my tasks",
        user_id="550e8400-e29b-41d4-a716-446655440000"
    )
    print(response)

asyncio.run(main())
```

**Method 3: Direct agent access**

```python
from src.agent import task_agent, UserContext
from agents import Runner

# Create user context (normally from JWT)
context = UserContext(user_id="550e8400-e29b-41d4-a716-446655440000")

# Run agent with natural language input
result = Runner.run_sync(
    task_agent,
    "Add a task called 'Buy groceries' with description 'Milk, eggs, bread'",
    context=context
)

# Get agent response
print(result.final_output)
# Output: Created task 'Buy groceries' (ID: abc123-...)
```

### Example Conversations

**Creating a Task**:
```
Input:  "Create a task to call mom tomorrow"
Output: "Created task 'call mom tomorrow' (ID: 550e8400-...)"
```

**Listing Tasks**:
```
Input:  "What tasks do I have?"
Output: "You have 3 tasks:
         1. [ ] Buy groceries (ID: abc...)
         2. [✓] Call mom (ID: def...)
         3. [ ] Finish report (ID: ghi...)"
```

**Completing a Task**:
```
Input:  "Mark 'Buy groceries' as done"
Output: "Marked 'Buy groceries' as complete."
```

**Deleting a Task**:
```
Input:  "Delete the groceries task"
Output: "Deleted task 'Buy groceries'."
```

**Updating a Task**:
```
Input:  "Change 'Finish report' to 'Finish quarterly report'"
Output: "Updated task title to 'Finish quarterly report'."
```

**Scheduling a Reminder**:
```
Input:  "Remind me about 'Buy groceries' tomorrow at 9am"
Output: "Reminder set for 'Buy groceries' at 2026-01-09T09:00:00Z."
```

**Scheduling a Repeating Reminder**:
```
Input:  "Remind me about 'Take medication' every day at 8am for a week"
Output: "Reminder set for 'Take medication' at 2026-01-09T08:00:00Z, repeating every 1440 minutes, 7 times."
```

---

## 5. Running Tests

```bash
cd backend

# Run all agent tests
uv run pytest tests/agent/ -v

# Run specific test file
uv run pytest tests/agent/test_tools.py -v

# Run with coverage
uv run pytest tests/agent/ --cov=src/agent
```

---

## 6. Development Workflow

### Step 1: Implement Context Module
```bash
# Create src/agent/context.py
# Define UserContext dataclass
```

### Step 2: Implement Function Tools
```bash
# Create src/agent/tools.py
# Wrap each MCP tool with @function_tool
```

### Step 3: Define System Prompt
```bash
# Create src/agent/prompts.py
# Write agent instructions
```

### Step 4: Create Agent Definition
```bash
# Create src/agent/agent.py
# Instantiate Agent with tools and instructions
```

### Step 5: Create Runner Utilities
```bash
# Create src/agent/runner.py
# Provide convenient run function
```

### Step 6: Write Tests
```bash
# Create tests/agent/
# Test each component
```

---

## 7. Debugging

### Enable Verbose Logging

```python
import structlog
structlog.configure(
    wrapper_class=structlog.make_filtering_bound_logger(10),  # DEBUG level
)
```

### Check Tool Invocations

The agent logs tool calls via structlog:
```
[INFO] mcp_tool_invocation tool=add_task user_id=... title_length=13
[INFO] mcp_tool_success tool=add_task task_id=...
```

### Test Agent Without Real API

Mock the OpenAI client for unit tests:
```python
from unittest.mock import patch

with patch('agents.Runner.run_sync') as mock_run:
    mock_run.return_value.final_output = "Mocked response"
    # Test code
```

---

## 8. Common Issues

### "OPENAI_API_KEY not set"
- Ensure `.env` file exists with `OPENAI_API_KEY=sk-...`
- Run `source .env` or restart your terminal

### "Module 'agents' not found"
- Run `uv add openai-agents && uv sync`

### "Task not found" errors
- Ensure database is running and seeded
- Check that user_id matches existing tasks

### Agent responds with unrelated content
- Review system prompt for clarity
- Ensure tools are correctly registered

---

## 9. Next Steps

After completing this phase:

1. **Phase 4**: Wrap agent in stateless chat API endpoint
2. **Phase 5**: Add conversation history via sessions
3. **Future**: Add streaming support for real-time responses

---

## 10. Reference Links

- [OpenAI Agents SDK Documentation](https://openai.github.io/openai-agents-python/)
- [MCP Tools Spec (007-mcp-stateless-tools)](../007-mcp-stateless-tools/spec.md)
- [Project Constitution](../../.specify/memory/constitution.md)
