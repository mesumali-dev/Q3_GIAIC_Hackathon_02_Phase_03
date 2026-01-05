# Data Model: MCP Tool Schemas

**Feature**: 007-mcp-stateless-tools
**Phase**: Phase 1 - Design
**Date**: 2026-01-05

## Overview

This document defines the data contracts for all MCP tools. Each tool has explicit input and output schemas that define the interface between AI agents and the task management system.

## Core Principles

1. **Stateless**: No tool maintains state between invocations
2. **Explicit**: All parameters explicitly defined (no dynamic fields)
3. **Validated**: Pydantic schemas provide runtime validation
4. **AI-Friendly**: Simple, flat structures with clear field names
5. **Consistent**: All tools follow same success/error response pattern

## Common Types

### UUID Format

All UUIDs are represented as strings in MCP tool interfaces:

```
Format: "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
Example: "550e8400-e29b-41d4-a716-446655440000"
Validation: Must match UUID4 format
```

### Timestamp Format

All timestamps use ISO 8601 format:

```
Format: "YYYY-MM-DDTHH:MM:SS.ffffffZ"
Example: "2026-01-05T14:30:00.123456Z"
Timezone: Always UTC (Z suffix)
```

### Success Response Pattern

```json
{
  "success": true,
  "data": { /* tool-specific payload */ }
}
```

### Error Response Pattern

```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message"
  }
}
```

## Tool Schemas

### 1. add_task

**Purpose**: Create a new task for a user

**Input Schema**:

| Field | Type | Required | Validation | Description |
|-------|------|----------|------------|-------------|
| `user_id` | string (UUID) | Yes | Valid UUID4 | Authenticated user UUID |
| `title` | string | Yes | 1-200 chars | Task title |
| `description` | string | No | Max 1000 chars | Task description (optional) |

**Output Schema (Success)**:

| Field | Type | Description |
|-------|------|-------------|
| `success` | boolean | Always `true` |
| `task_id` | string (UUID) | Generated task UUID |
| `user_id` | string (UUID) | Owner user UUID |
| `title` | string | Task title |
| `description` | string \| null | Task description |
| `is_completed` | boolean | Always `false` (new tasks incomplete) |
| `created_at` | string (ISO 8601) | Creation timestamp |
| `updated_at` | string (ISO 8601) | Last update timestamp |

**Example Request**:
```json
{
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "title": "Buy groceries",
  "description": "Milk, eggs, bread"
}
```

**Example Response (Success)**:
```json
{
  "success": true,
  "task_id": "7c9e6679-7425-40de-944b-e07fc1f90ae7",
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "title": "Buy groceries",
  "description": "Milk, eggs, bread",
  "is_completed": false,
  "created_at": "2026-01-05T14:30:00.123456Z",
  "updated_at": "2026-01-05T14:30:00.123456Z"
}
```

**Error Codes**:
- `VALIDATION_ERROR`: Invalid user_id, empty title, or title too long
- `DATABASE_ERROR`: Database operation failed

---

### 2. list_tasks

**Purpose**: Retrieve all tasks for a user

**Input Schema**:

| Field | Type | Required | Validation | Description |
|-------|------|----------|------------|-------------|
| `user_id` | string (UUID) | Yes | Valid UUID4 | Authenticated user UUID |

**Output Schema (Success)**:

| Field | Type | Description |
|-------|------|-------------|
| `success` | boolean | Always `true` |
| `tasks` | array | Array of task objects (see below) |
| `count` | integer | Number of tasks returned |

**Task Object Structure**:

| Field | Type | Description |
|-------|------|-------------|
| `task_id` | string (UUID) | Task UUID |
| `user_id` | string (UUID) | Owner user UUID |
| `title` | string | Task title |
| `description` | string \| null | Task description |
| `is_completed` | boolean | Completion status |
| `created_at` | string (ISO 8601) | Creation timestamp |
| `updated_at` | string (ISO 8601) | Last update timestamp |

