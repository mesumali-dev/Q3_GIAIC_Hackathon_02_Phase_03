# Data Model: AI-Native Todo Core Foundation (Phase 1)

**Feature Branch**: `006-ai-todo-core-foundation`
**Date**: 2026-01-04
**Status**: Design Complete

## Overview

This document defines the database schema for Phase 1 of the AI-native todo application. It extends the existing User and Task models with new Conversation and Message entities to support conversation storage for Phase 2 AI integration.

---

## Entity Relationship Diagram

```
┌──────────────────┐
│      users       │
├──────────────────┤
│ id (PK, UUID)    │
│ name             │
│ email (unique)   │
│ hashed_password  │
│ created_at       │
│ updated_at       │
└────────┬─────────┘
         │
         │ 1:N
         ▼
┌──────────────────┐     ┌──────────────────────┐
│      tasks       │     │    conversations     │
├──────────────────┤     ├──────────────────────┤
│ id (PK, UUID)    │     │ id (PK, UUID)        │
│ user_id (FK)     │◄────┤ user_id (FK)         │
│ title            │     │ title (nullable)     │
│ description      │     │ created_at           │
│ is_completed     │     │ updated_at           │
│ created_at       │     └──────────┬───────────┘
│ updated_at       │                │
└──────────────────┘                │ 1:N
                                    ▼
                        ┌──────────────────────┐
                        │      messages        │
                        ├──────────────────────┤
                        │ id (PK, UUID)        │
                        │ conversation_id (FK) │
                        │ role                 │
                        │ content              │
                        │ created_at           │
                        └──────────────────────┘
```

---

## Entity Definitions

### User (Existing)

**Table Name**: `users`
**Source**: `backend/src/models/user.py`
**Status**: No changes required

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK, default=uuid4 | Unique user identifier |
| name | VARCHAR(255) | NOT NULL | User display name |
| email | VARCHAR(255) | NOT NULL, UNIQUE, INDEX | Email for login |
| hashed_password | VARCHAR(255) | NOT NULL | bcrypt hashed password |
| created_at | TIMESTAMP WITH TZ | NOT NULL, default=now() | Account creation time |
| updated_at | TIMESTAMP WITH TZ | NOT NULL, default=now() | Last update time |

### Task (Existing)

**Table Name**: `tasks`
**Source**: `backend/src/models/task.py`
**Status**: No changes required

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK, default=uuid4 | Unique task identifier |
| user_id | UUID | FK(users.id), NOT NULL, INDEX | Owner user reference |
| title | VARCHAR(200) | NOT NULL, min_length=1 | Task title (required) |
| description | VARCHAR(1000) | NULLABLE | Task description (optional) |
| is_completed | BOOLEAN | NOT NULL, default=false, INDEX | Completion status |
| created_at | TIMESTAMP WITH TZ | NOT NULL, default=now() | Creation timestamp |
| updated_at | TIMESTAMP WITH TZ | NOT NULL, default=now() | Last update timestamp |

### Conversation (New)

**Table Name**: `conversations`
**Source**: `backend/src/models/conversation.py` (to be created)
**Purpose**: Stores chat sessions for AI-native interaction in Phase 2

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK, default=uuid4 | Unique conversation identifier |
| user_id | UUID | FK(users.id), NOT NULL, INDEX | Owner user reference |
| title | VARCHAR(200) | NULLABLE | Optional conversation title/summary |
| created_at | TIMESTAMP WITH TZ | NOT NULL, default=now() | Conversation start time |
| updated_at | TIMESTAMP WITH TZ | NOT NULL, default=now() | Last message time |

**Indexes**:
- `idx_conversations_user_id` on `user_id` (for user-scoped queries)
- `idx_conversations_created_at` on `created_at` (for chronological listing)

**Constraints**:
- ON DELETE CASCADE: When user is deleted, conversations are deleted (future scope)

### Message (New)

**Table Name**: `messages`
**Source**: `backend/src/models/message.py` (to be created)
**Purpose**: Stores individual messages within conversations

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK, default=uuid4 | Unique message identifier |
| conversation_id | UUID | FK(conversations.id), NOT NULL, INDEX | Parent conversation reference |
| role | VARCHAR(20) | NOT NULL | Message sender role: user/assistant/system |
| content | TEXT | NOT NULL, max_length=50000 | Message text content |
| created_at | TIMESTAMP WITH TZ | NOT NULL, default=now() | Message timestamp |

**Indexes**:
- `idx_messages_conversation_id` on `conversation_id` (for conversation queries)
- `idx_messages_created_at` on `created_at` (for chronological ordering)

