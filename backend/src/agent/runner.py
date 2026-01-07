"""Agent runner utilities.

Provides convenient functions for executing the Task Management Agent
with user input and context.
"""

import structlog
from agents import Runner, RunResult

from src.agent.agent import task_agent
from src.agent.context import UserContext

logger = structlog.get_logger(__name__)


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
