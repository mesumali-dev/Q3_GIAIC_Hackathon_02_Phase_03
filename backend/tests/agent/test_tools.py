"""Tests for agent function tools.

Each test class covers a specific function tool implementation.
Tests use mocked MCP tool responses to verify tool behavior.

Note: We test the _impl functions directly since the @function_tool
decorated versions are FunctionTool objects that require the SDK's Runner.
"""

import pytest
from unittest.mock import AsyncMock, patch


# =============================================================================
# User Story 1: add_task_impl Tests
# =============================================================================


class TestAddTaskImpl:
    """Tests for the add_task_impl function."""

    @pytest.mark.anyio
    async def test_add_task_with_title_only(
        self, fixed_user_id: str, sample_task_data: dict
    ) -> None:
        """add_task_impl creates task with title only."""
        from src.agent.tools import add_task_impl

        with patch("src.agent.tools.add_task", new_callable=AsyncMock) as mock_mcp:
            mock_mcp.return_value = sample_task_data

            result = await add_task_impl(
                user_id=fixed_user_id,
                title="Buy groceries",
            )

            mock_mcp.assert_called_once_with(
                user_id=fixed_user_id,
                title="Buy groceries",
                description=None,
            )

            assert "Buy groceries" in result
            assert sample_task_data["task_id"] in result

    @pytest.mark.anyio
    async def test_add_task_with_title_and_description(
        self, fixed_user_id: str, sample_task_data: dict
    ) -> None:
        """add_task_impl creates task with title and description."""
        from src.agent.tools import add_task_impl

        with patch("src.agent.tools.add_task", new_callable=AsyncMock) as mock_mcp:
            mock_mcp.return_value = sample_task_data

            result = await add_task_impl(
                user_id=fixed_user_id,
                title="Buy groceries",
                description="Milk, eggs, bread",
            )

            mock_mcp.assert_called_once_with(
                user_id=fixed_user_id,
                title="Buy groceries",
                description="Milk, eggs, bread",
            )

            assert "Buy groceries" in result

    @pytest.mark.anyio
    async def test_add_task_returns_error_message(
        self, fixed_user_id: str, validation_error: dict
    ) -> None:
        """add_task_impl returns error message on failure."""
        from src.agent.tools import add_task_impl

        with patch("src.agent.tools.add_task", new_callable=AsyncMock) as mock_mcp:
            mock_mcp.return_value = validation_error

            result = await add_task_impl(user_id=fixed_user_id, title="")

            assert "Error" in result


# =============================================================================
# User Story 2: list_tasks_impl Tests
# =============================================================================


class TestListTasksImpl:
    """Tests for the list_tasks_impl function."""

    @pytest.mark.anyio
    async def test_list_tasks_returns_formatted_list(
        self, fixed_user_id: str, sample_task_list: dict
    ) -> None:
        """list_tasks_impl returns formatted task list."""
        from src.agent.tools import list_tasks_impl

        with patch("src.agent.tools.list_tasks", new_callable=AsyncMock) as mock_mcp:
            mock_mcp.return_value = sample_task_list

            result = await list_tasks_impl(user_id=fixed_user_id)

            mock_mcp.assert_called_once_with(user_id=fixed_user_id)

            assert "Buy groceries" in result
            assert "Call mom" in result
            assert "2" in result

    @pytest.mark.anyio
    async def test_list_tasks_empty_returns_message(
        self, fixed_user_id: str, empty_task_list: dict
    ) -> None:
        """list_tasks_impl returns message when no tasks exist."""
        from src.agent.tools import list_tasks_impl

        with patch("src.agent.tools.list_tasks", new_callable=AsyncMock) as mock_mcp:
            mock_mcp.return_value = empty_task_list

            result = await list_tasks_impl(user_id=fixed_user_id)

            assert "no tasks" in result.lower()

    @pytest.mark.anyio
    async def test_list_tasks_shows_completion_status(
        self, fixed_user_id: str, sample_task_list: dict
    ) -> None:
        """list_tasks_impl shows correct completion status."""
        from src.agent.tools import list_tasks_impl

        with patch("src.agent.tools.list_tasks", new_callable=AsyncMock) as mock_mcp:
            mock_mcp.return_value = sample_task_list

            result = await list_tasks_impl(user_id=fixed_user_id)

            # Check completion indicators
            assert "[ ]" in result  # Incomplete task
            assert "[✓]" in result  # Completed task


# =============================================================================
# User Story 3: complete_task_impl Tests
# =============================================================================


