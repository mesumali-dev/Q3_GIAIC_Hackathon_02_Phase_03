"""AI Agent module for task management orchestration.

This module provides an AI agent that interprets natural language commands
and orchestrates MCP tools to manage user tasks. The agent is stateless
per invocation, receiving user context for each request.

Exports:
    UserContext: Runtime context with authenticated user information
    TASK_MANAGER_PROMPT: System prompt for the task management agent
    TASK_MANAGER_FULL_PROMPT: System prompt with error handling guidance
    task_agent: Pre-configured Task Management Agent instance
    run_agent: Synchronous utility function to run agent with user input
    run_agent_async: Async utility function to run agent with user input
"""

from src.agent.context import UserContext
from src.agent.prompts import TASK_MANAGER_PROMPT, TASK_MANAGER_FULL_PROMPT
from src.agent.agent import task_agent
from src.agent.runner import run_agent, run_agent_async

__all__ = [
    "UserContext",
    "TASK_MANAGER_PROMPT",
    "TASK_MANAGER_FULL_PROMPT",
    "task_agent",
    "run_agent",
    "run_agent_async",
]