**Constraints**:
- ON DELETE CASCADE: When conversation is deleted, messages are deleted

**Role Values**:
- `"user"`: Message from the human user
- `"assistant"`: Message from the AI assistant
- `"system"`: System-generated message (e.g., context, instructions)

---

## SQLModel Implementations

### Conversation Model

```python
# backend/src/models/conversation.py

from datetime import datetime, timezone
from uuid import UUID, uuid4

from sqlmodel import Field, SQLModel


class Conversation(SQLModel, table=True):
    """
    Conversation model for chat sessions.

    Each conversation belongs to exactly one user and contains
    zero or more messages.
    """

    __tablename__ = "conversations"

    id: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
        description="Unique conversation identifier",
    )
    user_id: UUID = Field(
        index=True,
        foreign_key="users.id",
        nullable=False,
        description="Owner user ID (from JWT)",
    )
    title: str | None = Field(
        default=None,
        max_length=200,
        description="Optional conversation title/summary",
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Conversation creation timestamp",
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Last message timestamp",
    )
```

### Message Model

```python
# backend/src/models/message.py

from datetime import datetime, timezone
from typing import Literal
from uuid import UUID, uuid4

from sqlmodel import Field, SQLModel


class Message(SQLModel, table=True):
    """
    Message model for conversation history.

    Each message belongs to exactly one conversation and has a role
    indicating who sent it (user, assistant, or system).
    """

    __tablename__ = "messages"

    id: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
        description="Unique message identifier",
    )
    conversation_id: UUID = Field(
        index=True,
        foreign_key="conversations.id",
        nullable=False,
        description="Parent conversation ID",
    )
    role: str = Field(
        max_length=20,
        description="Message role: user, assistant, or system",
    )
    content: str = Field(
        max_length=50000,
        description="Message text content",
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Message creation timestamp",
    )
```

---

## Validation Rules

### Conversation Validation

| Field | Rule | Error Response |
|-------|------|----------------|
| title | max 200 characters | 422 Unprocessable Entity |
| user_id | must match JWT user_id | 403 Forbidden |

### Message Validation

| Field | Rule | Error Response |
|-------|------|----------------|
| content | required, max 50,000 characters | 422 Unprocessable Entity |
| role | must be "user", "assistant", or "system" | 422 Unprocessable Entity |
| conversation_id | must exist and be owned by user | 404 Not Found |

---

## State Transitions

### Conversation States

Conversations have no explicit state machine in Phase 1. They exist or are deleted.

```
Created → (Messages added) → Deleted
```

### Message States

Messages are immutable after creation. No update or state transitions.

```
Created → Deleted (via cascade only)
```

---

## Migration Strategy

### Migration Approach

Use SQLModel's `create_tables()` for initial schema creation. For production, migrations would use Alembic.

### Migration Order

1. Ensure `users` table exists (already done)
2. Ensure `tasks` table exists (already done)
3. Create `conversations` table
4. Create `messages` table (depends on conversations)

### Rollback Strategy

Drop tables in reverse order:
1. Drop `messages`
2. Drop `conversations`

### Data Migration

No data migration required - these are new tables with no existing data.

---

## Query Patterns

### Common Query: List User's Conversations

```sql
SELECT id, user_id, title, created_at, updated_at
FROM conversations
WHERE user_id = :user_id
ORDER BY updated_at DESC;
```

### Common Query: Get Conversation with Messages

```sql
-- Get conversation
SELECT id, user_id, title, created_at, updated_at
FROM conversations
WHERE id = :conversation_id AND user_id = :user_id;

-- Get messages
SELECT id, conversation_id, role, content, created_at
FROM messages
WHERE conversation_id = :conversation_id
ORDER BY created_at ASC;
```

### Common Query: Add Message and Update Conversation

```sql
-- Insert message
INSERT INTO messages (id, conversation_id, role, content, created_at)
VALUES (:id, :conversation_id, :role, :content, :created_at);

-- Update conversation timestamp
UPDATE conversations
SET updated_at = :now
WHERE id = :conversation_id;
```

### Common Query: Delete Conversation (Cascade)

```sql
-- Messages deleted automatically via CASCADE
DELETE FROM conversations
WHERE id = :conversation_id AND user_id = :user_id;
```

---

## References

- Spec: `specs/006-ai-todo-core-foundation/spec.md` (FR-008 through FR-015)
- Research: `specs/006-ai-todo-core-foundation/research.md` (decisions)
- Existing Model: `backend/src/models/task.py` (pattern reference)
- Constitution: `.specify/memory/constitution.md` (data integrity requirements)
