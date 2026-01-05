"""list_tasks MCP tool implementation.

Enables AI agents to retrieve all tasks for a specific user.
"""

import structlog
from uuid import UUID

from src.mcp.errors import handle_tool_error
from src.mcp.schemas import ListTasksInput, ListTasksOutput
from src.mcp.server import get_db_session, server
from src.services.task_service import get_tasks

logger = structlog.get_logger(__name__)


@server.tool()
async def list_tasks(user_id: str) -> dict:
    """Retrieve all tasks for a user.

    This tool enables AI agents to list all tasks belonging to a specific
    user. Tasks are returned in descending order by creation date (newest first).
    The operation is stateless and user-scoped.

    Args:
        user_id: Authenticated user UUID (string format)

    Returns:
        dict: Success response with task list and count, or error response

    Success Response:
        {
            "success": True,
            "tasks": [
                {
                    "task_id": "uuid-string",
                    "user_id": "uuid-string",
                    "title": "Task title",
                    "description": "Task description" | None,
                    "is_completed": True | False,
                    "created_at": "ISO-8601-timestamp",
                    "updated_at": "ISO-8601-timestamp"
                },
                ...
            ],
            "count": 2
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
        - VALIDATION_ERROR: Invalid user_id format
        - DATABASE_ERROR: Database operation failed

    Example:
        >>> result = await list_tasks(user_id="550e8400-e29b-41d4-a716-446655440000")
        >>> result["success"]
        True
        >>> result["count"]
        5
    """
    try:
        # Log tool invocation
        logger.info(
            "mcp_tool_invocation",
            tool="list_tasks",
            user_id=user_id,
        )

        # Validate input using Pydantic schema
        input_data = ListTasksInput(user_id=user_id)

        # Convert string UUID to UUID object for database operations
        user_uuid = UUID(input_data.user_id)

        # Delegate to service layer with fresh database session
        with get_db_session() as db:
            tasks = get_tasks(db, user_uuid)

        # Convert list of Task models to ListTasksOutput schema
        output = ListTasksOutput.from_tasks(tasks)

        # Log success
        logger.info("mcp_tool_success", tool="list_tasks", count=output.count)

        # Return structured output as dict
        return output.model_dump()

    except Exception as e:
        # Log error
        logger.error("mcp_tool_error", tool="list_tasks", error=str(e), error_type=type(e).__name__)

        # Return structured error response
        return handle_tool_error(e)
