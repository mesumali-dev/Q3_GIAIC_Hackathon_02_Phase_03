# Research: Stateless Chat API & Conversation Persistence

**Feature**: 009-stateless-chat-api
**Date**: 2026-01-08
**Status**: Complete

## Research Questions

### 1. How to pass conversation history to OpenAI Agents SDK?

**Decision**: Use `Runner.run()` with a list of input items as the `input` parameter.

**Rationale**: The OpenAI Agents SDK `Runner.run()` method accepts either:
- A single string (for simple user message)
- A list of `TResponseInputItem` objects (for conversation history)

The SDK example shows building multi-turn conversations:
```python
# First turn
result = await Runner.run(agent, "What city is the Golden Gate Bridge in?")

# Second turn - pass history + new message
new_input = result.to_input_list() + [{"role": "user", "content": "What state is it in?"}]
result = await Runner.run(agent, new_input)
```

For our stateless API, we reconstruct the input list from database messages on each request.

**Alternatives Considered**:
- Using SDK's built-in `Session` class for persistence: Rejected because it uses SQLite internally and doesn't integrate with our existing Neon PostgreSQL setup.
- Using `previous_response_id`: Only works with OpenAI's stored conversations, not custom database storage.

### 2. How to capture tool calls from agent execution?

**Decision**: Extract tool calls from `result.new_items` by filtering for `ToolCallItem` types.

**Rationale**: The `RunResult` object contains:
- `new_items: list[RunItem]` - All items generated during the run
- Each item has a `type` field indicating its kind

Tool calls are represented as `ToolCallItem` with `type = "tool_call_item"`:
```python
@dataclass
class ToolCallItem(RunItemBase[Any]):
    raw_item: ToolCallItemTypes  # Contains function name, arguments, etc.
    type: Literal["tool_call_item"] = "tool_call_item"
```

We can filter `result.new_items` for items where `type == "tool_call_item"` to get all tool invocations.

**Alternatives Considered**:
- Using RunHooks for callback-based tracking: More complex and not needed for synchronous execution.
- Parsing raw_responses directly: Lower-level and error-prone.

### 3. How to convert database messages to SDK input format?

**Decision**: Convert database Message records to OpenAI message format dictionaries.

**Rationale**: The SDK accepts messages as dictionaries with `role` and `content` keys:
```python
[
    {"role": "user", "content": "Add a task to buy groceries"},
    {"role": "assistant", "content": "Created task 'buy groceries' (ID: abc123)"},
    {"role": "user", "content": "Mark it as complete"}
]
```

Our database Message model already has `role` and `content` fields, making conversion straightforward.

**Implementation**:
```python
def messages_to_input_list(messages: list[Message]) -> list[dict]:
    return [{"role": m.role, "content": m.content} for m in messages]
```

### 4. Conversation creation strategy

**Decision**: Create conversation implicitly when `conversation_id` is not provided in the request.

**Rationale**: This aligns with FR-003 ("System MUST create a new conversation when conversation_id is not provided or is null") and provides a smooth UX where users don't need to make separate API calls to create conversations.

**Flow**:
1. Request arrives without `conversation_id`
2. Create new Conversation record with `user_id` from JWT
3. Persist user message to new conversation
4. Execute agent
5. Persist assistant response
6. Return `conversation_id` in response for future messages

### 5. Error handling during agent execution

**Decision**: Wrap agent execution in try/except and map exceptions to appropriate HTTP status codes.

**Rationale**: The SDK can raise several exceptions:
- `MaxTurnsExceeded`: Agent took too many turns (504 Gateway Timeout)
- `GuardrailTripwireTriggered`: Safety guardrail triggered (422 Unprocessable Entity)
- `AgentsException`: General SDK errors (502 Bad Gateway)
- `OpenAI API errors`: External service errors (502 Bad Gateway)

**Mapping**:
| Exception | HTTP Status | Message |
|-----------|-------------|---------|
| MaxTurnsExceeded | 504 | "The assistant took too long to respond" |
| GuardrailTripwireTriggered | 422 | "Request was blocked by safety controls" |
| OpenAI API errors | 502 | "AI service temporarily unavailable" |
| Database errors | 500 | "An unexpected error occurred" |

### 6. Message persistence ordering

**Decision**: Persist user message BEFORE agent execution, persist assistant message AFTER.

**Rationale**: This ensures:
1. User message is never lost, even if agent fails
2. Conversation state is recoverable from any failure point
3. Follows FR-006 and FR-010 requirements

**Transaction boundary**: User message and assistant message are persisted in separate database transactions to ensure partial durability.

### 7. Stateless context reconstruction

**Decision**: Reload full conversation history from database on every request.

**Rationale**: This is mandated by FR-007 and FR-015. Benefits:
- Horizontal scalability (any server can handle any request)
- Zero-downtime deployments
- Resilience to server restarts
- Consistent behavior across instances

**Performance consideration**: For conversations with many messages, context window limits are managed by the model (per spec assumptions). Future optimization could add message truncation if needed.

## Technology Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Agent execution | `Runner.run()` async | FastAPI is async-native; avoids blocking |
| Message format | Dict with role/content | SDK-compatible, matches existing schema |
| Tool call extraction | Filter `new_items` | Clean, documented approach |
| Error mapping | HTTP status codes | RESTful, frontend-agnostic |
| Persistence order | User before, assistant after | Durability and recoverability |

## Dependencies Verified

| Dependency | Status | Notes |
|------------|--------|-------|
| OpenAI Agents SDK | Available | Already installed in backend |
| Task agent | Implemented | `backend/src/agent/agent.py` |
| UserContext | Implemented | `backend/src/agent/context.py` |
| Conversation model | Implemented | `backend/src/models/conversation.py` |
| Message model | Implemented | `backend/src/models/message.py` |
| Conversation service | Implemented | `backend/src/services/conversation_service.py` |
| JWT auth middleware | Implemented | `backend/src/middleware/auth.py` |
