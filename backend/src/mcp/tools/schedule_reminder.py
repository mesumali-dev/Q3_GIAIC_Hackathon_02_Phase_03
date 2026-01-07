"""schedule_reminder MCP tool implementation.

Enables AI agents to schedule reminders for tasks.
"""

import structlog
from datetime import datetime
from uuid import UUID

from src.mcp.errors import handle_tool_error
from src.mcp.schemas import ScheduleReminderInput, ReminderOutput
from src.mcp.server import get_db_session, server
from src.schemas.reminder import ReminderCreate
from src.services.reminder_service import create_reminder

logger = structlog.get_logger(__name__)


@server.tool()
async def schedule_reminder(
    user_id: str,
    task_id: str,
    remind_at: str,
    repeat_interval_minutes: int | None = None,
    repeat_count: int | None = None,
) -> dict:
    """Schedule a reminder for a task.

    This tool enables AI agents to create reminders by providing a task ID
    and reminder time. Optionally supports repeating reminders.

    Args:
        user_id: Authenticated user UUID (string format)
        task_id: Task UUID to set reminder for
        remind_at: When to trigger reminder (ISO 8601 datetime string)
        repeat_interval_minutes: Minutes between repeats (optional, max 1440 = 24 hours)
        repeat_count: Total times to repeat (optional, max 100)

    Returns:
        dict: Success response with reminder details, or error response

    Success Response:
        {
            "success": True,
            "reminder_id": 123,
            "user_id": "uuid-string",
            "task_id": "uuid-string",
            "remind_at": "ISO-8601-timestamp",
            "repeat_interval_minutes": 60 | None,
            "repeat_count": 5 | None,
            "triggered_count": 0,
            "is_active": True,
            "created_at": "ISO-8601-timestamp"
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
        - VALIDATION_ERROR: Invalid user_id, task_id, or remind_at format
        - NOT_FOUND_ERROR: Task not found or doesn't belong to user
        - DATABASE_ERROR: Database operation failed

    Example:
        >>> result = await schedule_reminder(
        ...     user_id="550e8400-e29b-41d4-a716-446655440000",
        ...     task_id="660e8400-e29b-41d4-a716-446655440001",
        ...     remind_at="2024-12-25T10:00:00Z",
        ...     repeat_interval_minutes=60,
        ...     repeat_count=3
        ... )
        >>> result["success"]
        True
    """
    try:
        # Log tool invocation
        logger.info(
            "mcp_tool_invocation",
            tool="schedule_reminder",
            user_id=user_id,
            task_id=task_id,
            remind_at=remind_at,
        )

        # Validate input using Pydantic schema
        input_data = ScheduleReminderInput(
            user_id=user_id,
            task_id=task_id,
            remind_at=remind_at,
            repeat_interval_minutes=repeat_interval_minutes,
            repeat_count=repeat_count,
        )

        # Convert string UUIDs to UUID objects for database operations
        user_uuid = UUID(input_data.user_id)
        task_uuid = UUID(input_data.task_id)

        # Parse remind_at datetime
        remind_at_dt = datetime.fromisoformat(input_data.remind_at.replace("Z", "+00:00"))

        # Create ReminderCreate schema for service layer
        reminder_data = ReminderCreate(
            task_id=task_uuid,
            remind_at=remind_at_dt,
            repeat_interval_minutes=input_data.repeat_interval_minutes,
            repeat_count=input_data.repeat_count,
        )

        # Delegate to service layer with fresh database session
        with get_db_session() as db:
            reminder = create_reminder(db, user_uuid, reminder_data)

        # Convert Reminder model to ReminderOutput schema
        output = ReminderOutput.from_reminder(reminder)

        # Log success
        logger.info("mcp_tool_success", tool="schedule_reminder", reminder_id=reminder.id)

        # Return structured output as dict
        return output.model_dump()

    except ValueError as e:
        # Log validation/not found errors
        logger.warning("mcp_tool_validation_error", tool="schedule_reminder", error=str(e))
        return handle_tool_error(e)

    except Exception as e:
        # Log unexpected errors
        logger.error("mcp_tool_error", tool="schedule_reminder", error=str(e), error_type=type(e).__name__)

        # Return structured error response
        return handle_tool_error(e)
