# Data Model: Task CRUD

**Feature**: 004-task-crud
**Date**: 2026-01-01
**Status**: Final

## Entity Definitions

### Task

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | Primary Key, default uuid4() | Unique task identifier |
| user_id | UUID | Foreign Key → users.id, NOT NULL, indexed | Owner of the task |
| title | String(200) | NOT NULL, 1-200 chars | Task title |
| description | String(1000) | NULL allowed, max 1000 chars | Optional task description |
| is_completed | Boolean | NOT NULL, default false | Completion status |
| created_at | DateTime(UTC) | NOT NULL, default now() | Creation timestamp |
| updated_at | DateTime(UTC) | NOT NULL, default now(), auto-update | Last modification timestamp |

### Relationships

```
User (1) ─────< Task (Many)
  │                │
  └── id ─────────> user_id (FK)
```

- One User has many Tasks
- Each Task belongs to exactly one User
- Deleting a Task does NOT affect User
- User deletion behavior: Out of scope (no cascade specified)

### Indexes

| Index | Columns | Type | Purpose |
|-------|---------|------|---------|
| ix_tasks_user_id | user_id | B-tree | Filter tasks by owner |
| ix_tasks_is_completed | is_completed | B-tree | Future filtering optimization |

## SQLModel Implementation

```python
# backend/src/models/task.py

from datetime import datetime, timezone
from uuid import UUID, uuid4

from sqlmodel import Field, SQLModel


class Task(SQLModel, table=True):
    """
    Task model for todo items.

    Each task belongs to exactly one user and is isolated from other users.
    """

    __tablename__ = "tasks"

    id: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
        description="Unique task identifier",
    )
    user_id: UUID = Field(
        index=True,
        foreign_key="users.id",
        nullable=False,
        description="Owner user ID (from JWT)",
    )
    title: str = Field(
        min_length=1,
        max_length=200,
        description="Task title (required)",
    )
    description: str | None = Field(
        default=None,
        max_length=1000,
        description="Task description (optional)",
    )
    is_completed: bool = Field(
        default=False,
        index=True,
        description="Completion status",
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Creation timestamp",
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Last update timestamp",
    )
```

## Request/Response Schemas

```python
# backend/src/schemas/task.py

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class TaskCreate(BaseModel):
    """Request schema for creating a task."""
    title: str = Field(..., min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=1000)


class TaskUpdate(BaseModel):
    """Request schema for updating a task."""
    title: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=1000)


class TaskResponse(BaseModel):
    """Response schema for task data."""
    id: UUID
    user_id: UUID
    title: str
    description: str | None
    is_completed: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class TaskListResponse(BaseModel):
    """Response schema for task list."""
    tasks: list[TaskResponse]
    count: int
```

## Validation Rules

| Field | Rule | Error Message |
|-------|------|---------------|
| title | Required, 1-200 chars | "Title is required" / "Title must be 200 characters or less" |
| description | Optional, max 1000 chars | "Description must be 1000 characters or less" |
| user_id | Must match JWT sub claim | 403 Forbidden |

## State Transitions

```
┌─────────────────┐
│                 │
│   is_completed  │◀──── PATCH /complete (toggle)
│   = false       │
│                 │
└────────┬────────┘
         │
         │ PATCH /complete
         ▼
┌─────────────────┐
│                 │
│   is_completed  │──────► PATCH /complete (toggle)
│   = true        │
│                 │
└─────────────────┘
```

- Toggle is idempotent: calling returns opposite of current state
- No intermediate states
- State persists in database
