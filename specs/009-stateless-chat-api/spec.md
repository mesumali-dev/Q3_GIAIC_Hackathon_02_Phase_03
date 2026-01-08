# Feature Specification: Stateless Chat API & Conversation Persistence

**Feature Branch**: `009-stateless-chat-api`
**Created**: 2026-01-08
**Status**: Draft
**Input**: User description: "Phase 4 – Stateless Chat API & Conversation Persistence: Building a stateless chat API endpoint that connects frontend clients to AI agents, reconstructs conversation context from the database, and persists all messages."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Send Message to New Conversation (Priority: P1)

A user sends their first message to the chat API without specifying a conversation ID. The system creates a new conversation, persists the user message, executes the AI agent with the message context, and persists the agent's response. The user receives the AI response along with the new conversation ID for future messages.

**Why this priority**: This is the foundational capability that enables all conversational interactions. Without the ability to start a new conversation and receive a response, no other features have value. This represents the minimum viable capability for the chat API.

**Independent Test**: Can be fully tested by sending a POST request to `/api/{user_id}/chat` with a message and no conversation_id, verifying that: (1) a new conversation is created in the database, (2) the user message is persisted, (3) the AI agent is executed, (4) the assistant response is persisted, (5) the response includes conversation_id and assistant message.

**Acceptance Scenarios**:

1. **Given** an authenticated user with valid JWT, **When** they POST to `/api/{user_id}/chat` with message "Add a task to buy groceries" and no conversation_id, **Then** a new conversation is created, the message is persisted, the agent executes, and the response includes the conversation_id, assistant message content, and any tool calls made
2. **Given** an authenticated user, **When** they POST with an empty message, **Then** the system returns a 422 validation error with a clear message about required content
3. **Given** an unauthenticated request, **When** they POST to the chat endpoint, **Then** the system returns a 401 unauthorized error

---

### User Story 2 - Continue Existing Conversation (Priority: P2)

A user sends a message to an existing conversation by providing the conversation_id. The system loads the full conversation history from the database, provides it as context to the AI agent, persists the new user message and agent response, and returns the response.

**Why this priority**: Conversation continuity is essential for natural multi-turn interactions. Without history context, the AI cannot provide coherent follow-up responses. This is the second most critical operation after starting new conversations.

**Independent Test**: Can be fully tested by creating a conversation with messages, then sending a follow-up message with the conversation_id, verifying that: (1) conversation history is loaded, (2) agent receives full context, (3) new messages are persisted, (4) response reflects awareness of prior messages.

**Acceptance Scenarios**:

1. **Given** an existing conversation where user previously said "Add a task to buy groceries" and received confirmation, **When** the user sends "Mark it as complete" with the same conversation_id, **Then** the agent understands context from history and attempts to complete the groceries task
2. **Given** a conversation_id that doesn't exist, **When** the user sends a message with that conversation_id, **Then** the system returns a 404 not found error
3. **Given** a conversation_id belonging to a different user, **When** the authenticated user sends a message with that conversation_id, **Then** the system returns a 403 forbidden error

---

### User Story 3 - Resume Conversation After Server Restart (Priority: P3)

A user resumes a conversation after the server has been restarted. Because the system is stateless and stores all conversation state in the database, the conversation continues seamlessly with full history preserved.

**Why this priority**: Statelessness ensures production reliability (horizontal scaling, zero-downtime deploys). This validates the core architectural constraint that no in-memory state exists.

**Independent Test**: Can be fully tested by: (1) creating a conversation and adding messages, (2) simulating server restart (clearing any caches), (3) sending a follow-up message, (4) verifying the agent has full historical context.

**Acceptance Scenarios**:

1. **Given** a conversation with 5 prior messages created before server restart, **When** the user sends a new message after restart, **Then** the agent response demonstrates awareness of all 5 prior messages
2. **Given** any point in time, **When** the same request is sent multiple times, **Then** the server reconstructs identical conversation context from the database each time
3. **Given** multiple server instances, **When** requests for the same conversation hit different instances, **Then** all instances produce consistent context from the shared database

---

### User Story 4 - Receive Tool Call Information (Priority: P4)

When the AI agent invokes MCP tools during response generation, the chat API response includes information about which tools were called and their results. This enables frontend transparency and debugging.

**Why this priority**: Tool call visibility supports frontend UX (showing "Creating task..." states) and debugging. This depends on core chat functionality working first.

**Independent Test**: Can be fully tested by sending a task-related command, verifying the response includes tool_calls array with tool names and parameters.

**Acceptance Scenarios**:

1. **Given** the user sends "Add a task to call mom", **When** the agent invokes the add_task tool, **Then** the response includes a tool_calls array containing the add_task invocation with parameters
2. **Given** the user sends "What are my tasks?", **When** the agent invokes list_tasks, **Then** the response includes the list_tasks tool call with the returned task list
3. **Given** the user sends a message that requires no tool calls (e.g., "Hello"), **When** the agent responds without tools, **Then** the response tool_calls array is empty

---

### User Story 5 - Handle Agent Errors Gracefully (Priority: P5)

When the AI agent encounters errors (tool failures, timeout, model errors), the system handles them gracefully, persists appropriate error information, and returns user-friendly error responses.

**Why this priority**: Robust error handling is essential for production readiness but depends on happy-path flows working first.

**Independent Test**: Can be fully tested by triggering various error conditions and verifying appropriate responses are returned and logged.

**Acceptance Scenarios**:

