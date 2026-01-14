# Research: AI Agent & MCP Tool Orchestration

**Feature**: 008-ai-agent-mcp-orchestration
**Phase**: Phase 0 - Research
**Created**: 2026-01-08

## Research Summary

This document captures research findings for integrating the OpenAI Agents SDK with existing MCP tools to create a natural language task management agent.

---

## 1. OpenAI Agents SDK Integration

### Decision: Use `openai-agents` Python Package

**Rationale**:
- Official package name is `openai-agents` (installed via `pip install openai-agents`)
- Import pattern: `from agents import Agent, Runner, function_tool`
- Compatible with Python 3.11+ (matches backend environment)
- Provides declarative agent definition with `Agent` class
- Supports typed context via generics: `Agent[TContext]`
- Built-in `Runner.run_sync()` for synchronous execution (ideal for Phase 3 without streaming)

**Alternatives Considered**:
- LangChain: Rejected due to complexity overhead for single-agent use case
- Custom implementation: Rejected due to maintenance burden and reinventing wheel
- OpenAI Functions API directly: Rejected because Agents SDK provides cleaner abstraction

**Code Pattern**:
```python
from agents import Agent, Runner, function_tool
from dataclasses import dataclass

@dataclass
class UserContext:
    user_id: str

agent = Agent[UserContext](
    name="TaskManager",
    instructions="You are a task management assistant...",
    tools=[add_task_tool, list_tasks_tool, complete_task_tool, delete_task_tool, update_task_tool],
)

result = Runner.run_sync(agent, user_input, context=user_context)
```

---

## 2. Function Tool Pattern

### Decision: Wrap MCP Tools with `@function_tool` Decorator

**Rationale**:
- OpenAI Agents SDK uses `@function_tool` decorator to define tools
- Tools receive `RunContextWrapper[TContext]` for accessing user context
- MCP tools are already async functions with standardized input/output
- Wrapper tools will call MCP tools directly and return their results

**Alternatives Considered**:
- Direct MCP tool registration: Rejected because Agents SDK needs its own tool format
- Code generation for tool wrappers: Rejected due to complexity; manual wrappers are cleaner
- Subclassing MCP tools: Rejected because `@function_tool` decorator is simpler

**Code Pattern**:
```python
from agents import function_tool, RunContextWrapper

@function_tool
async def add_task_tool(
    ctx: RunContextWrapper[UserContext],
    title: str,
    description: str | None = None
) -> str:
    """Add a new task for the user."""
    result = await add_task(ctx.context.user_id, title, description)
    if result["success"]:
        return f"Created task '{result['title']}' with ID {result['task_id']}"
    return f"Error: {result['error']['message']}"
```

---

## 3. Agent System Prompt Design

### Decision: Structured Role-Based System Prompt

**Rationale**:
- Clear role definition helps LLM understand its purpose
- Behavioral rules prevent undesirable actions (e.g., database access)
- Tool usage guidelines improve intent-to-tool mapping accuracy
- Error handling instructions ensure graceful responses

**Alternatives Considered**:
- Minimal prompt: Rejected because LLM needs guidance for consistent behavior
- Few-shot examples in prompt: Considered but tools reduce need for examples
- JSON schema constraints: Rejected because natural language instructions are more flexible

**System Prompt Structure**:
```
You are a task management assistant. You help users create, view, complete, update, and delete their tasks.

CAPABILITIES:
- Create new tasks with add_task_tool
- List all tasks with list_tasks_tool
- Mark tasks as complete with complete_task_tool
- Delete tasks with delete_task_tool
- Update task details with update_task_tool

RULES:
1. ALWAYS use tools to perform task operations. NEVER access the database directly.
2. When the user's intent is unclear, ask for clarification before acting.
3. After performing an action, confirm what was done with relevant details.
4. If a tool returns an error, explain the issue in user-friendly terms.
5. Only handle task-related requests. Politely decline other requests.
6. For ambiguous task references, list available tasks and ask which one.

RESPONSE FORMAT:
- Be concise but informative
- Include task IDs when relevant
- Format task lists clearly
```

---

## 4. Context Management

### Decision: Dataclass-Based User Context

**Rationale**:
- `RunContextWrapper[TContext]` passes context to function tools
- Dataclass provides type safety and simple structure
- Context contains `user_id` for scoping all tool operations
- Stateless per invocation (no session storage in Phase 3)

**Alternatives Considered**:
- Pydantic model: Viable but dataclass is simpler for single field
- TypedDict: Rejected due to less IDE support
- Plain dict: Rejected due to lack of type safety

**Code Pattern**:
```python
from dataclasses import dataclass

@dataclass
class UserContext:
    user_id: str  # UUID string from authenticated JWT

# Usage
context = UserContext(user_id="550e8400-e29b-41d4-a716-446655440000")
result = Runner.run_sync(agent, "Show my tasks", context=context)
```

