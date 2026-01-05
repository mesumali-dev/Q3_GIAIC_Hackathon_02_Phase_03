# Quickstart: AI-Native Todo Core Foundation (Phase 1)

**Feature Branch**: `006-ai-todo-core-foundation`
**Date**: 2026-01-04

## Overview

This guide helps developers get started with the Phase 1 implementation of the AI-native todo backend. It covers setting up the development environment, running the existing backend, and understanding the new entities to be implemented.

---

## Prerequisites

- Python 3.11+
- uv (Python package manager)
- Git
- Neon PostgreSQL account (or local PostgreSQL for testing)

---

## Quick Setup

### 1. Clone and Switch Branch

```bash
git checkout 006-ai-todo-core-foundation
cd Phase_03/backend
```

### 2. Install Dependencies

```bash
uv sync
```

### 3. Configure Environment

```bash
cp .env.example .env
```

Edit `.env` with your credentials:

```env
DATABASE_URL=postgresql://user:password@host:5432/dbname?sslmode=require
BETTER_AUTH_SECRET=your-jwt-secret-from-frontend
DEBUG=true
```

### 4. Run Development Server

```bash
uv run uvicorn src.main:app --reload --port 8000
```

### 5. Verify Health

```bash
curl http://localhost:8000/health
# Expected: {"status":"healthy","version":"1.0.0"}
```

---

## Existing Functionality

The backend already has these working features:

### Task API (Implemented)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/{user_id}/tasks` | List all tasks |
| POST | `/api/{user_id}/tasks` | Create task |
| GET | `/api/{user_id}/tasks/{id}` | Get task |
| PUT | `/api/{user_id}/tasks/{id}` | Update task |
| DELETE | `/api/{user_id}/tasks/{id}` | Delete task |
| PATCH | `/api/{user_id}/tasks/{id}/complete` | Toggle complete |

### Authentication (Implemented)

- JWT verification via `Authorization: Bearer <token>` header
- User ID extracted from JWT claims
- User ownership validation on all routes

---

## What Phase 1 Adds

### New Models

1. **Conversation** (`backend/src/models/conversation.py`)
   - Stores chat sessions for future AI interaction
   - Fields: id, user_id, title, created_at, updated_at

2. **Message** (`backend/src/models/message.py`)
   - Stores messages within conversations
   - Fields: id, conversation_id, role, content, created_at

### New Services

1. **conversation_service.py**
   - `create_conversation(db, user_id, data)` → Conversation
   - `get_conversations(db, user_id)` → List[Conversation]
   - `get_conversation(db, user_id, conversation_id)` → Conversation | None
   - `delete_conversation(db, user_id, conversation_id)` → bool
   - `add_message(db, user_id, conversation_id, data)` → Message
   - `get_messages(db, conversation_id)` → List[Message]

### New API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/{user_id}/conversations` | List conversations |
| POST | `/api/{user_id}/conversations` | Create conversation |
| GET | `/api/{user_id}/conversations/{id}` | Get with messages |
| DELETE | `/api/{user_id}/conversations/{id}` | Delete (cascade) |
| POST | `/api/{user_id}/conversations/{id}/messages` | Add message |

---

## Development Workflow

### 1. Create New Model

Following the pattern in `backend/src/models/task.py`:

```python
# backend/src/models/conversation.py
from sqlmodel import Field, SQLModel
# ... implement as shown in data-model.md
```

### 2. Register Model in Database

Update `backend/src/database.py`:

```python
def create_tables() -> None:
    from src.models.conversation import Conversation  # noqa: F401
    from src.models.message import Message  # noqa: F401
    # ... existing imports
    SQLModel.metadata.create_all(engine)
```

### 3. Create Service Layer

Following the pattern in `backend/src/services/task_service.py`:

```python
# backend/src/services/conversation_service.py
def create_conversation(db: Session, user_id: UUID, data: ConversationCreate) -> Conversation:
    # ... implementation
```

### 4. Create Pydantic Schemas

Following the pattern in `backend/src/schemas/task.py`:

```python
# backend/src/schemas/conversation.py
class ConversationCreate(BaseModel):
    title: str | None = Field(default=None, max_length=200)
```

### 5. Create API Routes

Following the pattern in `backend/src/api/tasks.py`:

```python
# backend/src/api/conversations.py
router = APIRouter(prefix="/api", tags=["Conversations"])

@router.get("/{user_id}/conversations")
def list_conversations(...):
    # ... implementation
```

### 6. Register Routes

Update `backend/src/main.py`:

```python
from src.api.conversations import router as conversations_router
app.include_router(conversations_router)
```

---

## Testing

### Run All Tests

```bash
uv run pytest
```

### Run Specific Test File

```bash
uv run pytest tests/test_conversations.py -v
```

### Test Coverage

```bash
uv run pytest --cov=src --cov-report=html
```

---

## Key Files Reference

| File | Purpose |
|------|---------|
| `backend/src/models/task.py` | Pattern for new models |
| `backend/src/services/task_service.py` | Pattern for new services |
| `backend/src/schemas/task.py` | Pattern for Pydantic schemas |
| `backend/src/api/tasks.py` | Pattern for API routes |
| `backend/src/database.py` | Database connection and table creation |
| `backend/src/middleware/auth.py` | JWT authentication |

---

## Common Commands

```bash
# Start dev server
uv run uvicorn src.main:app --reload --port 8000

# Run tests
uv run pytest

# Add dependency
uv add <package-name>

# Format code
uv run ruff format .

# Lint code
uv run ruff check .
```

---

## API Documentation

When the server is running:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

---

## Troubleshooting

### Database Connection Failed

1. Check `DATABASE_URL` in `.env`
2. Ensure Neon database is accessible
3. Verify SSL mode: `?sslmode=require`

### JWT Validation Failed

1. Check `BETTER_AUTH_SECRET` matches frontend
2. Ensure token is not expired
3. Verify `Authorization: Bearer <token>` header format

### Table Not Created

1. Ensure model is imported in `create_tables()`
2. Restart server to trigger table creation
3. Check database logs for errors

---

## Next Steps After Phase 1

Once Phase 1 is complete:

1. **Phase 2**: Expose MCP tools for AI agent interaction
2. **Phase 2**: Connect OpenAI Agents SDK
3. **Phase 3**: Add conversational UI to frontend

---

## References

- Spec: `specs/006-ai-todo-core-foundation/spec.md`
- Data Model: `specs/006-ai-todo-core-foundation/data-model.md`
- API Contract: `specs/006-ai-todo-core-foundation/contracts/openapi.yaml`
- Research: `specs/006-ai-todo-core-foundation/research.md`
