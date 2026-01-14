# Quickstart: Stateless Chat API

**Feature**: 009-stateless-chat-api
**Date**: 2026-01-08

## Prerequisites

- Backend running (`uv run uvicorn src.main:app --reload --port 8000`)
- Valid JWT token (from Better Auth login)
- OpenAI API key configured in `.env`

## API Endpoint

```
POST /api/{user_id}/chat
Authorization: Bearer <JWT_TOKEN>
Content-Type: application/json
```

## Usage Examples

### 1. Start a New Conversation

```bash
curl -X POST "http://localhost:8000/api/${USER_ID}/chat" \
  -H "Authorization: Bearer ${JWT_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Add a task to buy groceries"
  }'
```

**Response:**
```json
{
  "conversation_id": "550e8400-e29b-41d4-a716-446655440000",
  "assistant_message": "Created task 'buy groceries' (ID: abc123)",
  "tool_calls": [
    {
      "tool_name": "add_task",
      "parameters": {"title": "buy groceries"},
      "result": {"success": true, "task_id": "abc123"},
      "success": true
    }
  ],
  "created_at": "2026-01-08T12:00:00Z"
}
```

### 2. Continue an Existing Conversation

```bash
curl -X POST "http://localhost:8000/api/${USER_ID}/chat" \
  -H "Authorization: Bearer ${JWT_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Mark it as complete",
    "conversation_id": "550e8400-e29b-41d4-a716-446655440000"
  }'
```

**Response:**
```json
{
  "conversation_id": "550e8400-e29b-41d4-a716-446655440000",
  "assistant_message": "Marked 'buy groceries' as complete.",
  "tool_calls": [
    {
      "tool_name": "complete_task",
      "parameters": {"task_id": "abc123"},
      "result": {"success": true, "is_completed": true},
      "success": true
    }
  ],
  "created_at": "2026-01-08T12:01:00Z"
}
```

### 3. List Tasks

```bash
curl -X POST "http://localhost:8000/api/${USER_ID}/chat" \
  -H "Authorization: Bearer ${JWT_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What are my tasks?",
    "conversation_id": "550e8400-e29b-41d4-a716-446655440000"
  }'
```

### 4. Simple Greeting (No Tool Calls)

```bash
curl -X POST "http://localhost:8000/api/${USER_ID}/chat" \
  -H "Authorization: Bearer ${JWT_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Hello!"
  }'
```

**Response:**
```json
{
  "conversation_id": "660e8400-e29b-41d4-a716-446655440001",
  "assistant_message": "Hello! I can help you manage your tasks. What would you like to do?",
  "tool_calls": [],
  "created_at": "2026-01-08T12:02:00Z"
}
```

## Error Responses

### Missing Authentication (401)

```bash
curl -X POST "http://localhost:8000/api/${USER_ID}/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello"}'
```

```json
{"detail": "Not authenticated"}
```

### User ID Mismatch (403)

```json
{"detail": "Access denied"}
```

### Conversation Not Found (404)

```json
{"detail": "Conversation not found"}
```

### Empty Message (422)

```bash
curl -X POST "http://localhost:8000/api/${USER_ID}/chat" \
  -H "Authorization: Bearer ${JWT_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"message": ""}'
```

```json
{
  "detail": [
    {
      "loc": ["body", "message"],
      "msg": "String should have at least 1 character",
      "type": "string_too_short"
    }
  ]
}
```

## Testing the Stateless Property

### Test 1: Server Restart Resilience

1. Start a conversation and note the `conversation_id`
2. Restart the server (`Ctrl+C` and `uv run uvicorn...`)
3. Continue the conversation with the same `conversation_id`
4. Verify the assistant has context from previous messages

### Test 2: Concurrent Requests

Send multiple requests to the same conversation simultaneously:

```bash
# Terminal 1
curl -X POST "http://localhost:8000/api/${USER_ID}/chat" \
  -d '{"message": "Add task A", "conversation_id": "..."}'

# Terminal 2
curl -X POST "http://localhost:8000/api/${USER_ID}/chat" \
  -d '{"message": "Add task B", "conversation_id": "..."}'
```

Both requests should succeed and both messages should be persisted.

## Key Behaviors

1. **New conversation**: Omit `conversation_id` → new conversation created
2. **Continue conversation**: Include `conversation_id` → history loaded from DB
3. **Stateless**: No server-side session storage; context reconstructed per request
4. **Tool visibility**: All MCP tool calls returned in `tool_calls` array
5. **Message persistence**: User message persisted before agent; assistant after

## File Structure (Implementation)

```
backend/src/
├── api/
│   └── chat.py              # Chat endpoint router
├── services/
│   └── chat_service.py      # Chat business logic (NEW)
├── schemas/
│   └── chat.py              # ChatRequest/ChatResponse (NEW)
└── agent/
    ├── agent.py             # Task agent (existing)
    └── runner.py            # Agent execution helper (NEW)
```
