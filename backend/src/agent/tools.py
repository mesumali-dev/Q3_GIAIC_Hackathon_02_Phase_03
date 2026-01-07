"""Function tools for the Task Management Agent.

Each function tool wraps an MCP tool and is decorated with @function_tool
from the OpenAI Agents SDK. Tools receive user context via RunContextWrapper
and return human-readable string responses.

Architecture:
    - _impl functions: Pure implementation functions (testable without SDK)
    - @function_tool decorated functions: SDK-wrapped tools for agent use
"""

import structlog
from agents import function_tool, RunContextWrapper

from src.agent.context import UserContext

# Import MCP tools - these are async functions that return dict responses
from src.mcp.tools.add_task import add_task
from src.mcp.tools.list_tasks import list_tasks
from src.mcp.tools.complete_task import complete_task
from src.mcp.tools.delete_task import delete_task
from src.mcp.tools.update_task import update_task
from src.mcp.tools.schedule_reminder import schedule_reminder

logger = structlog.get_logger(__name__)


# =============================================================================
# Error Translation Helper
# =============================================================================


def translate_error(result: dict) -> str:
    """Translate MCP error response to user-friendly message.

    Args:
        result: MCP tool response with success=False and error details

    Returns:
        User-friendly error message string
    """
    error = result.get("error", {})
    code = error.get("code", "UNKNOWN_ERROR")
    message = error.get("message", "An unexpected error occurred")

    # Map error codes to user-friendly messages
    error_messages = {
        "TASK_NOT_FOUND": "I couldn't find that task. It may have been deleted or you may not have access to it.",
        "VALIDATION_ERROR": f"There was a problem with that request: {message}",
        "AUTHORIZATION_ERROR": "You don't have access to that task.",
        "DATABASE_ERROR": "Something went wrong on our end. Please try again.",
        "UNKNOWN_ERROR": "Something unexpected happened. Please try again.",
    }

    return f"Error: {error_messages.get(code, message)}"


# =============================================================================
# Implementation Functions (Testable)
# =============================================================================


async def add_task_impl(
    user_id: str,
    title: str,
    description: str | None = None,
) -> str:
    """Implementation for add_task_tool - testable without SDK wrapper.

    Args:
        user_id: User's UUID string
        title: Task title
        description: Optional task description

    Returns:
        Confirmation message or error string
    """
    logger.info(
        "agent_tool_invocation",
        tool="add_task_tool",
        user_id=user_id,
        title_length=len(title) if title else 0,
    )

    result = await add_task(
        user_id=user_id,
        title=title,
        description=description,
    )

    if result.get("success"):
        task_id = result.get("task_id", "unknown")
        task_title = result.get("title", title)
        logger.info("agent_tool_success", tool="add_task_tool", task_id=task_id)
        return f"Created task '{task_title}' (ID: {task_id})"
    else:
        logger.warning("agent_tool_error", tool="add_task_tool", result=result)
        return translate_error(result)


async def list_tasks_impl(user_id: str) -> str:
    """Implementation for list_tasks_tool - testable without SDK wrapper.

    Args:
        user_id: User's UUID string

    Returns:
        Formatted task list or error string
    """
    logger.info("agent_tool_invocation", tool="list_tasks_tool", user_id=user_id)

    result = await list_tasks(user_id=user_id)

    if result.get("success"):
        tasks = result.get("tasks", [])
        count = result.get("count", len(tasks))

        logger.info("agent_tool_success", tool="list_tasks_tool", count=count)

        if count == 0:
            return "You have no tasks. Would you like to create one?"

        lines = [f"You have {count} task{'s' if count != 1 else ''}:"]
        for i, task in enumerate(tasks, 1):
            status = "[✓]" if task.get("is_completed") else "[ ]"
            title = task.get("title", "Untitled")
            task_id = task.get("task_id", "unknown")
            lines.append(f"{i}. {status} {title} (ID: {task_id})")

        return "\n".join(lines)
    else:
        logger.warning("agent_tool_error", tool="list_tasks_tool", result=result)
        return translate_error(result)


