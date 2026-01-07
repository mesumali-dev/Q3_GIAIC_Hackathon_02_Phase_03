"""Task Management Agent definition.

Defines the AI agent that interprets natural language commands and
orchestrates MCP tools for task management operations.
"""

import os
from agents import Agent

from src.agent.context import UserContext
from src.agent.prompts import TASK_MANAGER_FULL_PROMPT
from src.agent.tools import ALL_TOOLS


def get_model() -> str:
    """Get the model to use for the agent.

    Returns the model from OPENAI_DEFAULT_MODEL environment variable,
    or defaults to 'gpt-4o' if not set.
    """
    return os.environ.get("OPENAI_DEFAULT_MODEL", "gpt-4o")


# Task Management Agent
# This agent is stateless per invocation - it receives user context for
# each request and does not maintain conversation history internally.
task_agent: Agent[UserContext] = Agent(
    name="TaskManager",
    instructions=TASK_MANAGER_FULL_PROMPT,
    model=get_model(),
    tools=ALL_TOOLS,
)