class TestCompleteTaskImpl:
    """Tests for the complete_task_impl function."""

    @pytest.mark.anyio
    async def test_complete_task_marks_as_done(
        self, fixed_user_id: str, sample_task_id: str, sample_task_data: dict
    ) -> None:
        """complete_task_impl marks task as complete."""
        from src.agent.tools import complete_task_impl

        completed_task = {**sample_task_data, "is_completed": True}

        with patch("src.agent.tools.complete_task", new_callable=AsyncMock) as mock_mcp:
            mock_mcp.return_value = completed_task

            result = await complete_task_impl(
                user_id=fixed_user_id,
                task_id=sample_task_id,
            )

            mock_mcp.assert_called_once_with(
                user_id=fixed_user_id,
                task_id=sample_task_id,
            )

            assert "complete" in result.lower()

    @pytest.mark.anyio
    async def test_complete_task_not_found(
        self, fixed_user_id: str, sample_task_id: str, task_not_found_error: dict
    ) -> None:
        """complete_task_impl returns error when task not found."""
        from src.agent.tools import complete_task_impl

        with patch("src.agent.tools.complete_task", new_callable=AsyncMock) as mock_mcp:
            mock_mcp.return_value = task_not_found_error

            result = await complete_task_impl(
                user_id=fixed_user_id,
                task_id=sample_task_id,
            )

            assert "couldn't find" in result.lower() or "error" in result.lower()


# =============================================================================
# User Story 4: delete_task_impl Tests
# =============================================================================


class TestDeleteTaskImpl:
    """Tests for the delete_task_impl function."""

    @pytest.mark.anyio
    async def test_delete_task_removes_task(
        self, fixed_user_id: str, sample_task_id: str
    ) -> None:
        """delete_task_impl deletes task successfully."""
        from src.agent.tools import delete_task_impl

        with patch("src.agent.tools.delete_task", new_callable=AsyncMock) as mock_mcp:
            mock_mcp.return_value = {
                "success": True,
                "task_id": sample_task_id,
                "message": "Task deleted successfully",
            }

            result = await delete_task_impl(
                user_id=fixed_user_id,
                task_id=sample_task_id,
            )

            mock_mcp.assert_called_once_with(
                user_id=fixed_user_id,
                task_id=sample_task_id,
            )

            assert "Deleted" in result

    @pytest.mark.anyio
    async def test_delete_task_not_found(
        self, fixed_user_id: str, sample_task_id: str, task_not_found_error: dict
    ) -> None:
        """delete_task_impl returns error when task not found."""
        from src.agent.tools import delete_task_impl

        with patch("src.agent.tools.delete_task", new_callable=AsyncMock) as mock_mcp:
            mock_mcp.return_value = task_not_found_error

            result = await delete_task_impl(
                user_id=fixed_user_id,
                task_id=sample_task_id,
            )

            assert "couldn't find" in result.lower() or "error" in result.lower()


# =============================================================================
# User Story 5: update_task_impl Tests
# =============================================================================


class TestUpdateTaskImpl:
    """Tests for the update_task_impl function."""

    @pytest.mark.anyio
    async def test_update_task_title(
        self, fixed_user_id: str, sample_task_id: str, sample_task_data: dict
    ) -> None:
        """update_task_impl updates task title."""
        from src.agent.tools import update_task_impl

        updated_task = {**sample_task_data, "title": "Buy fruits"}

        with patch("src.agent.tools.update_task", new_callable=AsyncMock) as mock_mcp:
            mock_mcp.return_value = updated_task

            result = await update_task_impl(
                user_id=fixed_user_id,
                task_id=sample_task_id,
                title="Buy fruits",
            )

            mock_mcp.assert_called_once_with(
                user_id=fixed_user_id,
                task_id=sample_task_id,
                title="Buy fruits",
                description=None,
            )

            assert "Updated" in result

    @pytest.mark.anyio
    async def test_update_task_description(
        self, fixed_user_id: str, sample_task_id: str, sample_task_data: dict
    ) -> None:
        """update_task_impl updates task description."""
        from src.agent.tools import update_task_impl

        updated_task = {**sample_task_data, "description": "New description"}

        with patch("src.agent.tools.update_task", new_callable=AsyncMock) as mock_mcp:
            mock_mcp.return_value = updated_task

            result = await update_task_impl(
                user_id=fixed_user_id,
                task_id=sample_task_id,
                description="New description",
            )

            assert "Updated" in result

    @pytest.mark.anyio
    async def test_update_task_not_found(
        self, fixed_user_id: str, sample_task_id: str, task_not_found_error: dict
    ) -> None:
        """update_task_impl returns error when task not found."""
        from src.agent.tools import update_task_impl

        with patch("src.agent.tools.update_task", new_callable=AsyncMock) as mock_mcp:
            mock_mcp.return_value = task_not_found_error

            result = await update_task_impl(
                user_id=fixed_user_id,
                task_id=sample_task_id,
                title="New title",
            )

            assert "couldn't find" in result.lower() or "error" in result.lower()


