"""Tests for the Task Management Agent definition.

Tests agent creation, tool registration, and basic configuration.
"""

import pytest
from unittest.mock import patch, MagicMock

from src.agent.agent import task_agent, get_model
from src.agent.context import UserContext
from src.agent.prompts import TASK_MANAGER_FULL_PROMPT
from src.agent.tools import ALL_TOOLS


class TestAgentDefinition:
    """Tests for the TaskManager agent definition."""

    def test_agent_has_correct_name(self) -> None:
        """Agent should be named TaskManager."""
        assert task_agent.name == "TaskManager"

    def test_agent_has_system_prompt(self) -> None:
        """Agent should have the task manager system prompt."""
        assert task_agent.instructions == TASK_MANAGER_FULL_PROMPT

    def test_agent_has_all_tools_registered(self) -> None:
        """Agent should have all function tools registered."""
        # Agent should have the same number of tools
        assert len(task_agent.tools) == len(ALL_TOOLS)

    def test_agent_tools_include_add_task(self) -> None:
        """Agent should have add_task_tool registered."""
        tool_names = [t.name for t in task_agent.tools]
        assert "add_task_tool" in tool_names

    def test_agent_tools_include_list_tasks(self) -> None:
        """Agent should have list_tasks_tool registered."""
        tool_names = [t.name for t in task_agent.tools]
        assert "list_tasks_tool" in tool_names

    def test_agent_tools_include_complete_task(self) -> None:
        """Agent should have complete_task_tool registered."""
        tool_names = [t.name for t in task_agent.tools]
        assert "complete_task_tool" in tool_names

    def test_agent_tools_include_delete_task(self) -> None:
        """Agent should have delete_task_tool registered."""
        tool_names = [t.name for t in task_agent.tools]
        assert "delete_task_tool" in tool_names

    def test_agent_tools_include_update_task(self) -> None:
        """Agent should have update_task_tool registered."""
        tool_names = [t.name for t in task_agent.tools]
        assert "update_task_tool" in tool_names

    def test_agent_tools_include_schedule_reminder(self) -> None:
        """Agent should have schedule_reminder_tool registered."""
        tool_names = [t.name for t in task_agent.tools]
        assert "schedule_reminder_tool" in tool_names


class TestGetModel:
    """Tests for the get_model function."""

    def test_default_model_is_gpt4o(self) -> None:
        """Default model should be gpt-4o when env var not set."""
        with patch.dict("os.environ", {}, clear=True):
            # Remove OPENAI_DEFAULT_MODEL if it exists
            import os
            original = os.environ.pop("OPENAI_DEFAULT_MODEL", None)
            try:
                model = get_model()
                assert model == "gpt-4o"
            finally:
                if original is not None:
                    os.environ["OPENAI_DEFAULT_MODEL"] = original

    def test_custom_model_from_env(self) -> None:
        """Model should be read from OPENAI_DEFAULT_MODEL env var."""
        with patch.dict("os.environ", {"OPENAI_DEFAULT_MODEL": "gpt-4o-mini"}):
            model = get_model()
            assert model == "gpt-4o-mini"


class TestToolDescriptions:
    """Tests for tool docstrings and descriptions."""

    def test_add_task_tool_has_description(self) -> None:
        """add_task_tool should have a description."""
        from src.agent.tools import add_task_tool
        assert add_task_tool.__doc__ is not None
        assert len(add_task_tool.__doc__) > 50

    def test_list_tasks_tool_has_description(self) -> None:
        """list_tasks_tool should have a description."""
        from src.agent.tools import list_tasks_tool
        assert list_tasks_tool.__doc__ is not None
        assert len(list_tasks_tool.__doc__) > 50

    def test_complete_task_tool_has_description(self) -> None:
        """complete_task_tool should have a description."""
        from src.agent.tools import complete_task_tool
        assert complete_task_tool.__doc__ is not None
        assert len(complete_task_tool.__doc__) > 50

    def test_delete_task_tool_has_description(self) -> None:
        """delete_task_tool should have a description."""
        from src.agent.tools import delete_task_tool
        assert delete_task_tool.__doc__ is not None
        assert len(delete_task_tool.__doc__) > 50

    def test_update_task_tool_has_description(self) -> None:
        """update_task_tool should have a description."""
        from src.agent.tools import update_task_tool
        assert update_task_tool.__doc__ is not None
        assert len(update_task_tool.__doc__) > 50

    def test_schedule_reminder_tool_has_description(self) -> None:
        """schedule_reminder_tool should have a description."""
        from src.agent.tools import schedule_reminder_tool
        assert schedule_reminder_tool.__doc__ is not None
        assert len(schedule_reminder_tool.__doc__) > 50


class TestSystemPrompt:
    """Tests for the system prompt content."""

    def test_prompt_defines_role(self) -> None:
        """System prompt should define the agent's role."""
        assert "task management assistant" in TASK_MANAGER_FULL_PROMPT.lower()

    def test_prompt_lists_capabilities(self) -> None:
        """System prompt should list agent capabilities."""
        prompt_lower = TASK_MANAGER_FULL_PROMPT.lower()
        assert "create" in prompt_lower
        assert "list" in prompt_lower
        assert "complete" in prompt_lower
        assert "delete" in prompt_lower
        assert "update" in prompt_lower

    def test_prompt_includes_rules(self) -> None:
        """System prompt should include behavioral rules."""
        assert "RULES" in TASK_MANAGER_FULL_PROMPT
        assert "always use tools" in TASK_MANAGER_FULL_PROMPT.lower()

    def test_prompt_includes_error_handling(self) -> None:
        """System prompt should include error handling guidance."""
        assert "ERROR" in TASK_MANAGER_FULL_PROMPT
        assert "TASK_NOT_FOUND" in TASK_MANAGER_FULL_PROMPT
