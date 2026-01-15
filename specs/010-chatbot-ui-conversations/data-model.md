# Data Model: Custom Chatbot UI & Threaded Conversations

## Overview

This document defines the data models for the custom chatbot UI with threaded conversations. The models leverage existing backend conversation and message entities while defining frontend-specific representations.

## Backend Data Models (Already Defined)

### Conversation Entity
```python
class Conversation(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(index=True, foreign_key="users.id", nullable=False)
    title: str | None = Field(default=None, max_length=200)
    created_at: datetime
    updated_at: datetime
```

### Message Entity
```python
class Message(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    conversation_id: UUID = Field(index=True, foreign_key="conversations.id", nullable=False)
    role: str = Field(max_length=20)  # 'user', 'assistant', 'system'
    content: str = Field(max_length=50000)
    created_at: datetime
```

## Frontend Data Models

### ConversationSummary (for thread list)
```typescript
interface ConversationSummary {
  id: string;                    // UUID from backend
  title: string | null;          // Optional title/summary
  lastMessage: string | null;    // Preview of last message content
  updatedAt: string;             // ISO date string
  createdAt: string;             // ISO date string
}
```

### ConversationDetail (for active conversation)
```typescript
interface ConversationDetail {
  id: string;                    // UUID from backend
  title: string | null;          // Optional title/summary
  messages: MessageItem[];       // Ordered list of messages
  createdAt: string;             // ISO date string
  updatedAt: string;             // ISO date string
}
```

### MessageItem (for display)
```typescript
interface MessageItem {
  id: string;                    // UUID from backend or temporary ID for unsent messages
  conversationId: string;        // Reference to parent conversation
  role: 'user' | 'assistant';    // Role determines display styling
  content: string;               // Message text content
  createdAt: string;             // ISO date string
  status: 'sent' | 'sending' | 'failed';  // For UI state management
}
```

### ChatRequest (frontend to backend)
```typescript
interface ChatRequest {
  message: string;               // User's message content (1-50000 chars)
  conversation_id?: string | null;  // Existing conversation ID or null for new
}
```

### ChatResponse (backend to frontend)
```typescript
interface ChatResponse {
  conversation_id: string;       // Conversation ID (new or existing)
  assistant_message: string;     // AI response content
  tool_calls: ToolCall[];        // List of tool invocations (can be empty)
  created_at: string;            // Response timestamp
}

interface ToolCall {
  tool_name: string;             // Name of the invoked MCP tool
  parameters: Record<string, any>;  // Parameters passed to the tool
  result: Record<string, any> | null;  // Tool result (null if failed)
  success: boolean;              // Whether the tool call succeeded
}
```

## API Response Models

### GetConversationsResponse
```typescript
interface GetConversationsResponse {
  conversations: ConversationSummary[];
  count: number;                 // Total number of conversations
}
```

### GetMessagesResponse
```typescript
interface GetMessagesResponse {
  messages: MessageItem[];
  count: number;                 // Total number of messages in conversation
  hasNext: boolean;             // Whether more messages are available
}
```

## Validation Rules

### Backend Validation (Already Implemented)
- Conversation IDs must be valid UUIDs
- Message length must be 1-50000 characters
- Role must be 'user', 'assistant', or 'system'
- User ID in JWT must match conversation ownership
- Conversation must belong to authenticated user

### Frontend Validation
- Message input should trim whitespace
- Prevent duplicate message sending
- Validate conversation ID format before API calls
- Handle empty responses gracefully

## State Management Models

### ChatUIState (Frontend)
```typescript
interface ChatUIState {
  activeConversationId: string | null;     // Currently selected conversation
  conversations: Map<string, ConversationSummary>;  // Cached conversation list
  messages: Map<string, MessageItem[]>;     // Cached messages by conversation ID
  isLoading: boolean;                      // Global loading state
  error: string | null;                    // Global error state
  composing: boolean;                      // Whether user is typing
}
```

## Relationships

### Conversation to Messages
- One conversation contains many messages
- Messages are ordered chronologically by created_at timestamp
- Foreign key relationship enforced at database level

### User to Conversations
- One user owns many conversations
- Access control enforced via user_id validation against JWT
- No cross-user access allowed

## Indexing Strategy

### Backend Database Indexes (Already Implemented)
- conversations.user_id: Index for user-based queries
- conversations.updated_at: Index for sorting by recency
- messages.conversation_id: Index for conversation-based queries
- messages.created_at: Index for chronological ordering

### Frontend Caching Strategy
- Cache conversation summaries in memory
- Cache individual conversation messages when active
- Invalidate cache on mutation operations
- Implement cache size limits to prevent memory bloat