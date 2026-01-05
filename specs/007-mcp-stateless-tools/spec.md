# Feature Specification: MCP Stateless Tool Layer

**Feature Branch**: `007-mcp-stateless-tools`
**Created**: 2026-01-05
**Status**: Draft
**Input**: User description: "Project: AI-Native Conversational Todo Application - Phase: Phase 2 – MCP Server & Stateless Tool Layer. Building a stateless MCP server using the Official MCP SDK that exposes task operations as tools and persists all state changes to the database."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - AI Agent Task Creation (Priority: P1)

An AI agent receives a user request to create a new task and invokes the MCP server's `add_task` tool to persist the task to the database. The tool returns confirmation of task creation with the generated task ID.

**Why this priority**: This is the foundational operation that enables all AI agent interactions. Without task creation, no other operations have value. This represents the minimum viable capability for the MCP tool layer.

**Independent Test**: Can be fully tested by invoking the `add_task` MCP tool with valid task data (title, description, user_id) and verifying that: (1) the task is persisted in the database, (2) a task ID is returned, (3) the tool call is stateless and repeatable.

**Acceptance Scenarios**:

1. **Given** an authenticated user ID and valid task data, **When** the AI agent invokes `add_task` with title "Buy groceries" and user_id "user123", **Then** a new task is created in the database and the tool returns the task ID and confirmation
2. **Given** an authenticated user ID and minimal task data, **When** the AI agent invokes `add_task` with only title "Call mom" and user_id "user123", **Then** a new task is created with default values for optional fields and returns success
3. **Given** invalid input data, **When** the AI agent invokes `add_task` with missing title or user_id, **Then** the tool returns a validation error with clear error message

---

### User Story 2 - AI Agent Task Retrieval (Priority: P2)

An AI agent needs to show a user their current tasks and invokes the MCP server's `list_tasks` tool to retrieve all tasks for a specific user. The tool queries the database and returns a list of tasks scoped to that user.

**Why this priority**: Task retrieval is essential for users to view their existing tasks and for AI agents to provide context-aware responses. This is the second most critical operation after task creation.

**Independent Test**: Can be fully tested by creating several tasks for a user, then invoking `list_tasks` with that user_id and verifying that: (1) all tasks for that user are returned, (2) tasks from other users are not included, (3) the operation is stateless.

**Acceptance Scenarios**:

1. **Given** a user with 5 existing tasks, **When** the AI agent invokes `list_tasks` with user_id "user123", **Then** all 5 tasks are returned with complete task details
2. **Given** a user with no tasks, **When** the AI agent invokes `list_tasks` with user_id "user456", **Then** an empty list is returned without errors
3. **Given** multiple users with tasks, **When** the AI agent invokes `list_tasks` with user_id "user123", **Then** only tasks belonging to "user123" are returned, not other users' tasks

---

### User Story 3 - AI Agent Task Completion (Priority: P3)

An AI agent receives a request to mark a task as complete and invokes the MCP server's `complete_task` tool to update the task status in the database. The tool updates the completion state and timestamp.

**Why this priority**: Marking tasks complete is a core workflow but depends on tasks existing first (P1) and being retrievable (P2). This completes the basic task lifecycle.

**Independent Test**: Can be fully tested by creating a task, invoking `complete_task` with the task ID and user_id, and verifying that: (1) the task status is updated in the database, (2) completion timestamp is recorded, (3) subsequent retrievals show the completed status.

**Acceptance Scenarios**:

1. **Given** an incomplete task with ID "task789" owned by "user123", **When** the AI agent invokes `complete_task` with task_id "task789" and user_id "user123", **Then** the task is marked complete in the database and returns success
2. **Given** a task that doesn't exist, **When** the AI agent invokes `complete_task` with task_id "invalid999", **Then** the tool returns a "task not found" error
3. **Given** a task owned by a different user, **When** the AI agent invokes `complete_task` with task_id "task789" and user_id "user999", **Then** the tool returns an authorization error preventing the update

---

