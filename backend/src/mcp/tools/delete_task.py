"""delete_task MCP tool implementation.

Enables AI agents to permanently delete tasks.
"""

import structlog
from uuid import UUID

from src.mcp.errors import AuthorizationError, TaskNotFoundError, handle_tool_error
from src.mcp.schemas import DeleteTaskInput, DeleteTaskOutput
from src.mcp.server import get_db_session, server
from src.services.task_service import delete_task as delete_task_service, get_task

logger = structlog.get_logger(__name__)


@server.tool()
async def delete_task(user_id: str, task_id: str) -> dict:
    """Permanently delete a task.

    This tool enables AI agents to remove a task from the database.
    The operation is permanent and cannot be undone. The task must
    exist and belong to the authenticated user.

    Args:
        user_id: Authenticated user UUID (string format)
        task_id: Task UUID to delete (string format)

    Returns:
        dict: Success response with confirmation, or error response

    Success Response:
        {
            "success": True,
            "task_id": "uuid-string",
            "message": "Task deleted successfully"
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
        - VALIDATION_ERROR: Invalid user_id or task_id format
        - TASK_NOT_FOUND: Task does not exist or user not authorized
        - AUTHORIZATION_ERROR: Task belongs to different user
        - DATABASE_ERROR: Database operation failed

    Example:
        >>> result = await delete_task(
        ...     user_id="550e8400-e29b-41d4-a716-446655440000",
        ...     task_id="7c9e6679-7425-40de-944b-e07fc1f90ae7"
        ... )
        >>> result["success"]
        True
        >>> result["message"]
        'Task deleted successfully'
    """
    try:
        # Log tool invocation
        logger.info(
            "mcp_tool_invocation",
            tool="delete_task",
            user_id=user_id,
            task_id=task_id,
        )

        # Validate input using Pydantic schema
        input_data = DeleteTaskInput(user_id=user_id, task_id=task_id)

        # Convert string UUIDs to UUID objects for database operations
        user_uuid = UUID(input_data.user_id)
        task_uuid = UUID(input_data.task_id)

        # Delegate to service layer with fresh database session
        with get_db_session() as db:
            # First verify task exists and belongs to user
            task = get_task(db, user_uuid, task_uuid)

            if task is None:
                # Task not found or doesn't belong to user
                raise TaskNotFoundError()

            # Verify ownership (additional authorization check)
            if task.user_id != user_uuid:
                raise AuthorizationError("Task belongs to different user")

            # Delete the task
            success = delete_task_service(db, user_uuid, task_uuid)

            if not success:
                # Should not happen after verification, but handle defensively
                raise TaskNotFoundError()

        # Create success output
        output = DeleteTaskOutput(task_id=str(task_uuid))

        # Log success
        logger.info(
            "mcp_tool_success",
            tool="delete_task",
            task_id=str(input_data.task_id),
        )

        # Return structured output as dict
        return output.model_dump()

    except (TaskNotFoundError, AuthorizationError) as e:
        # Log authorization/not-found errors
        logger.warning(
            "mcp_tool_authorization_error",
            tool="delete_task",
            error=str(e),
            user_id=user_id,
            task_id=task_id,
        )
        return handle_tool_error(e)

    except Exception as e:
        # Log unexpected errors
        logger.error(
            "mcp_tool_error",
            tool="delete_task",
            error=str(e),
            error_type=type(e).__name__,
        )
        return handle_tool_error(e)
