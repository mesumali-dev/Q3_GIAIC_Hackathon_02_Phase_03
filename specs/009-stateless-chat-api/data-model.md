# Data Model: Stateless Chat API & Conversation Persistence

**Feature**: 009-stateless-chat-api
**Date**: 2026-01-08

## Overview

This feature uses existing entities (Conversation, Message) and introduces new request/response schemas for the chat API endpoint.

## Existing Entities (No Changes Required)

### Conversation

Already implemented in `backend/src/models/conversation.py`.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PK, auto-generated | Unique conversation identifier |
| user_id | UUID | FK → users.id, NOT NULL, indexed | Owner user ID from JWT |
| title | string | max 200 chars, nullable | Optional conversation title |
| created_at | datetime | NOT NULL, auto-generated | Conversation creation timestamp |
| updated_at | datetime | NOT NULL, auto-updated | Last message timestamp |

### Message

Already implemented in `backend/src/models/message.py`.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PK, auto-generated | Unique message identifier |
| conversation_id | UUID | FK → conversations.id, NOT NULL, indexed | Parent conversation |
| role | string | max 20 chars, NOT NULL | Message role: "user", "assistant", "system" |
| content | string | max 50000 chars, NOT NULL | Message text content |
| created_at | datetime | NOT NULL, auto-generated | Message creation timestamp |

## New Request/Response Schemas

### ChatRequest

Request body for POST `/api/{user_id}/chat`.

| Field | Type | Required | Constraints | Description |
|-------|------|----------|-------------|-------------|
| message | string | Yes | min 1, max 50000 chars | User message content |
| conversation_id | UUID | No | Valid UUID v4 if provided | Existing conversation to continue |

**Validation Rules**:
- `message` cannot be empty or whitespace-only
- `conversation_id`, if provided, must exist and belong to the authenticated user

### ChatResponse

Response body from POST `/api/{user_id}/chat`.

| Field | Type | Nullable | Description |
|-------|------|----------|-------------|
| conversation_id | UUID | No | Conversation ID (new or existing) |
| assistant_message | string | No | AI agent's response text |
| tool_calls | ToolCall[] | No | Array of tool invocations (can be empty) |
| created_at | datetime | No | Response timestamp |

### ToolCall

Information about an MCP tool invocation.

| Field | Type | Nullable | Description |
|-------|------|----------|-------------|
| tool_name | string | No | Name of the invoked tool |
| parameters | object | No | Parameters passed to the tool |
| result | object | Yes | Tool result (null if pending/failed) |
| success | boolean | No | Whether the tool call succeeded |

## Entity Relationships

```
User (1) ─────────────< Conversation (*)
                              │
                              │ user_id (FK)
                              │
                              └────────────< Message (*)
                                    │
                                    │ conversation_id (FK)
                                    │
                                    ├── role: "user"
                                    └── role: "assistant"
```

## State Transitions

### Conversation Lifecycle

```
[No Conversation]
      │
      │ POST /api/{user_id}/chat (no conversation_id)
      ▼
[Created] ──────────────────────────────────────────┐
      │                                              │
      │ POST /api/{user_id}/chat (with conversation_id)
      ▼                                              │
[Active] <───────────────────────────────────────────┘
      │
      │ DELETE /api/{user_id}/conversations/{id}
      ▼
[Deleted]
```

### Message Flow (Per Chat Request)

```
[Request Received]
      │
      │ Validate JWT + user_id
      ▼
[Authenticated]
      │
      ├─── conversation_id provided? ───┐
      │         │                        │
      │         │ Yes                    │ No
      │         ▼                        ▼
      │   [Load Conversation]    [Create Conversation]
      │         │                        │
      │         └────────┬───────────────┘
      │                  │
      │                  ▼
      │         [Fetch Message History]
      │                  │
      │                  ▼
      │         [Persist User Message]
      │                  │
      │                  ▼
      │         [Build Agent Input]
      │                  │
      │                  ▼
      │         [Execute Agent]
      │                  │
      │                  ▼
      │         [Extract Tool Calls]
      │                  │
      │                  ▼
      │         [Persist Assistant Message]
      │                  │
      │                  ▼
      │         [Return ChatResponse]
```

## Database Queries

### Load Conversation History

```sql
-- Get all messages for a conversation, chronologically
SELECT id, conversation_id, role, content, created_at
FROM messages
WHERE conversation_id = :conversation_id
ORDER BY created_at ASC;
```

### Verify Conversation Ownership

```sql
-- Check conversation exists and belongs to user
SELECT id, user_id, title, created_at, updated_at
FROM conversations
WHERE id = :conversation_id AND user_id = :user_id;
```

### Persist Message

```sql
-- Insert new message
INSERT INTO messages (id, conversation_id, role, content, created_at)
VALUES (:id, :conversation_id, :role, :content, :created_at);

-- Update conversation timestamp
UPDATE conversations
SET updated_at = :updated_at
WHERE id = :conversation_id;
```

## Pydantic Schema Definitions

```python
# In backend/src/schemas/chat.py

from datetime import datetime
from typing import Any
from uuid import UUID
from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """Request schema for chat endpoint."""

    message: str = Field(
        ...,
        min_length=1,
        max_length=50000,
        description="User message content"
    )
    conversation_id: UUID | None = Field(
        default=None,
        description="Existing conversation ID to continue"
    )


class ToolCall(BaseModel):
    """Information about an MCP tool invocation."""

    tool_name: str = Field(..., description="Name of the invoked tool")
    parameters: dict[str, Any] = Field(
        default_factory=dict,
        description="Parameters passed to the tool"
    )
    result: dict[str, Any] | None = Field(
        default=None,
        description="Tool result"
    )
    success: bool = Field(..., description="Whether the tool call succeeded")


class ChatResponse(BaseModel):
    """Response schema for chat endpoint."""

    conversation_id: UUID = Field(
        ...,
        description="Conversation ID (new or existing)"
    )
    assistant_message: str = Field(
        ...,
        description="AI agent's response text"
    )
    tool_calls: list[ToolCall] = Field(
        default_factory=list,
        description="Array of tool invocations"
    )
    created_at: datetime = Field(
        ...,
        description="Response timestamp"
    )

    model_config = {"from_attributes": True}
```

## Index Requirements

Existing indexes are sufficient:
- `conversations.user_id` - indexed for user lookup
- `messages.conversation_id` - indexed for message retrieval

No new indexes required for this feature.