### User Story 4 - AI Agent Task Deletion (Priority: P4)

An AI agent receives a request to delete a task and invokes the MCP server's `delete_task` tool to remove the task from the database permanently.

**Why this priority**: Task deletion is important for task management but is less critical than creation, retrieval, and completion. Users need to be able to remove tasks, but this is a secondary workflow.

**Independent Test**: Can be fully tested by creating a task, invoking `delete_task` with the task ID and user_id, and verifying that: (1) the task is removed from the database, (2) subsequent list operations don't include the deleted task, (3) attempts to access the deleted task return appropriate errors.

**Acceptance Scenarios**:

1. **Given** an existing task with ID "task101" owned by "user123", **When** the AI agent invokes `delete_task` with task_id "task101" and user_id "user123", **Then** the task is permanently removed from the database and returns success
2. **Given** a non-existent task, **When** the AI agent invokes `delete_task` with task_id "invalid888", **Then** the tool returns a "task not found" error
3. **Given** a task owned by a different user, **When** the AI agent invokes `delete_task` with task_id "task101" and user_id "user999", **Then** the tool returns an authorization error preventing deletion

---

### User Story 5 - AI Agent Task Modification (Priority: P5)

An AI agent receives a request to update task details (title, description, priority, etc.) and invokes the MCP server's `update_task` tool to modify the task in the database.

**Why this priority**: Task updates enable rich task management but are the least critical core operation. Users can accomplish most goals with create/list/complete/delete operations.

**Independent Test**: Can be fully tested by creating a task, invoking `update_task` with modified fields, and verifying that: (1) only specified fields are updated in the database, (2) unchanged fields remain intact, (3) the operation is atomic and stateless.

**Acceptance Scenarios**:

1. **Given** an existing task with title "Old title" owned by "user123", **When** the AI agent invokes `update_task` with task_id "task202", user_id "user123", and new title "New title", **Then** the task title is updated in the database while other fields remain unchanged
2. **Given** an existing task, **When** the AI agent invokes `update_task` with multiple field updates (title, description, priority), **Then** all specified fields are updated atomically
3. **Given** invalid update data, **When** the AI agent invokes `update_task` with empty title or invalid priority value, **Then** the tool returns a validation error and no changes are persisted

---

### Edge Cases

