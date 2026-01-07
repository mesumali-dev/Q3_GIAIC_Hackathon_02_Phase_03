# Data Model: AI Agent & MCP Tool Orchestration

**Feature**: 008-ai-agent-mcp-orchestration
**Phase**: Phase 1 - Design
**Created**: 2026-01-08

## Overview

This feature introduces AI agent components that orchestrate MCP tools. No new database entities are required - the agent layer uses existing Task entities via MCP tools. This document defines the runtime data structures for agent execution.

---

## 1. UserContext

**Purpose**: Runtime context passed to the agent containing authenticated user information.

**Type**: Python Dataclass

```python
@dataclass
class UserContext:
    """Context for agent execution containing authenticated user info.

    This context is passed to the agent runner and made available to all
    function tools via RunContextWrapper[UserContext].
    """
    user_id: str  # UUID string from authenticated JWT
```

**Fields**:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| user_id | str | Yes | UUID string identifying the authenticated user |

**Validation**:
- `user_id` MUST be a valid UUID v4 string format
- Empty or whitespace-only `user_id` is invalid

**Lifecycle**:
- Created once per agent invocation
- Immutable during agent execution
- Discarded after agent run completes

---

## 2. AgentConfig (Design-Time Entity)

**Purpose**: Configuration for the Task Management Agent definition.

**Type**: Static Configuration (not persisted)

```python
AGENT_CONFIG = {
    "name": "TaskManager",
    "model": "gpt-4o",  # Or from OPENAI_DEFAULT_MODEL env
    "instructions": "...",  # System prompt
    "tools": [
        "add_task_tool",
        "list_tasks_tool",
        "complete_task_tool",
        "delete_task_tool",
        "update_task_tool",
        "schedule_reminder_tool",
    ]
}
```

**Fields**:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| name | str | Yes | Agent identifier: "TaskManager" |
| model | str | No | LLM model to use (default: gpt-4o) |
| instructions | str | Yes | System prompt defining agent behavior |
| tools | list[Tool] | Yes | Registered function tools |

---

## 3. Function Tool Definitions

Each function tool wraps an MCP tool call and returns a string response.

### 3.1 add_task_tool

**Input Parameters**:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| ctx | RunContextWrapper[UserContext] | Yes | Injected context with user_id |
| title | str | Yes | Task title (1-200 chars) |
| description | str | None | No | Optional description (max 1000 chars) |

**Output**: `str` - Confirmation message or error description

**MCP Tool Called**: `add_task`

### 3.2 list_tasks_tool

**Input Parameters**:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| ctx | RunContextWrapper[UserContext] | Yes | Injected context with user_id |

**Output**: `str` - Formatted task list or empty message

**MCP Tool Called**: `list_tasks`

### 3.3 complete_task_tool

**Input Parameters**:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| ctx | RunContextWrapper[UserContext] | Yes | Injected context with user_id |
| task_id | str | Yes | UUID of task to complete |

**Output**: `str` - Confirmation or error message

**MCP Tool Called**: `complete_task`

### 3.4 delete_task_tool

**Input Parameters**:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| ctx | RunContextWrapper[UserContext] | Yes | Injected context with user_id |
| task_id | str | Yes | UUID of task to delete |

**Output**: `str` - Confirmation or error message

**MCP Tool Called**: `delete_task`

### 3.5 update_task_tool

**Input Parameters**:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| ctx | RunContextWrapper[UserContext] | Yes | Injected context with user_id |
| task_id | str | Yes | UUID of task to update |
| title | str | None | No | New title (optional) |
| description | str | None | No | New description (optional) |

**Output**: `str` - Confirmation or error message

**MCP Tool Called**: `update_task`

### 3.6 schedule_reminder_tool

**Input Parameters**:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| ctx | RunContextWrapper[UserContext] | Yes | Injected context with user_id |
| task_id | str | Yes | UUID of task to set reminder for |
| remind_at | str | Yes | ISO 8601 datetime string for reminder |
| repeat_interval_minutes | int | None | No | Minutes between repeats (max 1440) |
| repeat_count | int | None | No | Total times to repeat (max 100) |

**Output**: `str` - Confirmation with reminder details or error message

