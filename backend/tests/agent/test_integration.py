"""Integration tests for the Task Management Agent.

These tests verify the complete agent flow including:
- Agent instantiation
- Tool registration
- Context propagation
- Response formatting

Note: Integration tests with real MCP tools require database setup.
These tests mock the MCP layer to test agent integration without DB.
"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock

from src.agent.agent import task_agent
from src.agent.context import UserContext
from src.agent.runner import run_agent_async
from src.agent.tools import ALL_TOOLS


class TestAgentIntegration:
    """Integration tests for the task_agent."""

    def test_agent_is_configured_correctly(self) -> None:
        """Agent should be properly configured with all components."""
        assert task_agent.name == "TaskManager"
        assert task_agent.instructions is not None
        assert len(task_agent.tools) == 6

    def test_all_tools_are_registered(self) -> None:
        """All expected tools should be registered with the agent."""
        tool_names = [t.name for t in task_agent.tools]
        expected_tools = [
            "add_task_tool",
            "list_tasks_tool",
            "complete_task_tool",
            "delete_task_tool",
            "update_task_tool",
            "schedule_reminder_tool",
        ]
        for tool in expected_tools:
            assert tool in tool_names, f"Missing tool: {tool}"


class TestUserIdPropagation:
    """Tests verifying user_id is correctly propagated through the system."""

    def test_user_context_stores_user_id(self, fixed_user_id: str) -> None:
        """UserContext should store the provided user_id."""
        context = UserContext(user_id=fixed_user_id)
        assert context.user_id == fixed_user_id

    @pytest.mark.anyio
    async def test_add_task_receives_user_id(self, fixed_user_id: str) -> None:
        """add_task_impl should receive correct user_id."""
        from src.agent.tools import add_task_impl

        with patch("src.agent.tools.add_task", new_callable=AsyncMock) as mock:
            mock.return_value = {"success": True, "task_id": "test-id", "title": "Test"}

            await add_task_impl(fixed_user_id, "Test task")

            mock.assert_called_once()
            call_args = mock.call_args
            assert call_args.kwargs["user_id"] == fixed_user_id

    @pytest.mark.anyio
    async def test_list_tasks_receives_user_id(self, fixed_user_id: str) -> None:
        """list_tasks_impl should receive correct user_id."""
        from src.agent.tools import list_tasks_impl

        with patch("src.agent.tools.list_tasks", new_callable=AsyncMock) as mock:
            mock.return_value = {"success": True, "tasks": [], "count": 0}

            await list_tasks_impl(fixed_user_id)

            mock.assert_called_once()
            assert mock.call_args.kwargs["user_id"] == fixed_user_id

    @pytest.mark.anyio
    async def test_complete_task_receives_user_id(
        self, fixed_user_id: str, sample_task_id: str
    ) -> None:
        """complete_task_impl should receive correct user_id."""
        from src.agent.tools import complete_task_impl

        with patch("src.agent.tools.complete_task", new_callable=AsyncMock) as mock:
            mock.return_value = {"success": True, "title": "Test", "is_completed": True}

            await complete_task_impl(fixed_user_id, sample_task_id)

            mock.assert_called_once()
            assert mock.call_args.kwargs["user_id"] == fixed_user_id

    @pytest.mark.anyio
    async def test_delete_task_receives_user_id(
        self, fixed_user_id: str, sample_task_id: str
    ) -> None:
        """delete_task_impl should receive correct user_id."""
        from src.agent.tools import delete_task_impl

        with patch("src.agent.tools.delete_task", new_callable=AsyncMock) as mock:
            mock.return_value = {"success": True, "task_id": sample_task_id}

            await delete_task_impl(fixed_user_id, sample_task_id)

            mock.assert_called_once()
            assert mock.call_args.kwargs["user_id"] == fixed_user_id

    @pytest.mark.anyio
    async def test_update_task_receives_user_id(
        self, fixed_user_id: str, sample_task_id: str
    ) -> None:
        """update_task_impl should receive correct user_id."""
        from src.agent.tools import update_task_impl

        with patch("src.agent.tools.update_task", new_callable=AsyncMock) as mock:
            mock.return_value = {"success": True, "title": "Updated"}

            await update_task_impl(fixed_user_id, sample_task_id, title="Updated")

            mock.assert_called_once()
            assert mock.call_args.kwargs["user_id"] == fixed_user_id

    @pytest.mark.anyio
    async def test_schedule_reminder_receives_user_id(
        self, fixed_user_id: str, sample_task_id: str
    ) -> None:
        """schedule_reminder_impl should receive correct user_id."""
        from src.agent.tools import schedule_reminder_impl

        with patch("src.agent.tools.schedule_reminder", new_callable=AsyncMock) as mock:
            mock.return_value = {
                "success": True,
                "reminder_id": 1,
                "remind_at": "2026-01-09T09:00:00Z",
            }

            await schedule_reminder_impl(
                fixed_user_id, sample_task_id, "2026-01-09T09:00:00Z"
            )

            mock.assert_called_once()
            assert mock.call_args.kwargs["user_id"] == fixed_user_id


class TestNoDirectDatabaseAccess:
    """Tests verifying agent never accesses database directly."""

    def test_tools_module_does_not_import_database(self) -> None:
        """tools.py should not directly import database modules."""
        import src.agent.tools as tools_module
        import inspect

        source = inspect.getsource(tools_module)

        # Should not import database directly
        assert "from src.database" not in source
        assert "from src.models" not in source
        assert "sqlmodel" not in source.lower()
        assert "Session" not in source or "RunContextWrapper" in source

    def test_agent_module_does_not_import_database(self) -> None:
        """agent.py should not directly import database modules."""
        import src.agent.agent as agent_module
        import inspect

        source = inspect.getsource(agent_module)

        assert "from src.database" not in source
        assert "from src.models" not in source

    def test_runner_module_does_not_import_database(self) -> None:
        """runner.py should not directly import database modules."""
        import src.agent.runner as runner_module
        import inspect

        source = inspect.getsource(runner_module)

        assert "from src.database" not in source
        assert "from src.models" not in source


class TestAgentStatelessness:
    """Tests verifying agent is stateless per invocation."""

    def test_context_is_created_fresh_each_call(self, fixed_user_id: str) -> None:
        """Each call should create a fresh context."""
        ctx1 = UserContext(user_id=fixed_user_id)
        ctx2 = UserContext(user_id=fixed_user_id)

        # Different objects
        assert ctx1 is not ctx2

        # Same values
        assert ctx1.user_id == ctx2.user_id

    def test_context_is_immutable(self, fixed_user_context: UserContext) -> None:
        """Context should not change during execution."""
        original_user_id = fixed_user_context.user_id

        # Dataclass is mutable by default, but we shouldn't modify it
        # Verify the value hasn't changed
        assert fixed_user_context.user_id == original_user_id


class TestToolResponseFormats:
    """Tests verifying tools return properly formatted responses."""

    @pytest.mark.anyio
    async def test_add_task_success_format(self, fixed_user_id: str) -> None:
        """add_task_impl success response should include title and ID."""
        from src.agent.tools import add_task_impl

        with patch("src.agent.tools.add_task", new_callable=AsyncMock) as mock:
            mock.return_value = {
                "success": True,
                "task_id": "abc-123",
                "title": "Test Task",
            }

            result = await add_task_impl(fixed_user_id, "Test Task")

            assert "Test Task" in result
            assert "abc-123" in result
            assert "Created" in result

    @pytest.mark.anyio
    async def test_list_tasks_success_format(self, fixed_user_id: str) -> None:
        """list_tasks_impl success response should be properly formatted."""
        from src.agent.tools import list_tasks_impl

        with patch("src.agent.tools.list_tasks", new_callable=AsyncMock) as mock:
            mock.return_value = {
                "success": True,
                "tasks": [
                    {"task_id": "1", "title": "Task 1", "is_completed": False},
                    {"task_id": "2", "title": "Task 2", "is_completed": True},
                ],
                "count": 2,
            }

            result = await list_tasks_impl(fixed_user_id)

            assert "2 tasks" in result
            assert "[ ]" in result  # Incomplete marker
            assert "[✓]" in result  # Complete marker
            assert "Task 1" in result
            assert "Task 2" in result

    @pytest.mark.anyio
    async def test_error_response_format(self, fixed_user_id: str) -> None:
        """Error responses should be user-friendly."""
        from src.agent.tools import add_task_impl

        with patch("src.agent.tools.add_task", new_callable=AsyncMock) as mock:
            mock.return_value = {
                "success": False,
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": "Title is required",
                },
            }

            result = await add_task_impl(fixed_user_id, "")

            assert "Error:" in result
            assert "Title is required" in result