async def complete_task_impl(user_id: str, task_id: str) -> str:
    """Implementation for complete_task_tool - testable without SDK wrapper.

    Args:
        user_id: User's UUID string
        task_id: Task's UUID string

    Returns:
        Confirmation message or error string
    """
    logger.info(
        "agent_tool_invocation",
        tool="complete_task_tool",
        user_id=user_id,
        task_id=task_id,
    )

    result = await complete_task(user_id=user_id, task_id=task_id)

    if result.get("success"):
        task_title = result.get("title", "Task")
        is_completed = result.get("is_completed", True)
        status = "complete" if is_completed else "incomplete"

        logger.info(
            "agent_tool_success",
            tool="complete_task_tool",
            task_id=task_id,
            is_completed=is_completed,
        )

        return f"Marked '{task_title}' as {status}."
    else:
        logger.warning("agent_tool_error", tool="complete_task_tool", result=result)
        return translate_error(result)


async def delete_task_impl(user_id: str, task_id: str) -> str:
    """Implementation for delete_task_tool - testable without SDK wrapper.

    Args:
        user_id: User's UUID string
        task_id: Task's UUID string

    Returns:
        Confirmation message or error string
    """
    logger.info(
        "agent_tool_invocation",
        tool="delete_task_tool",
        user_id=user_id,
        task_id=task_id,
    )

    result = await delete_task(user_id=user_id, task_id=task_id)

    if result.get("success"):
        logger.info("agent_tool_success", tool="delete_task_tool", task_id=task_id)
        return f"Deleted task (ID: {task_id})."
    else:
        logger.warning("agent_tool_error", tool="delete_task_tool", result=result)
        return translate_error(result)


async def update_task_impl(
    user_id: str,
    task_id: str,
    title: str | None = None,
    description: str | None = None,
) -> str:
    """Implementation for update_task_tool - testable without SDK wrapper.

    Args:
        user_id: User's UUID string
        task_id: Task's UUID string
        title: New title (optional)
        description: New description (optional)

    Returns:
        Confirmation message or error string
    """
    logger.info(
        "agent_tool_invocation",
        tool="update_task_tool",
        user_id=user_id,
        task_id=task_id,
        has_title=title is not None,
        has_description=description is not None,
    )

    result = await update_task(
        user_id=user_id,
        task_id=task_id,
        title=title,
        description=description,
    )

    if result.get("success"):
        updated_title = result.get("title", "Task")
        logger.info("agent_tool_success", tool="update_task_tool", task_id=task_id)

        changes = []
        if title:
            changes.append(f"title to '{updated_title}'")
        if description is not None:
            changes.append("description")

        change_text = " and ".join(changes) if changes else "task"
        return f"Updated {change_text}."
    else:
        logger.warning("agent_tool_error", tool="update_task_tool", result=result)
        return translate_error(result)


async def schedule_reminder_impl(
    user_id: str,
    task_id: str,
    remind_at: str,
    repeat_interval_minutes: int | None = None,
    repeat_count: int | None = None,
) -> str:
    """Implementation for schedule_reminder_tool - testable without SDK wrapper.

    Args:
        user_id: User's UUID string
        task_id: Task's UUID string
        remind_at: ISO 8601 datetime string
        repeat_interval_minutes: Minutes between repeats (optional)
        repeat_count: Number of times to repeat (optional)

    Returns:
        Confirmation message or error string
    """
    logger.info(
        "agent_tool_invocation",
        tool="schedule_reminder_tool",
        user_id=user_id,
        task_id=task_id,
        remind_at=remind_at,
    )

    result = await schedule_reminder(
        user_id=user_id,
        task_id=task_id,
        remind_at=remind_at,
        repeat_interval_minutes=repeat_interval_minutes,
        repeat_count=repeat_count,
    )

    if result.get("success"):
        reminder_time = result.get("remind_at", remind_at)
        logger.info(
            "agent_tool_success",
            tool="schedule_reminder_tool",
            reminder_id=result.get("reminder_id"),
        )

        msg = f"Reminder scheduled for {reminder_time}"

        if repeat_interval_minutes and repeat_count:
            msg += f", repeating every {repeat_interval_minutes} minutes, {repeat_count} times"
        elif repeat_interval_minutes:
            msg += f", repeating every {repeat_interval_minutes} minutes"

        return msg + "."
    else:
        logger.warning("agent_tool_error", tool="schedule_reminder_tool", result=result)
        return translate_error(result)