- What happens when an MCP tool is invoked with a user_id that doesn't exist in the system?
- How does the system handle concurrent tool invocations attempting to modify the same task?
- What happens if database connection fails during a tool invocation?
- How does the system handle malformed input schemas (missing required fields, wrong data types)?
- What happens when `list_tasks` is called for a user with thousands of tasks (pagination/performance)?
- How does the system handle duplicate `add_task` calls with identical data within milliseconds?
- What happens if a tool invocation times out during database operation?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST expose an MCP server using the Official MCP SDK that is accessible to external clients
- **FR-002**: System MUST implement `add_task` MCP tool that accepts title, description (optional), priority (optional), due_date (optional), and user_id, and persists the task to the database
- **FR-003**: System MUST implement `list_tasks` MCP tool that accepts user_id and returns all tasks for that user from the database
- **FR-004**: System MUST implement `complete_task` MCP tool that accepts task_id and user_id, updates the task completion status in the database, and records completion timestamp
- **FR-005**: System MUST implement `delete_task` MCP tool that accepts task_id and user_id, and removes the task from the database
- **FR-006**: System MUST implement `update_task` MCP tool that accepts task_id, user_id, and optional fields (title, description, priority, due_date), and updates only the specified fields in the database
- **FR-007**: All MCP tools MUST be completely stateless with no in-memory state storage between invocations
- **FR-008**: All MCP tools MUST persist state changes directly to the Neon PostgreSQL database via SQLModel ORM
- **FR-009**: All MCP tools MUST scope operations by user_id to ensure data isolation between users
- **FR-010**: All MCP tools MUST validate input parameters and return clear error messages for invalid inputs (missing required fields, invalid data types, constraint violations)
- **FR-011**: All MCP tools MUST handle "task not found" scenarios by returning a structured error response
- **FR-012**: All MCP tools MUST handle authorization failures (user attempting to access another user's tasks) by returning an authorization error
- **FR-013**: All MCP tools MUST handle database connection failures gracefully and return appropriate error responses
- **FR-014**: MCP tool input schemas MUST be clearly defined with required and optional parameters
- **FR-015**: MCP tool output schemas MUST be consistent and include success indicators and data payloads or error details
- **FR-016**: System MUST use existing service/repository layer components for database operations (no direct database access in MCP tools)
- **FR-017**: System MUST ensure MCP tools have no side effects beyond database writes (no file system changes, no external API calls, no email sending)
- **FR-018**: System MUST provide example tool invocation payloads for testing each MCP tool
- **FR-019**: System MUST document MCP tool contracts including input/output schemas and error conditions

### Key Entities

- **Task**: Represents a user's todo item with attributes: task_id (unique identifier), user_id (owner), title (required), description (optional), priority (optional, e.g., low/medium/high), due_date (optional), completed (boolean), completion_timestamp (timestamp when marked complete), created_at (creation timestamp), updated_at (last modification timestamp)

- **MCP Tool Invocation**: Represents a single stateless tool call with attributes: tool_name (add_task/list_tasks/complete_task/delete_task/update_task), input_parameters (user_id and tool-specific params), output_result (success data or error details), invocation_timestamp

- **User Context**: Represents the authenticated user context for tool operations with attributes: user_id (unique identifier for scoping operations). Note: user authentication is handled externally; MCP tools receive authenticated user_id.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: All five MCP tools (`add_task`, `list_tasks`, `complete_task`, `delete_task`, `update_task`) are operational and invocable by external MCP clients
- **SC-002**: Tool invocations complete successfully within 500ms for standard operations (single task create/update/delete/retrieve)
- **SC-003**: `list_tasks` returns results within 1 second for users with up to 1000 tasks
- **SC-004**: 100% of tool invocations persist state changes to the database with no in-memory state retention
- **SC-005**: 100% of invalid tool invocations (missing required params, invalid data types) return clear validation errors without causing system failures
- **SC-006**: 100% of operations are correctly scoped by user_id with no cross-user data leakage
- **SC-007**: Tool layer operates independently of the API server and can be tested in isolation
- **SC-008**: MCP server remains stateless across restarts with all state recovered from database
- **SC-009**: All error conditions (task not found, authorization failure, database error) return structured error responses suitable for AI agent consumption
- **SC-010**: Tool contracts (input/output schemas) are documented and include at least one example invocation payload per tool

### Assumptions

- User authentication and authorization have already been handled by the time the MCP tool receives a user_id
- The existing SQLModel-based service/repository layer provides all necessary database operations for task CRUD
- Database connection configuration and management are already established from Phase 1
- The Official MCP SDK is compatible with the Python backend environment
- External MCP clients (AI agents in Phase 3) will handle user intent parsing and tool selection
- Network latency between MCP clients and server is negligible for local/same-region deployments
- Task data volume per user will not exceed 10,000 tasks in the initial deployment phase

### Out of Scope

- Natural language understanding or intent classification
- Conversation state management or multi-turn dialogue
- OpenAI Agents SDK integration (reserved for Phase 3)
- Frontend integration or user interface changes
- Task reminder scheduling or notification delivery
- Real-time task synchronization or push notifications
- Task sharing or collaboration features
- Advanced task querying (filtering, sorting, search) beyond listing all user tasks
- Rate limiting or quota management for tool invocations
- Audit logging of tool invocations (can be added later if needed)

### Dependencies

- **External**: Official MCP SDK (Python package) must be installed and compatible with Python 3.11+
- **Internal**: Existing SQLModel-based Task model, TaskService, and TaskRepository from Phase 1
- **Internal**: Existing Neon PostgreSQL database connection and configuration
- **Internal**: User authentication system that provides authenticated user_id (from earlier implementation)