---

## 5. Error Propagation Strategy

### Decision: Tool-Level Error Translation

**Rationale**:
- MCP tools return structured error responses with code and message
- Function tools translate errors into human-readable strings
- Agent receives string output and includes it in response
- Internal details (stack traces, database errors) are hidden

**Alternatives Considered**:
- Raise exceptions from tools: Rejected because agent can't handle Python exceptions gracefully
- Return structured errors to agent: Viable but string responses are simpler
- Global error handler: Rejected because each tool has different error semantics

**Error Flow**:
```
MCP Tool → {"success": false, "error": {"code": "TASK_NOT_FOUND", "message": "..."}}
    ↓
Function Tool → "Error: The specified task was not found."
    ↓
Agent → "I couldn't find that task. Would you like to see your current tasks?"
```

---

## 6. Single-Agent Architecture

### Decision: Single Task-Management Agent (No Multi-Agent)

**Rationale**:
- Feature scope is limited to CRUD operations on tasks
- All five operations share the same context (user_id)
- Multi-agent handoffs would add complexity without benefit
- Spec explicitly excludes multi-agent workflows

**Alternatives Considered**:
- Specialist agents per operation: Rejected due to unnecessary complexity
- Triage agent with sub-agents: Rejected because single agent handles scope well
- Agent-as-tool pattern: Reserved for future multi-agent phases

**Architecture**:
```
User Input → Task Management Agent → Function Tools → MCP Tools → Database
                    ↓
               Agent Response
```

---

## 7. Task Identification Strategy

### Decision: List-First for Ambiguous References

**Rationale**:
- Users may reference tasks by title, position, or partial match
- Agent should first call `list_tasks` to get available tasks
- Then match user's description to task IDs from list
- For ambiguous matches, ask user to clarify

**Alternatives Considered**:
- Search/filter tool: Not available in Phase 2 MCP tools
- Always require task ID: Rejected due to poor UX
- Fuzzy matching in agent: LLM can naturally match partial titles

**Flow for "Complete the groceries task"**:
1. Agent calls `list_tasks_tool` to get all tasks
2. Agent finds task with title containing "groceries"
3. Agent calls `complete_task_tool` with matched task_id
4. If multiple matches, agent lists options and asks user to choose

---

## 8. Synchronous Execution

### Decision: Use `Runner.run_sync()` for Phase 3

**Rationale**:
- Phase 3 has no streaming requirements
- Synchronous execution simplifies testing and debugging
- API wrapper in Phase 4 can switch to `Runner.run()` if needed
- Typical operations complete within 5 seconds

**Alternatives Considered**:
- Async from start: More complex for no immediate benefit
- Streaming: Not needed until frontend integration

**Code Pattern**:
```python
from agents import Runner

result = Runner.run_sync(agent, user_input, context=context)
response = result.final_output  # String response to user
```

---

## 9. Testing Strategy

### Decision: Mock MCP Tools for Unit Tests

**Rationale**:
- Agent behavior can be tested with mocked tool responses
- Integration tests can use real MCP tools with test database
- Tool invocation can be verified through mock call assertions

**Test Categories**:
1. **Intent Classification**: Verify correct tool is called for each intent
2. **Parameter Extraction**: Verify title/description extracted correctly
3. **Error Handling**: Verify graceful responses for tool errors
4. **Ambiguity Handling**: Verify clarification requests

---

## 10. Environment Configuration

### Decision: Use OPENAI_API_KEY Environment Variable

**Rationale**:
- OpenAI Agents SDK reads `OPENAI_API_KEY` automatically
- Consistent with existing `.env` pattern in project
- No hardcoded credentials

**Required Variables**:
```bash
OPENAI_API_KEY=sk-...          # For OpenAI API access
OPENAI_DEFAULT_MODEL=gpt-4o    # Optional: default model
```

---

## Dependencies Summary

| Package | Version | Purpose |
|---------|---------|---------|
| openai-agents | Latest | OpenAI Agents SDK |
| openai | ^1.0.0 | Required by agents SDK |
| Existing: structlog | - | Logging |
| Existing: pydantic | - | Validation |

---

## Constitution Alignment

| Principle | Alignment |
|-----------|-----------|
| Security by Default | ✅ user_id from context, no direct DB access |
| Separation of Concerns | ✅ Agent → Tools → MCP → Database |
| Spec-Driven Development | ✅ All decisions traced to requirements |
| Error Handling | ✅ Structured errors, user-friendly messages |

---

## Next Steps

1. Generate `data-model.md` with agent and context entities
2. Generate `quickstart.md` with development setup instructions
3. Proceed to Phase 1 design artifacts
