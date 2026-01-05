"""update_task MCP tool implementation.

Enables AI agents to update task details (title, description).
"""

import structlog
from uuid import UUID

from src.mcp.errors import AuthorizationError, TaskNotFoundError, ValidationError, handle_tool_error
from src.mcp.schemas import TaskOutput, UpdateTaskInput
from src.mcp.server import get_db_session, server
from src.schemas.task import TaskUpdate
from src.services.task_service import get_task, update_task as update_task_service

logger = structlog.get_logger(__name__)


@server.tool()
async def update_task(user_id: str, task_id: str, title: str | None = None, description: str | None = None) -> dict:
    """Update task title and/or description.

    This tool enables AI agents to modify task details. At least one field
    (title or description) must be provided. Only the specified fields are
    updated; other fields remain unchanged. The task must exist and belong
    to the authenticated user.

    Args:
        user_id: Authenticated user UUID (string format)
        task_id: Task UUID to update (string format)
        title: New task title (optional, 1-200 characters)
        description: New description (optional, max 1000 characters)

    Returns:
        dict: Success response with updated task details, or error response

    Success Response:
        {
            "success": True,
            "task_id": "uuid-string",
            "user_id": "uuid-string",
            "title": "Updated title",
            "description": "Updated description" | None,
            "is_completed": True | False,
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
        - VALIDATION_ERROR: Invalid IDs, empty title, no fields provided, or field too long
        - TASK_NOT_FOUND: Task does not exist or user not authorized
        - AUTHORIZATION_ERROR: Task belongs to different user
        - DATABASE_ERROR: Database operation failed

    Example:
        >>> result = await update_task(
        ...     user_id="550e8400-e29b-41d4-a716-446655440000",
        ...     task_id="7c9e6679-7425-40de-944b-e07fc1f90ae7",
        ...     title="Updated task title"
        ... )
        >>> result["success"]
        True
        >>> result["title"]
        'Updated task title'
    """
    try:
        # Log tool invocation
        logger.info(
            "mcp_tool_invocation",
            tool="update_task",
            user_id=user_id,
            task_id=task_id,
            has_title=title is not None,
            has_description=description is not None,
        )

        # Validate input using Pydantic schema
        input_data = UpdateTaskInput(
            user_id=user_id,
            task_id=task_id,
            title=title,
            description=description
        )

        # Convert string UUIDs to UUID objects for database operations
        user_uuid = UUID(input_data.user_id)
        task_uuid = UUID(input_data.task_id)

        # Create TaskUpdate schema for service layer
        task_update = TaskUpdate(title=input_data.title, description=input_data.description)

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

            # Update the task
            updated_task = update_task_service(db, user_uuid, task_uuid, task_update)

            if updated_task is None:
                # Should not happen after verification, but handle defensively
                raise TaskNotFoundError()

        # Convert Task model to TaskOutput schema
        output = TaskOutput.from_task(updated_task)

        # Log success
        logger.info(
            "mcp_tool_success",
            tool="update_task",
            task_id=str(updated_task.id),
        )

        # Return structured output as dict
        return output.model_dump()

    except (TaskNotFoundError, AuthorizationError, ValidationError) as e:
        # Log known errors
        logger.warning(
            "mcp_tool_error",
            tool="update_task",
            error=str(e),
            error_type=type(e).__name__,
            user_id=user_id,
            task_id=task_id,
        )
        return handle_tool_error(e)

    except Exception as e:
        # Log unexpected errors
        logger.error(
            "mcp_tool_error",
            tool="update_task",
            error=str(e),
            error_type=type(e).__name__,
        )
        return handle_tool_error(e)