# =============================================================================
# User Story 7: schedule_reminder_impl Tests
# =============================================================================


class TestScheduleReminderImpl:
    """Tests for the schedule_reminder_impl function."""

    @pytest.mark.anyio
    async def test_schedule_reminder_basic(
        self, fixed_user_id: str, sample_task_id: str, sample_reminder_data: dict
    ) -> None:
        """schedule_reminder_impl schedules a basic reminder."""
        from src.agent.tools import schedule_reminder_impl

        with patch(
            "src.agent.tools.schedule_reminder", new_callable=AsyncMock
        ) as mock_mcp:
            mock_mcp.return_value = sample_reminder_data

            result = await schedule_reminder_impl(
                user_id=fixed_user_id,
                task_id=sample_task_id,
                remind_at="2026-01-09T09:00:00Z",
            )

            mock_mcp.assert_called_once_with(
                user_id=fixed_user_id,
                task_id=sample_task_id,
                remind_at="2026-01-09T09:00:00Z",
                repeat_interval_minutes=None,
                repeat_count=None,
            )

            assert "Reminder scheduled" in result

    @pytest.mark.anyio
    async def test_schedule_reminder_repeating(
        self, fixed_user_id: str, sample_task_id: str
    ) -> None:
        """schedule_reminder_impl schedules a repeating reminder."""
        from src.agent.tools import schedule_reminder_impl

        reminder_data = {
            "success": True,
            "reminder_id": 1,
            "user_id": fixed_user_id,
            "task_id": sample_task_id,
            "remind_at": "2026-01-09T09:00:00Z",
            "repeat_interval_minutes": 60,
            "repeat_count": 5,
            "triggered_count": 0,
            "is_active": True,
            "created_at": "2026-01-08T10:00:00Z",
        }

        with patch(
            "src.agent.tools.schedule_reminder", new_callable=AsyncMock
        ) as mock_mcp:
            mock_mcp.return_value = reminder_data

            result = await schedule_reminder_impl(
                user_id=fixed_user_id,
                task_id=sample_task_id,
                remind_at="2026-01-09T09:00:00Z",
                repeat_interval_minutes=60,
                repeat_count=5,
            )

            mock_mcp.assert_called_once_with(
                user_id=fixed_user_id,
                task_id=sample_task_id,
                remind_at="2026-01-09T09:00:00Z",
                repeat_interval_minutes=60,
                repeat_count=5,
            )

            assert "Reminder scheduled" in result
            assert "repeating" in result

    @pytest.mark.anyio
    async def test_schedule_reminder_task_not_found(
        self, fixed_user_id: str, sample_task_id: str, task_not_found_error: dict
    ) -> None:
        """schedule_reminder_impl returns error when task not found."""
        from src.agent.tools import schedule_reminder_impl

        with patch(
            "src.agent.tools.schedule_reminder", new_callable=AsyncMock
        ) as mock_mcp:
            mock_mcp.return_value = task_not_found_error

            result = await schedule_reminder_impl(
                user_id=fixed_user_id,
                task_id=sample_task_id,
                remind_at="2026-01-09T09:00:00Z",
            )

            assert "couldn't find" in result.lower() or "error" in result.lower()


# =============================================================================
# User Story 6: Error Translation Tests
# =============================================================================


class TestErrorTranslation:
    """Tests for error translation helper."""

    def test_translate_task_not_found(self) -> None:
        """translate_error handles TASK_NOT_FOUND."""
        from src.agent.tools import translate_error

        result = translate_error(
            {
                "success": False,
                "error": {
                    "code": "TASK_NOT_FOUND",
                    "message": "Task not found or access denied",
                },
            }
        )

        assert "couldn't find" in result.lower()
        assert "Error:" in result

    def test_translate_validation_error(self) -> None:
        """translate_error handles VALIDATION_ERROR."""
        from src.agent.tools import translate_error

        result = translate_error(
            {
                "success": False,
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": "Title cannot be empty",
                },
            }
        )

        assert "problem" in result.lower()
        assert "Title cannot be empty" in result

    def test_translate_database_error(self) -> None:
        """translate_error handles DATABASE_ERROR."""
        from src.agent.tools import translate_error

        result = translate_error(
            {
                "success": False,
                "error": {
                    "code": "DATABASE_ERROR",
                    "message": "Connection failed",
                },
            }
        )

        assert "Something went wrong" in result

    def test_translate_unknown_error(self) -> None:
        """translate_error handles unknown error codes."""
        from src.agent.tools import translate_error

        result = translate_error(
            {
                "success": False,
                "error": {
                    "code": "SOME_NEW_ERROR",
                    "message": "Something unexpected",
                },
            }
        )

        assert "Something unexpected" in result
