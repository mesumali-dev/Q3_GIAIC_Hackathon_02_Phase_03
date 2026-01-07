"""Test fixtures for agent testing.

Provides common fixtures for testing agent components including:
- Mock user contexts
- Mock MCP tool responses
- Test database sessions
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

from src.agent.context import UserContext


# =============================================================================
# User Context Fixtures
# =============================================================================


@pytest.fixture
def valid_user_id() -> str:
    """Generate a valid UUID string for testing."""
    return str(uuid4())


@pytest.fixture
def user_context(valid_user_id: str) -> UserContext:
    """Create a valid UserContext for testing."""
    return UserContext(user_id=valid_user_id)


@pytest.fixture
def fixed_user_id() -> str:
    """A fixed UUID for deterministic testing."""
    return "550e8400-e29b-41d4-a716-446655440000"


@pytest.fixture
def fixed_user_context(fixed_user_id: str) -> UserContext:
    """Create a UserContext with a fixed UUID for deterministic testing."""
    return UserContext(user_id=fixed_user_id)


# =============================================================================
# Mock Task Data Fixtures
# =============================================================================


@pytest.fixture
def sample_task_id() -> str:
    """A sample task UUID for testing."""
    return "7c9e6679-7425-40de-944b-e07fc1f90ae7"


@pytest.fixture
def sample_task_data(fixed_user_id: str, sample_task_id: str) -> dict:
    """Sample task data as returned by MCP tools."""
    return {
        "success": True,
        "task_id": sample_task_id,
        "user_id": fixed_user_id,
        "title": "Buy groceries",
        "description": "Milk, eggs, bread",
        "is_completed": False,
        "created_at": "2026-01-08T10:00:00Z",
        "updated_at": "2026-01-08T10:00:00Z",
    }


@pytest.fixture
def sample_task_list(fixed_user_id: str) -> dict:
    """Sample task list as returned by list_tasks MCP tool."""
    return {
        "success": True,
        "tasks": [
            {
                "task_id": "7c9e6679-7425-40de-944b-e07fc1f90ae7",
                "user_id": fixed_user_id,
                "title": "Buy groceries",
                "description": "Milk, eggs, bread",
                "is_completed": False,
                "created_at": "2026-01-08T10:00:00Z",
                "updated_at": "2026-01-08T10:00:00Z",
            },
            {
                "task_id": "8d0f7790-8536-51ef-a55c-f18gd2g01bf8",
                "user_id": fixed_user_id,
                "title": "Call mom",
                "description": None,
                "is_completed": True,
                "created_at": "2026-01-07T09:00:00Z",
                "updated_at": "2026-01-07T15:00:00Z",
            },
        ],
        "count": 2,
    }


@pytest.fixture
def empty_task_list() -> dict:
    """Empty task list response."""
    return {
        "success": True,
        "tasks": [],
        "count": 0,
    }


# =============================================================================
# Mock Error Response Fixtures
# =============================================================================


@pytest.fixture
def task_not_found_error() -> dict:
    """Task not found error response."""
    return {
        "success": False,
        "error": {
            "code": "TASK_NOT_FOUND",
            "message": "Task not found or access denied",
        },
    }


@pytest.fixture
def validation_error() -> dict:
    """Validation error response."""
    return {
        "success": False,
        "error": {
            "code": "VALIDATION_ERROR",
            "message": "Invalid input parameters",
        },
    }


@pytest.fixture
def database_error() -> dict:
    """Database error response."""
    return {
        "success": False,
        "error": {
            "code": "DATABASE_ERROR",
            "message": "Database operation failed",
        },
    }


# =============================================================================
# Mock Reminder Data Fixtures
# =============================================================================


@pytest.fixture
def sample_reminder_data(fixed_user_id: str, sample_task_id: str) -> dict:
    """Sample reminder data as returned by schedule_reminder MCP tool."""
    return {
        "success": True,
        "reminder_id": 1,
        "user_id": fixed_user_id,
        "task_id": sample_task_id,
        "remind_at": "2026-01-09T09:00:00Z",
        "repeat_interval_minutes": None,
        "repeat_count": None,
        "triggered_count": 0,
        "is_active": True,
        "created_at": "2026-01-08T10:00:00Z",
    }


# =============================================================================
# Mock MCP Tool Helpers
# =============================================================================


@pytest.fixture
def mock_add_task(sample_task_data: dict):
    """Mock the add_task MCP tool."""
    with patch("src.agent.tools.add_task") as mock:
        mock.return_value = sample_task_data
        yield mock


@pytest.fixture
def mock_list_tasks(sample_task_list: dict):
    """Mock the list_tasks MCP tool."""
    with patch("src.agent.tools.list_tasks") as mock:
        mock.return_value = sample_task_list
        yield mock


@pytest.fixture
def mock_complete_task(sample_task_data: dict):
    """Mock the complete_task MCP tool."""
    with patch("src.agent.tools.complete_task") as mock:
        completed_task = {**sample_task_data, "is_completed": True}
        mock.return_value = completed_task
        yield mock


@pytest.fixture
def mock_delete_task(sample_task_id: str):
    """Mock the delete_task MCP tool."""
    with patch("src.agent.tools.delete_task") as mock:
        mock.return_value = {
            "success": True,
            "task_id": sample_task_id,
            "message": "Task deleted successfully",
        }
        yield mock


@pytest.fixture
def mock_update_task(sample_task_data: dict):
    """Mock the update_task MCP tool."""
    with patch("src.agent.tools.update_task") as mock:
        mock.return_value = sample_task_data
        yield mock


@pytest.fixture
def mock_schedule_reminder(sample_reminder_data: dict):
    """Mock the schedule_reminder MCP tool."""
    with patch("src.agent.tools.schedule_reminder") as mock:
        mock.return_value = sample_reminder_data
        yield mock