**Example Request**:
```json
{
  "user_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

**Example Response (Success)**:
```json
{
  "success": true,
  "tasks": [
    {
      "task_id": "7c9e6679-7425-40de-944b-e07fc1f90ae7",
      "user_id": "550e8400-e29b-41d4-a716-446655440000",
      "title": "Buy groceries",
      "description": "Milk, eggs, bread",
      "is_completed": false,
      "created_at": "2026-01-05T14:30:00.123456Z",
      "updated_at": "2026-01-05T14:30:00.123456Z"
    },
    {
      "task_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
      "user_id": "550e8400-e29b-41d4-a716-446655440000",
      "title": "Call dentist",
      "description": null,
      "is_completed": true,
      "created_at": "2026-01-04T10:15:00.000000Z",
      "updated_at": "2026-01-05T08:00:00.000000Z"
    }
  ],
  "count": 2
}
```

**Example Response (Empty)**:
```json
{
  "success": true,
  "tasks": [],
  "count": 0
}
```

**Error Codes**:
- `VALIDATION_ERROR`: Invalid user_id format
- `DATABASE_ERROR`: Database operation failed

---

### 3. complete_task

**Purpose**: Mark a task as complete (or toggle completion status)

**Input Schema**:

| Field | Type | Required | Validation | Description |
|-------|------|----------|------------|-------------|
| `user_id` | string (UUID) | Yes | Valid UUID4 | Authenticated user UUID |
| `task_id` | string (UUID) | Yes | Valid UUID4 | Task UUID to complete |

**Output Schema (Success)**:

| Field | Type | Description |
|-------|------|-------------|
| `success` | boolean | Always `true` |
| `task_id` | string (UUID) | Task UUID |
| `user_id` | string (UUID) | Owner user UUID |
| `title` | string | Task title |
| `description` | string \| null | Task description |
| `is_completed` | boolean | Updated completion status |
| `created_at` | string (ISO 8601) | Creation timestamp |
| `updated_at` | string (ISO 8601) | Updated timestamp |

**Example Request**:
```json
{
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "task_id": "7c9e6679-7425-40de-944b-e07fc1f90ae7"
}
```

**Example Response (Success)**:
```json
{
  "success": true,
  "task_id": "7c9e6679-7425-40de-944b-e07fc1f90ae7",
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "title": "Buy groceries",
  "description": "Milk, eggs, bread",
  "is_completed": true,
  "created_at": "2026-01-05T14:30:00.123456Z",
  "updated_at": "2026-01-05T15:45:00.789012Z"
}
```

**Error Codes**:
- `VALIDATION_ERROR`: Invalid user_id or task_id format
- `TASK_NOT_FOUND`: Task does not exist or user not authorized
- `AUTHORIZATION_ERROR`: Task belongs to different user
- `DATABASE_ERROR`: Database operation failed

---

### 4. delete_task

**Purpose**: Permanently delete a task

**Input Schema**:

| Field | Type | Required | Validation | Description |
|-------|------|----------|------------|-------------|
| `user_id` | string (UUID) | Yes | Valid UUID4 | Authenticated user UUID |
| `task_id` | string (UUID) | Yes | Valid UUID4 | Task UUID to delete |

**Output Schema (Success)**:

| Field | Type | Description |
|-------|------|-------------|
| `success` | boolean | Always `true` |
| `task_id` | string (UUID) | Deleted task UUID |
| `message` | string | Confirmation message |

**Example Request**:
```json
{
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "task_id": "7c9e6679-7425-40de-944b-e07fc1f90ae7"
}
```

**Example Response (Success)**:
```json
{
  "success": true,
  "task_id": "7c9e6679-7425-40de-944b-e07fc1f90ae7",
  "message": "Task deleted successfully"
}
```

**Error Codes**:
- `VALIDATION_ERROR`: Invalid user_id or task_id format
- `TASK_NOT_FOUND`: Task does not exist or user not authorized
- `AUTHORIZATION_ERROR`: Task belongs to different user
- `DATABASE_ERROR`: Database operation failed

---

### 5. update_task

**Purpose**: Update task title and/or description

**Input Schema**:

| Field | Type | Required | Validation | Description |
|-------|------|----------|------------|-------------|
| `user_id` | string (UUID) | Yes | Valid UUID4 | Authenticated user UUID |
| `task_id` | string (UUID) | Yes | Valid UUID4 | Task UUID to update |
| `title` | string | No | 1-200 chars | New task title (optional) |
| `description` | string | No | Max 1000 chars | New description (optional) |

**Notes**:
- At least one of `title` or `description` must be provided
- Only provided fields are updated (partial updates supported)
- Setting `description` to empty string clears it

**Output Schema (Success)**:

| Field | Type | Description |
|-------|------|-------------|
| `success` | boolean | Always `true` |
| `task_id` | string (UUID) | Task UUID |
| `user_id` | string (UUID) | Owner user UUID |
| `title` | string | Updated task title |
| `description` | string \| null | Updated description |
| `is_completed` | boolean | Completion status (unchanged) |
| `created_at` | string (ISO 8601) | Creation timestamp (unchanged) |
| `updated_at` | string (ISO 8601) | Updated timestamp |

**Example Request**:
```json
{
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "task_id": "7c9e6679-7425-40de-944b-e07fc1f90ae7",
  "title": "Buy groceries and supplies",
  "description": "Milk, eggs, bread, paper towels"
}
```

**Example Response (Success)**:
```json
{
  "success": true,
  "task_id": "7c9e6679-7425-40de-944b-e07fc1f90ae7",
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "title": "Buy groceries and supplies",
  "description": "Milk, eggs, bread, paper towels",
  "is_completed": false,
  "created_at": "2026-01-05T14:30:00.123456Z",
  "updated_at": "2026-01-05T16:00:00.456789Z"
}
```

**Error Codes**:
- `VALIDATION_ERROR`: Invalid IDs, empty title, no fields provided, or field too long
- `TASK_NOT_FOUND`: Task does not exist or user not authorized
- `AUTHORIZATION_ERROR`: Task belongs to different user
- `DATABASE_ERROR`: Database operation failed

## Error Code Reference

| Error Code | HTTP Analog | When Used |
|------------|-------------|-----------|
| `VALIDATION_ERROR` | 422 Unprocessable Entity | Invalid input parameters, constraint violations |
| `TASK_NOT_FOUND` | 404 Not Found | Task does not exist or user lacks access |
| `AUTHORIZATION_ERROR` | 403 Forbidden | User not authorized to access task |
| `DATABASE_ERROR` | 500 Internal Server Error | Database connection or query failure |

## Validation Rules Summary

### User ID
- **Format**: UUID4 string
- **Example**: `"550e8400-e29b-41d4-a716-446655440000"`
- **Validation**: Must parse as valid UUID4

### Task ID
- **Format**: UUID4 string
- **Example**: `"7c9e6679-7425-40de-944b-e07fc1f90ae7"`
- **Validation**: Must parse as valid UUID4

### Title
- **Type**: String
- **Required**: Yes (for add_task), Optional (for update_task)
- **Min Length**: 1 character
- **Max Length**: 200 characters
- **Constraint**: Cannot be empty string

### Description
- **Type**: String or null
- **Required**: No
- **Max Length**: 1000 characters
- **Nullable**: Yes

### Timestamps
- **Format**: ISO 8601 with microseconds and UTC timezone
- **Pattern**: `YYYY-MM-DDTHH:MM:SS.ffffffZ`
- **Timezone**: Always UTC (Z suffix)
- **Generated**: Server-side (clients cannot set)

## Pydantic Model Mapping

| Schema | Python Module | Pydantic Model |
|--------|---------------|----------------|
| add_task input | `src.mcp.schemas` | `AddTaskInput` |
| add_task output | `src.mcp.schemas` | `TaskOutput` |
| list_tasks input | `src.mcp.schemas` | `ListTasksInput` |
| list_tasks output | `src.mcp.schemas` | `ListTasksOutput` |
| complete_task input | `src.mcp.schemas` | `CompleteTaskInput` |
| complete_task output | `src.mcp.schemas` | `TaskOutput` |
| delete_task input | `src.mcp.schemas` | `DeleteTaskInput` |
| delete_task output | `src.mcp.schemas` | `DeleteTaskOutput` |
| update_task input | `src.mcp.schemas` | `UpdateTaskInput` |
| update_task output | `src.mcp.schemas` | `TaskOutput` |

## Database Model Mapping

All MCP tools use the existing `Task` SQLModel:

**Source**: `backend/src/models/task.py`

**Task Model Fields**:
- `id` (UUID) → `task_id` (string UUID) in MCP
- `user_id` (UUID) → `user_id` (string UUID) in MCP
- `title` (str) → `title` (string) in MCP
- `description` (str | None) → `description` (string | null) in MCP
- `is_completed` (bool) → `is_completed` (boolean) in MCP
- `created_at` (datetime) → `created_at` (ISO 8601 string) in MCP
- `updated_at` (datetime) → `updated_at` (ISO 8601 string) in MCP

**Conversion**: MCP schemas handle UUID ↔ string and datetime ↔ ISO string conversions