**MCP Tool Called**: `schedule_reminder`

---

## 4. AgentResponse

**Purpose**: Result from running the agent with user input.

**Type**: OpenAI Agents SDK `RunResult`

```python
class RunResult:
    final_output: str  # Agent's response text
    # ... other SDK fields
```

**Usage**:
```python
result = Runner.run_sync(agent, user_input, context=context)
response_text = result.final_output
```

---

## 5. MCP Tool Response Contracts

The agent function tools process MCP tool responses and translate them to user-friendly strings.

### Success Response Pattern

```json
{
  "success": true,
  "task_id": "uuid-string",
  "title": "Task title",
  ...
}
```

**Translation**: `"Created task 'Task title' (ID: uuid-string)"`

### Error Response Pattern

```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error"
  }
}
```

**Translation**: `"Error: Human-readable error"`

### List Response Pattern

```json
{
  "success": true,
  "tasks": [...],
  "count": 5
}
```

**Translation**:
```
You have 5 tasks:
1. [✓] Task One (ID: abc)
2. [ ] Task Two (ID: def)
...
```

---

## 6. Entity Relationships

```
┌─────────────────────────────────────────────────────────────────────┐
│                        Agent Runtime Layer                          │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌─────────────┐     ┌──────────────────┐     ┌──────────────┐     │
│  │ UserContext │────▶│ Task Management  │────▶│ Function     │     │
│  │ (user_id)   │     │ Agent            │     │ Tools        │     │
│  └─────────────┘     └──────────────────┘     └──────────────┘     │
│                              │                       │              │
│                              │                       │              │
│                              ▼                       ▼              │
│                     ┌──────────────────┐   ┌──────────────────┐    │
│                     │ Runner.run_sync  │   │ MCP Tools        │    │
│                     └──────────────────┘   │ (existing)       │    │
│                              │             └──────────────────┘    │
│                              ▼                       │              │
│                     ┌──────────────────┐             │              │
│                     │ RunResult        │             ▼              │
│                     │ (final_output)   │   ┌──────────────────┐    │
│                     └──────────────────┘   │ Database (Task)  │    │
│                                            └──────────────────┘    │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 7. State Machine

The agent is stateless per invocation. Each run follows this flow:

```
┌──────────┐
│  START   │
└────┬─────┘
     │
     ▼
┌──────────────────┐
│ Receive Input    │
│ + UserContext    │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ Agent Interprets │
│ User Intent      │
└────────┬─────────┘
         │
    ┌────┴────┐
    │         │
    ▼         ▼
┌────────┐ ┌─────────────┐
│ Clear  │ │ Ambiguous   │
│ Intent │ │ Intent      │
└───┬────┘ └──────┬──────┘
    │             │
    ▼             ▼
┌────────────┐ ┌─────────────────┐
│ Invoke     │ │ Request         │
│ Tool(s)    │ │ Clarification   │
└─────┬──────┘ └────────┬────────┘
      │                 │
      ▼                 │
┌────────────┐          │
│ Format     │◀─────────┘
│ Response   │
└─────┬──────┘
      │
      ▼
┌──────────┐
│   END    │
│ (output) │
└──────────┘
```

---

## 8. Validation Rules

### UserContext Validation

| Rule | Enforcement |
|------|-------------|
| user_id is valid UUID | Validated at context creation |
| user_id is not empty | Validated at context creation |

### Tool Input Validation

| Tool | Validation | Error |
|------|------------|-------|
| add_task_tool | title required, 1-200 chars | VALIDATION_ERROR |
| list_tasks_tool | (none) | - |
| complete_task_tool | task_id is valid UUID | VALIDATION_ERROR |
| delete_task_tool | task_id is valid UUID | VALIDATION_ERROR |
| update_task_tool | At least one field provided | VALIDATION_ERROR |
| schedule_reminder_tool | task_id valid UUID, remind_at valid ISO 8601 | VALIDATION_ERROR |

---

## 9. No Database Schema Changes

This feature does not modify the database schema. All data operations use existing:

- **Task** entity (from Phase 2)
- **User** entity (from Phase 1)
- **Reminder** entity (from Phase 5 - task reminders feature)

The agent layer is purely a runtime orchestration layer.
