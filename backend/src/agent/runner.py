"""Agent runner utilities.

Provides convenient functions for executing the Task Management Agent
with user input and context. Includes history-aware execution for
stateless chat API support.

@see specs/009-stateless-chat-api/research.md for design decisions
"""

from typing import Any

import structlog
from agents import Runner, RunResult
from agents.items import TResponseInputItem, ToolCallItem, ToolCallOutputItem

from src.agent.agent import task_agent
from src.agent.context import UserContext
from src.models import Message
from src.schemas.chat import ToolCall

logger = structlog.get_logger(__name__)


def messages_to_input_list(messages: list[Message]) -> list[TResponseInputItem]:
    """Convert database Message records to SDK input format.

    Transforms a list of persisted messages into the format expected
    by the OpenAI Agents SDK for context reconstruction.

    Args:
        messages: List of Message records from the database

    Returns:
        List of input items compatible with Runner.run()

    Example:
        >>> messages = [
        ...     Message(role="user", content="Add task"),
        ...     Message(role="assistant", content="Created task")
        ... ]
        >>> input_list = messages_to_input_list(messages)
        >>> # [{"role": "user", "content": "Add task"}, ...]
    """
    return [{"role": m.role, "content": m.content} for m in messages]


def extract_tool_calls(result: RunResult[UserContext]) -> list[ToolCall]:
    """Extract tool call information from agent run result.

    Filters the RunResult.new_items for ToolCallItem entries and
    transforms them into ToolCall schema objects for the API response.

    Args:
        result: The RunResult from agent execution

    Returns:
        List of ToolCall objects with tool details

    Note:
        Tool call outputs are matched by call_id when available.
        Success is determined by the presence of output content.
    """
    tool_calls: list[ToolCall] = []

    # Build a map of tool outputs by call_id
    output_map: dict[str, ToolCallOutputItem] = {}
    for item in result.new_items:
        if isinstance(item, ToolCallOutputItem):
            output_map[item.raw_item.call_id] = item

    # Extract tool calls
    for item in result.new_items:
        if isinstance(item, ToolCallItem):
            raw = item.raw_item
            call_id = getattr(raw, "call_id", None)

            # Extract function name and arguments
            tool_name = ""
            parameters: dict[str, Any] = {}

            if hasattr(raw, "function"):
                tool_name = raw.function.name or ""
                # Parse arguments from JSON string
                import json

                try:
                    args_str = raw.function.arguments or "{}"
                    parameters = json.loads(args_str)
                except (json.JSONDecodeError, AttributeError):
                    parameters = {}

            # Match with output if available
            output = output_map.get(call_id) if call_id else None
            result_data: dict[str, Any] | None = None
            success = False

            if output:
                # Parse output content
                try:
                    output_content = output.output
                    if isinstance(output_content, str):
                        result_data = json.loads(output_content)
                    elif isinstance(output_content, dict):
                        result_data = output_content
                    success = True
                except (json.JSONDecodeError, AttributeError):
                    result_data = {"raw": str(output.output)}
                    success = True

            tool_calls.append(
                ToolCall(
                    tool_name=tool_name,
                    parameters=parameters,
                    result=result_data,
                    success=success,
                )
            )

    return tool_calls


async def run_agent_with_history(
    messages: list[TResponseInputItem],
    user_id: str,
) -> RunResult[UserContext]:
    """Execute agent with full conversation history.

    Runs the agent asynchronously with a list of message inputs,
    enabling stateless context reconstruction from the database.

    Args:
        messages: List of prior messages in SDK format
        user_id: Authenticated user's UUID string

    Returns:
        Full RunResult for response and tool call extraction

    Raises:
        ValueError: If user_id is invalid
        MaxTurnsExceeded: If agent takes too many turns
        Other SDK exceptions on execution errors
    """
    context = UserContext(user_id=user_id)

    logger.info(
        "agent_run_with_history_start",
        user_id=user_id,
        message_count=len(messages),
    )

    result: RunResult[UserContext] = await Runner.run(
        task_agent,
        messages,
        context=context,
    )

    logger.info(
        "agent_run_with_history_complete",
        user_id=user_id,
        new_items_count=len(result.new_items),
        response_length=len(result.final_output) if result.final_output else 0,
    )

    return result


def run_agent(user_input: str, user_id: str) -> str:
    """Run the Task Management Agent with user input.

    This is the main entry point for executing the agent. It creates a
    UserContext from the provided user_id and runs the agent synchronously.

    Args:
        user_input: Natural language command from the user
        user_id: Authenticated user's UUID string

    Returns:
        Agent's response text

    Raises:
        ValueError: If user_id is invalid

    Example:
        >>> response = run_agent(
        ...     user_input="Show my tasks",
        ...     user_id="550e8400-e29b-41d4-a716-446655440000"
        ... )
        >>> print(response)
        You have 3 tasks:
        1. [ ] Buy groceries (ID: abc...)
        ...
    """
    # Create context (validates user_id)
    context = UserContext(user_id=user_id)

    logger.info(
        "agent_run_start",
        user_id=user_id,
        input_length=len(user_input),
    )

    # Run agent synchronously
    result: RunResult[UserContext] = Runner.run_sync(
        task_agent,
        user_input,
        context=context,
    )

    # Extract response text
    response = result.final_output

    logger.info(
        "agent_run_complete",
        user_id=user_id,
        response_length=len(response) if response else 0,
    )

    return response


async def run_agent_async(user_input: str, user_id: str) -> str:
    """Run the Task Management Agent asynchronously.

    Async version of run_agent for use in async contexts like FastAPI.

    Args:
        user_input: Natural language command from the user
        user_id: Authenticated user's UUID string

    Returns:
        Agent's response text

    Raises:
        ValueError: If user_id is invalid
    """
    # Create context (validates user_id)
    context = UserContext(user_id=user_id)

    logger.info(
        "agent_run_start",
        user_id=user_id,
        input_length=len(user_input),
        async_mode=True,
    )

    # Run agent asynchronously
    result: RunResult[UserContext] = await Runner.run(
        task_agent,
        user_input,
        context=context,
    )

    # Extract response text
    response = result.final_output

    logger.info(
        "agent_run_complete",
        user_id=user_id,
        response_length=len(response) if response else 0,
        async_mode=True,
    )

    return response