# =============================================================================
# SDK-Wrapped Function Tools
# =============================================================================


@function_tool
async def add_task_tool(
    ctx: RunContextWrapper[UserContext],
    title: str,
    description: str | None = None,
) -> str:
    """Create a new task for the user.

    Use this tool when the user wants to create a new task. Extract the task
    title from their request, and optionally a description if they provide one.

    Args:
        ctx: Context wrapper providing access to user_id
        title: The title of the task to create (required, 1-200 characters)
        description: Optional description for the task (max 1000 characters)

    Returns:
        Confirmation message with task title and ID, or error message
    """
    return await add_task_impl(ctx.context.user_id, title, description)


@function_tool
async def list_tasks_tool(ctx: RunContextWrapper[UserContext]) -> str:
    """List all tasks for the user.

    Use this tool when the user wants to see their tasks, such as when they
    ask "Show my tasks", "What do I have to do?", or "List my todos".

    Args:
        ctx: Context wrapper providing access to user_id

    Returns:
        Formatted list of tasks with completion status, or message if no tasks
    """
    return await list_tasks_impl(ctx.context.user_id)


@function_tool
async def complete_task_tool(
    ctx: RunContextWrapper[UserContext],
    task_id: str,
) -> str:
    """Mark a task as complete (or toggle its completion status).

    Use this tool when the user wants to mark a task as done. You'll need
    the task_id, which you can get by first listing the user's tasks.

    Args:
        ctx: Context wrapper providing access to user_id
        task_id: The UUID of the task to mark as complete

    Returns:
        Confirmation message with new status, or error message
    """
    return await complete_task_impl(ctx.context.user_id, task_id)


@function_tool
async def delete_task_tool(
    ctx: RunContextWrapper[UserContext],
    task_id: str,
) -> str:
    """Permanently delete a task.

    Use this tool when the user wants to remove a task. This action cannot
    be undone. You'll need the task_id, which you can get by first listing
    the user's tasks.

    Args:
        ctx: Context wrapper providing access to user_id
        task_id: The UUID of the task to delete

    Returns:
        Confirmation message, or error message
    """
    return await delete_task_impl(ctx.context.user_id, task_id)


@function_tool
async def update_task_tool(
    ctx: RunContextWrapper[UserContext],
    task_id: str,
    title: str | None = None,
    description: str | None = None,
) -> str:
    """Update a task's title or description.

    Use this tool when the user wants to change a task's title or description.
    At least one of title or description must be provided. You'll need the
    task_id, which you can get by first listing the user's tasks.

    Args:
        ctx: Context wrapper providing access to user_id
        task_id: The UUID of the task to update
        title: New title for the task (optional)
        description: New description for the task (optional)

    Returns:
        Confirmation message with updated details, or error message
    """
    return await update_task_impl(ctx.context.user_id, task_id, title, description)


@function_tool
async def schedule_reminder_tool(
    ctx: RunContextWrapper[UserContext],
    task_id: str,
    remind_at: str,
    repeat_interval_minutes: int | None = None,
    repeat_count: int | None = None,
) -> str:
    """Schedule a reminder for a task.

    Use this tool when the user wants to be reminded about a task. The reminder
    time should be in ISO 8601 format (e.g., "2026-01-09T09:00:00Z"). Optionally,
    set up a repeating reminder with interval and count.

    Args:
        ctx: Context wrapper providing access to user_id
        task_id: The UUID of the task to set a reminder for
        remind_at: When to trigger the reminder (ISO 8601 datetime string)
        repeat_interval_minutes: Minutes between repeats (optional, max 1440)
        repeat_count: Total times to repeat (optional, max 100)

    Returns:
        Confirmation message with reminder details, or error message
    """
    return await schedule_reminder_impl(
        ctx.context.user_id, task_id, remind_at, repeat_interval_minutes, repeat_count
    )


# =============================================================================
# Tool Registry
# =============================================================================

# All available function tools for the Task Management Agent
ALL_TOOLS = [
    add_task_tool,
    list_tasks_tool,
    complete_task_tool,
    delete_task_tool,
    update_task_tool,
    schedule_reminder_tool,
]
