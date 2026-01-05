"""add_task MCP tool implementation.

Enables AI agents to create new tasks and persist them to the database.
"""

import structlog
from uuid import UUID

from src.mcp.errors import handle_tool_error
from src.mcp.schemas import AddTaskInput, TaskOutput
from src.mcp.server import get_db_session, server
from src.schemas.task import TaskCreate
from src.services.task_service import create_task

logger = structlog.get_logger(__name__)


@server.tool()
async def add_task(user_id: str, title: str, description: str | None = None) -> dict:
    """Create a new task for a user.

    This tool enables AI agents to create tasks by providing a title and
    optional description. The task is persisted to the database and scoped
    to the authenticated user.

    Args:
        user_id: Authenticated user UUID (string format)
        title: Task title (1-200 characters, required)
        description: Optional task description (max 1000 characters)

    Returns:
        dict: Success response with task details, or error response

    Success Response:
        {
            "success": True,
            "task_id": "uuid-string",
            "user_id": "uuid-string",
            "title": "Task title",
            "description": "Task description" | None,
            "is_completed": False,
            "created_at": "ISO-8601-timestamp",
            "updated_at": "ISO-8601-timestamp"
        }

    Error Response:
        {
            "success": False,
            "error": {
                "code": "ERROR_CODE",
                "message": "Error message"
            }
        }

    Error Codes:
        - VALIDATION_ERROR: Invalid user_id, empty title, or title too long
        - DATABASE_ERROR: Database operation failed

    Example:
        >>> result = await add_task(
        ...     user_id="550e8400-e29b-41d4-a716-446655440000",
        ...     title="Buy groceries",
        ...     description="Milk, eggs, bread"
        ... )
        >>> result["success"]
        True
    """
    try:
        # Log tool invocation
        logger.info(
            "mcp_tool_invocation",
            tool="add_task",
            user_id=user_id,
            title_length=len(title) if title else 0,
        )

        # Validate input using Pydantic schema
        input_data = AddTaskInput(user_id=user_id, title=title, description=description)

        # Convert string UUID to UUID object for database operations
        user_uuid = UUID(input_data.user_id)

        # Create TaskCreate schema for service layer
        task_data = TaskCreate(title=input_data.title, description=input_data.description)

        # Delegate to service layer with fresh database session
        with get_db_session() as db:
            task = create_task(db, user_uuid, task_data)

        # Convert Task model to TaskOutput schema
        output = TaskOutput.from_task(task)

        # Log success
        logger.info("mcp_tool_success", tool="add_task", task_id=str(task.id))

        # Return structured output as dict
        return output.model_dump()

    except Exception as e:
        # Log error
        logger.error("mcp_tool_error", tool="add_task", error=str(e), error_type=type(e).__name__)

        # Return structured error response
        return handle_tool_error(e)