1. **Given** an MCP tool returns an error (e.g., task not found), **When** the agent processes the error, **Then** the response includes a user-friendly error message without exposing internal details
2. **Given** the agent times out during execution, **When** the timeout occurs, **Then** the system returns a 504 timeout error with appropriate message
3. **Given** the OpenAI API returns an error, **When** the error occurs, **Then** the system returns a 502 bad gateway error without exposing API keys or internal errors

---

### Edge Cases

- What happens when the message content exceeds the maximum length (50,000 characters)?
- How does the system handle concurrent requests for the same conversation?
- What happens if the database is unavailable during message persistence?
- How does the system handle a conversation with hundreds of messages (context window limits)?
- What happens if the agent response is empty?
- How does the system handle special characters, emojis, or non-ASCII content in messages?
- What happens if user_id in the path doesn't match the JWT user_id?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST implement a POST `/api/{user_id}/chat` endpoint that accepts messages and returns AI responses
- **FR-002**: System MUST accept a request body containing `message` (required) and `conversation_id` (optional)
- **FR-003**: System MUST create a new conversation when `conversation_id` is not provided or is null
- **FR-004**: System MUST validate that the provided `conversation_id` exists and belongs to the authenticated user
- **FR-005**: System MUST load the full conversation history from the database when `conversation_id` is provided
- **FR-006**: System MUST persist the user message to the database BEFORE executing the agent
- **FR-007**: System MUST reconstruct agent context from database on every request (no in-memory conversation state)
- **FR-008**: System MUST execute the AI agent with the conversation history as context
- **FR-009**: System MUST capture all MCP tool calls invoked by the agent during execution
- **FR-010**: System MUST persist the assistant response to the database AFTER agent execution completes
- **FR-011**: System MUST update the conversation's `updated_at` timestamp after each message
- **FR-012**: System MUST return a response containing `conversation_id`, `assistant_message`, and `tool_calls` array
- **FR-013**: System MUST scope all database operations by the authenticated user_id from JWT
- **FR-014**: System MUST return appropriate HTTP error codes (401, 403, 404, 422, 500, 502, 504)
- **FR-015**: System MUST maintain zero server-side session storage or in-memory conversation cache
- **FR-016**: System MUST handle agent errors gracefully without exposing internal error details
- **FR-017**: System MUST convert database message history to the format expected by the OpenAI Agents SDK
- **FR-018**: All message content MUST be validated for length and format before persistence
- **FR-019**: System MUST support message roles: "user" for incoming messages, "assistant" for agent responses

### Key Entities

- **Chat Request**: Incoming request with `message` (required string) and `conversation_id` (optional UUID). Represents a single user turn in the conversation.

- **Chat Response**: Outgoing response with `conversation_id` (UUID), `assistant_message` (string content), `tool_calls` (array of tool invocations), and `created_at` (timestamp). Represents the complete result of processing a chat request.

- **Tool Call**: Information about an MCP tool invocation with `tool_name` (string), `parameters` (object), `result` (object or null), and `success` (boolean). Captured during agent execution for frontend visibility.

- **Conversation** (existing): Chat session container with `id`, `user_id`, `title`, `created_at`, `updated_at`. Links messages together for history reconstruction.

- **Message** (existing): Individual message in a conversation with `id`, `conversation_id`, `role`, `content`, `created_at`. Persisted before and after agent execution.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can send a message and receive an AI response in a single request-response cycle
- **SC-002**: Conversations persist across requests and are fully resumable with complete history
- **SC-003**: Server maintains zero in-memory conversational state (verified by restart test)
- **SC-004**: Identical message sequences to the same conversation produce consistent context reconstruction
- **SC-005**: Chat API response time is within 10 seconds for standard operations (single message, agent execution, persistence)
- **SC-006**: 100% of user messages are persisted before agent execution begins
- **SC-007**: 100% of assistant responses are persisted after agent execution completes
- **SC-008**: Tool calls are captured and returned in 100% of responses where tools were invoked
- **SC-009**: All error conditions return appropriate status codes without exposing internal details
- **SC-010**: Chat API endpoint is ready for frontend integration (documented request/response schema)

### Assumptions

- AI agent from Phase 3 (008-ai-agent-mcp-orchestration) is fully operational
- MCP tools from Phase 2 (007-mcp-stateless-tools) are working correctly
- Conversation and Message models from Phase 1 are implemented with database migrations applied
- JWT authentication middleware is functional and provides user_id
- OpenAI API is accessible with valid credentials configured
- Database connection is stable and performant
- Context window limitations are managed by the model (no explicit truncation in Phase 4)

### Out of Scope

- Frontend ChatKit UI (reserved for Phase 5)
- Streaming/SSE responses (synchronous only in Phase 4)
- Multi-agent orchestration or agent handoffs
- Long-term memory, summarization, or context window management
- Notifications, reminders, or background job processing
- Message editing or deletion
- Conversation title auto-generation from content
- Rate limiting or quota management for chat requests
- WebSocket connections for real-time updates
- File attachments or multimedia messages
- Message reactions or threading

### Dependencies

- **External**: OpenAI API access with valid API key for model inference
- **External**: Neon PostgreSQL database for conversation/message persistence
- **Internal**: AI agent from Phase 3 (`task_agent` with MCP tool integration)
- **Internal**: MCP tools: `add_task`, `list_tasks`, `complete_task`, `delete_task`, `update_task`
- **Internal**: Conversation and Message models with SQLModel ORM
- **Internal**: Conversation service functions: `create_conversation`, `get_conversation`, `get_messages`, `add_message`
- **Internal**: JWT authentication middleware providing `user_id`
