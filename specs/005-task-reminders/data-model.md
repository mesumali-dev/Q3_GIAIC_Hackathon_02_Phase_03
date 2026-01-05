# Data Model: Task Reminders & Notifications

**Feature**: 005-task-reminders
**Date**: 2026-01-02
**Database**: Neon PostgreSQL via SQLModel ORM

## Entity: Reminder

Represents a scheduled notification for a task with optional repeat functionality.

### Schema

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | Integer | PRIMARY KEY, AUTO INCREMENT | Unique reminder identifier |
| `user_id` | String | FOREIGN KEY → user.id, NOT NULL, INDEX | Owner of the reminder (from JWT) |
| `task_id` | Integer | FOREIGN KEY → task.id, NOT NULL, ON DELETE CASCADE | Associated task |
| `remind_at` | DateTime (UTC) | NOT NULL, INDEX | When to trigger the reminder |
| `repeat_interval_minutes` | Integer | NULLABLE, CHECK (> 0) | Minutes between repeats (null = one-time) |
| `repeat_count` | Integer | NULLABLE, CHECK (> 0) | Total number of times to repeat (null = one-time) |
| `triggered_count` | Integer | NOT NULL, DEFAULT 0 | How many times reminder has triggered |
| `is_active` | Boolean | NOT NULL, DEFAULT TRUE, INDEX | Whether reminder is active |
| `created_at` | DateTime (UTC) | NOT NULL, DEFAULT CURRENT_TIMESTAMP | When reminder was created |

### Indexes

```sql
CREATE INDEX idx_reminder_user_id ON reminder(user_id);
CREATE INDEX idx_reminder_remind_at ON reminder(remind_at);
CREATE INDEX idx_reminder_is_active ON reminder(is_active);

-- Composite index for most common query (due reminders for user)
CREATE INDEX idx_reminder_user_active_time ON reminder(user_id, is_active, remind_at);
```

### Validation Rules

1. **Repeat Interval**: If provided, must be positive integer
2. **Repeat Count**: If provided, must be positive integer
3. **Triggered Count**: Must be >= 0 and <= repeat_count (if repeat_count exists)
4. **Remind At**: Must be valid ISO 8601 datetime
5. **Foreign Keys**: user_id and task_id must reference existing records
6. **Active State**: Can only be FALSE if triggered_count >= repeat_count OR manually deactivated

### State Transitions

```
┌─────────────┐
│   CREATED   │ (is_active=true, triggered_count=0)
└─────┬───────┘
      │
      v
┌─────────────┐
│  DUE/FIRED  │ (remind_at <= now)
└─────┬───────┘
      │
      v
┌─────────────────────────┐
│  Process Reminder       │
│  - Increment triggered  │
│  - Check repeat logic   │
└─────┬───────────────────┘
      │
      ├─> repeat_count not reached ──> Calculate next remind_at (ACTIVE)
      │
      └─> repeat_count reached ──────> Set is_active=false (INACTIVE)
```

### Relationships

```
User (1) ─────< has many >───── (N) Reminder
Task (1) ─────< has many >───── (N) Reminder

- One User can have many Reminders
- One Task can have many Reminders
- One Reminder belongs to exactly one User and one Task
```

### Example Records

```json
// One-time reminder
{
  "id": 1,
  "user_id": "user_abc123",
  "task_id": 42,
  "remind_at": "2026-01-03T14:30:00Z",
  "repeat_interval_minutes": null,
  "repeat_count": null,
  "triggered_count": 0,
  "is_active": true,
  "created_at": "2026-01-02T10:00:00Z"
}

// Repeating reminder (e.g., every 15 minutes, 3 times)
{
  "id": 2,
  "user_id": "user_abc123",
  "task_id": 43,
  "remind_at": "2026-01-02T15:00:00Z",
  "repeat_interval_minutes": 15,
  "repeat_count": 3,
  "triggered_count": 1,
  "is_active": true,
  "created_at": "2026-01-02T14:45:00Z"
}

// Exhausted repeating reminder
{
  "id": 3,
  "user_id": "user_abc123",
  "task_id": 44,
  "remind_at": "2026-01-02T16:30:00Z",
  "repeat_interval_minutes": 30,
  "repeat_count": 2,
  "triggered_count": 2,
  "is_active": false,
  "created_at": "2026-01-02T15:30:00Z"
}
```

