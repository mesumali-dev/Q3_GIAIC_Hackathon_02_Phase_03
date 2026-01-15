# Chat API Contracts: Custom Chatbot UI & Threaded Conversations

## Overview

This document defines the API contracts for conversation management in the custom chatbot UI. These contracts build upon the existing `/api/{user_id}/chat` endpoint while adding new endpoints for conversation listing and management.

## Existing Endpoint (to be reused)

### POST /api/{user_id}/chat
Send a message to the AI assistant and receive a response.

#### Request
```yaml
{
  "message": "string (1-50000 chars)",
  "conversation_id": "string (UUID) or null"
}
```

#### Response
```yaml
{
  "conversation_id": "string (UUID)",
  "assistant_message": "string",
  "tool_calls": [
    {
      "tool_name": "string",
      "parameters": {},
      "result": {} or null,
      "success": true or false
    }
  ],
  "created_at": "ISO datetime string"
}
```

#### Status Codes
- 200: Success
- 401: Unauthorized
- 403: Forbidden (user_id mismatch)
- 404: Conversation not found
- 422: Validation error
- 502: AI service unavailable
- 504: Agent execution timeout

## New Endpoints to Implement

### GET /api/{user_id}/conversations
Retrieve a list of all conversations for a user.

#### Headers
```
Authorization: Bearer <JWT_TOKEN>
```

#### Path Parameters
- `user_id`: UUID of the authenticated user (must match JWT)

#### Query Parameters
- `limit`: Number of conversations to return (default: 50, max: 100)
- `offset`: Number of conversations to skip (default: 0)
- `sort`: Sort order (default: "updated_desc", options: "updated_desc", "updated_asc", "created_desc", "created_asc")

#### Response (200 OK)
```yaml
{
  "conversations": [
    {
      "id": "string (UUID)",
      "title": "string or null",
      "created_at": "ISO datetime string",
      "updated_at": "ISO datetime string"
    }
  ],
  "count": integer,
  "has_more": boolean
}
```

#### Status Codes
- 200: Success
- 401: Unauthorized
- 403: Forbidden (user_id mismatch)

### GET /api/{user_id}/conversations/{conversation_id}
Retrieve details of a specific conversation for a user.

#### Headers
```
Authorization: Bearer <JWT_TOKEN>
```

#### Path Parameters
- `user_id`: UUID of the authenticated user (must match JWT)
- `conversation_id`: UUID of the conversation to retrieve

#### Response (200 OK)
```yaml
{
  "id": "string (UUID)",
  "title": "string or null",
  "created_at": "ISO datetime string",
  "updated_at": "ISO datetime string",
  "message_count": integer
}
```

#### Status Codes
- 200: Success
- 401: Unauthorized
- 403: Forbidden (user_id mismatch or conversation doesn't belong to user)
- 404: Conversation not found

### GET /api/{user_id}/conversations/{conversation_id}/messages
Retrieve messages for a specific conversation.

#### Headers
```
Authorization: Bearer <JWT_TOKEN>
```

#### Path Parameters
- `user_id`: UUID of the authenticated user (must match JWT)
- `conversation_id`: UUID of the conversation

#### Query Parameters
- `limit`: Number of messages to return (default: 50, max: 100)
- `offset`: Number of messages to skip (default: 0)
- `sort`: Sort order (default: "asc", options: "asc", "desc")

#### Response (200 OK)
```yaml
{
  "messages": [
    {
      "id": "string (UUID)",
      "role": "string (user|assistant|system)",
      "content": "string",
      "created_at": "ISO datetime string"
    }
  ],
  "count": integer,
  "has_more": boolean
}
```

#### Status Codes
- 200: Success
- 401: Unauthorized
- 403: Forbidden (user_id mismatch or conversation doesn't belong to user)
- 404: Conversation not found

### DELETE /api/{user_id}/conversations/{conversation_id}
Delete a specific conversation.

#### Headers
```
Authorization: Bearer <JWT_TOKEN>
```

#### Path Parameters
- `user_id`: UUID of the authenticated user (must match JWT)
- `conversation_id`: UUID of the conversation to delete

#### Response (204 No Content)
Empty response body on successful deletion.

#### Status Codes
- 204: Success (conversation deleted)
- 401: Unauthorized
- 403: Forbidden (user_id mismatch or conversation doesn't belong to user)
- 404: Conversation not found

### POST /api/{user_id}/conversations
Create a new conversation (alternative to creating implicitly via chat endpoint).

#### Headers
```
Authorization: Bearer <JWT_TOKEN>
Content-Type: application/json
```

#### Path Parameters
- `user_id`: UUID of the authenticated user (must match JWT)

#### Request Body
```yaml
{
  "title": "string (optional, max 200 chars)"
}
```

#### Response (201 Created)
```yaml
{
  "id": "string (UUID)",
  "title": "string or null",
  "created_at": "ISO datetime string",
  "updated_at": "ISO datetime string"
}
```

#### Status Codes
- 201: Created
- 401: Unauthorized
- 403: Forbidden (user_id mismatch)
- 422: Validation error (invalid title)

## Security Requirements

### Authentication
- All endpoints require JWT token in Authorization header
- Token must be valid and not expired
- User ID in JWT must match user_id in path parameter

### Authorization
- Users can only access their own conversations
- Conversation ownership is validated on every request
- Cross-user data access is prohibited

### Input Validation
- UUID parameters must be valid
- String lengths are limited as specified
- Malicious content is sanitized before storage

## Error Response Format

All error responses follow the same format:

```yaml
{
  "detail": "Human-readable error message"
}
```

## Implementation Notes

### Backward Compatibility
- Existing `/api/{user_id}/chat` endpoint remains unchanged
- New endpoints extend functionality without breaking existing clients

### Performance Considerations
- Endpoints support pagination to handle large datasets
- Database indexes should be in place for efficient querying
- Response times should be under 200ms for typical requests

### Data Consistency
- Conversation and message creation/deletion maintains referential integrity
- Updated_at timestamps are automatically managed
- Concurrent modifications are handled at the database level