## SQLModel Implementation

```python
from datetime import datetime
from typing import Optional
from sqlmodel import Field, SQLModel


class Reminder(SQLModel, table=True):
    """
    Reminder entity for task notifications.

    Represents a scheduled notification for a task with optional repeat functionality.
    Reminders are evaluated on-demand during API requests.
    """

    id: Optional[int] = Field(default=None, primary_key=True)

    # Foreign keys
    user_id: str = Field(
        foreign_key="user.id",
        index=True,
        description="Owner of the reminder (from JWT)"
    )
    task_id: int = Field(
        foreign_key="task.id",
        sa_column_kwargs={"ondelete": "CASCADE"},
        description="Associated task (cascade delete)"
    )

    # Timing fields
    remind_at: datetime = Field(
        index=True,
        description="When to trigger reminder (UTC)"
    )
    repeat_interval_minutes: Optional[int] = Field(
        default=None,
        gt=0,
        description="Minutes between repeats (null = one-time)"
    )
    repeat_count: Optional[int] = Field(
        default=None,
        gt=0,
        description="Total times to repeat (null = one-time)"
    )

    # State fields
    triggered_count: int = Field(
        default=0,
        ge=0,
        description="How many times reminder has triggered"
    )
    is_active: bool = Field(
        default=True,
        index=True,
        description="Whether reminder is active"
    )

    # Audit
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="When reminder was created (UTC)"
    )

    class Config:
        """SQLModel configuration."""
        schema_extra = {
            "example": {
                "user_id": "user_abc123",
                "task_id": 42,
                "remind_at": "2026-01-03T14:30:00Z",
                "repeat_interval_minutes": 15,
                "repeat_count": 3
            }
        }


class ReminderCreate(SQLModel):
    """Schema for creating a new reminder."""
    task_id: int = Field(description="ID of the task to remind about")
    remind_at: datetime = Field(description="When to trigger reminder (ISO 8601)")
    repeat_interval_minutes: Optional[int] = Field(
        default=None,
        gt=0,
        le=1440,  # Max 24 hours
        description="Minutes between repeats (optional)"
    )
    repeat_count: Optional[int] = Field(
        default=None,
        gt=0,
        le=100,  # Max 100 repeats
        description="Total times to repeat (optional)"
    )


class ReminderRead(SQLModel):
    """Schema for reading reminder data."""
    id: int
    user_id: str
    task_id: int
    remind_at: datetime
    repeat_interval_minutes: Optional[int]
    repeat_count: Optional[int]
    triggered_count: int
    is_active: bool
    created_at: datetime


class ReminderWithTask(ReminderRead):
    """Schema for reminder with task details (for notifications)."""
    task_title: str = Field(description="Title of the associated task")
    task_description: Optional[str] = Field(description="Description of the task")
```

## Database Migration

### Initial Table Creation

```sql
-- Run automatically via SQLModel.metadata.create_all(engine)
-- Or manually via migration tool

CREATE TABLE reminder (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR NOT NULL REFERENCES "user"(id),
    task_id INTEGER NOT NULL REFERENCES task(id) ON DELETE CASCADE,
    remind_at TIMESTAMP WITH TIME ZONE NOT NULL,
    repeat_interval_minutes INTEGER CHECK (repeat_interval_minutes > 0),
    repeat_count INTEGER CHECK (repeat_count > 0),
    triggered_count INTEGER NOT NULL DEFAULT 0 CHECK (triggered_count >= 0),
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_reminder_user_id ON reminder(user_id);
CREATE INDEX idx_reminder_remind_at ON reminder(remind_at);
CREATE INDEX idx_reminder_is_active ON reminder(is_active);
CREATE INDEX idx_reminder_user_active_time ON reminder(user_id, is_active, remind_at);

-- Constraint: triggered_count cannot exceed repeat_count
ALTER TABLE reminder ADD CONSTRAINT chk_triggered_count_le_repeat_count
    CHECK (
        repeat_count IS NULL OR
        triggered_count <= repeat_count
    );
```

## Query Patterns

### Get Due Reminders for User

```python
from sqlmodel import select
from datetime import datetime

def get_due_reminders(user_id: str, db: Session) -> List[Reminder]:
    """Fetch all active reminders that are due for a user."""
    now = datetime.utcnow()
    statement = (
        select(Reminder)
        .where(Reminder.user_id == user_id)
        .where(Reminder.is_active == True)
        .where(Reminder.remind_at <= now)
        .order_by(Reminder.remind_at)
    )
    return db.exec(statement).all()
```

### Process Reminder (Update State)

```python
from datetime import timedelta

def process_reminder(reminder: Reminder, db: Session) -> None:
    """
    Process a due reminder:
    1. Increment triggered_count
    2. Calculate next remind_at if repeats remain
    3. Deactivate if repeat exhausted
    """
    reminder.triggered_count += 1

    # Check if more repeats remain
    if (
        reminder.repeat_interval_minutes is not None
        and reminder.repeat_count is not None
        and reminder.triggered_count < reminder.repeat_count
    ):
        # Schedule next repeat
        reminder.remind_at = reminder.remind_at + timedelta(
            minutes=reminder.repeat_interval_minutes
        )
    else:
        # No more repeats, deactivate
        reminder.is_active = False

    db.add(reminder)
    db.commit()
    db.refresh(reminder)
```

### Get Reminders with Task Details (for Notification Display)

```python
from sqlmodel import select
from src.models.task import Task

def get_due_reminders_with_tasks(user_id: str, db: Session) -> List[dict]:
    """Fetch due reminders with task details for notification display."""
    now = datetime.utcnow()
    statement = (
        select(Reminder, Task)
        .join(Task, Reminder.task_id == Task.id)
        .where(Reminder.user_id == user_id)
        .where(Reminder.is_active == True)
        .where(Reminder.remind_at <= now)
        .order_by(Reminder.remind_at)
    )

    results = db.exec(statement).all()
    return [
        {
            "id": reminder.id,
            "remind_at": reminder.remind_at,
            "triggered_count": reminder.triggered_count,
            "repeat_count": reminder.repeat_count,
            "task_id": task.id,
            "task_title": task.title,
            "task_description": task.description,
        }
        for reminder, task in results
    ]
```

## Data Integrity Guarantees

1. **Referential Integrity**: Foreign keys ensure reminders reference valid users and tasks
2. **Cascade Delete**: Deleting a task automatically deletes associated reminders
3. **User Isolation**: All queries filter by user_id from JWT (enforced in API layer)
4. **Atomic Updates**: Reminder state updates happen in database transactions
5. **Constraint Checks**: Database enforces positive intervals/counts and triggered_count <= repeat_count

## Performance Considerations

**Estimated Query Performance** (Neon PostgreSQL):
- Get due reminders for user: ~10-50ms (indexed on user_id, is_active, remind_at)
- Create reminder: ~5-10ms (single INSERT)
- Delete reminder: ~5-10ms (single DELETE)

**Scaling Characteristics**:
- Linear with number of users (user-scoped queries)
- Sub-linear with total reminders (composite index optimizes filtering)
- Expected load: 50-100 reminders per user (well within index efficiency range)

**Index Selectivity**:
- `idx_reminder_user_id`: High (distributes across users)
- `idx_reminder_remind_at`: Medium (time-based clustering)
- `idx_reminder_is_active`: Low (boolean), but combined index compensates
- `idx_reminder_user_active_time`: Very High (composite covers common query)
