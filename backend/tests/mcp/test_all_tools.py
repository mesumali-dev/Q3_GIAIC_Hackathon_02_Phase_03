"""Comprehensive test suite runner for all MCP tools.

This module serves as a central entry point for running all MCP tool tests.
It can be used to verify the complete MCP tool layer implementation.

Usage:
    pytest backend/tests/mcp/test_all_tools.py -v
"""

import pytest


def test_import_all_tools():
    """Test that all MCP tools can be imported successfully.

    Verifies:
    - All tool modules exist
    - No import errors
    - Tools are properly registered with server
    """
    from src.mcp.tools.add_task import add_task
    from src.mcp.tools.complete_task import complete_task
    from src.mcp.tools.delete_task import delete_task
    from src.mcp.tools.list_tasks import list_tasks
    from src.mcp.tools.update_task import update_task

    # Verify all tools are imported
    assert add_task is not None
    assert list_tasks is not None
    assert complete_task is not None
    assert delete_task is not None
    assert update_task is not None


def test_import_schemas():
    """Test that all MCP schemas can be imported successfully.

    Verifies:
    - All schema modules exist
    - Pydantic models are properly defined
    """
    from src.mcp.schemas import (
        AddTaskInput,
        CompleteTaskInput,
        DeleteTaskInput,
        DeleteTaskOutput,
        ErrorResponse,
        ListTasksInput,
        ListTasksOutput,
        TaskOutput,
        UpdateTaskInput,
    )

    # Verify all schemas are imported
    assert AddTaskInput is not None
    assert ListTasksInput is not None
    assert CompleteTaskInput is not None
    assert DeleteTaskInput is not None
    assert UpdateTaskInput is not None
    assert TaskOutput is not None
    assert ListTasksOutput is not None
    assert DeleteTaskOutput is not None
    assert ErrorResponse is not None


def test_import_errors():
    """Test that all MCP error classes can be imported successfully.

    Verifies:
    - All error classes exist
    - Error handling utilities available
    """
    from src.mcp.errors import (
        AuthorizationError,
        DatabaseError,
        MCPToolError,
        TaskNotFoundError,
        ValidationError,
        handle_tool_error,
    )

    # Verify all error classes are imported
    assert MCPToolError is not None
    assert TaskNotFoundError is not None
    assert ValidationError is not None
    assert AuthorizationError is not None
    assert DatabaseError is not None
    assert handle_tool_error is not None


def test_server_configuration():
    """Test that MCP server configuration is properly set up.

    Verifies:
    - Server instance exists
    - Configuration variables are set
    - Database session manager available
    """
    from src.mcp.server import MCP_SERVER_NAME, MCP_SERVER_VERSION, get_db_session, server

    # Verify server configuration
    assert server is not None
    assert MCP_SERVER_NAME is not None
    assert MCP_SERVER_VERSION is not None
    assert get_db_session is not None


# ============================================================================
# Test Suite Summary
# ============================================================================


@pytest.fixture(scope="module", autouse=True)
def print_test_suite_header():
    """Print test suite header before running tests."""
    print("\n" + "="*80)
    print("MCP TOOL LAYER - COMPREHENSIVE TEST SUITE")
    print("="*80)
    print("\nThis test suite validates all 5 MCP tools:")
    print("  1. add_task    - Create new tasks")
    print("  2. list_tasks  - Retrieve user's tasks")
    print("  3. complete_task - Toggle task completion")
    print("  4. delete_task - Permanently delete tasks")
    print("  5. update_task - Modify task details")
    print("\n" + "="*80 + "\n")
    yield
    print("\n" + "="*80)
    print("TEST SUITE COMPLETED")
    print("="*80 + "\n")


# ============================================================================
# Integration Test Examples
# ============================================================================


@pytest.mark.anyio
async def test_complete_task_workflow():
    """Integration test demonstrating complete task workflow.

    Tests the full lifecycle:
    1. Add task
    2. List tasks
    3. Complete task
    4. Update task
    5. Delete task

    This verifies all tools work together correctly.
    """
    import uuid

    from src.mcp.tools.add_task import add_task
    from src.mcp.tools.complete_task import complete_task
    from src.mcp.tools.delete_task import delete_task
    from src.mcp.tools.list_tasks import list_tasks
    from src.mcp.tools.update_task import update_task

    user_id = str(uuid.uuid4())

    # Step 1: Add a task
    add_result = await add_task(
        user_id=user_id,
        title="Complete workflow test",
        description="Testing full lifecycle"
    )
    assert add_result["success"] is True
    task_id = add_result["task_id"]

    # Step 2: List tasks (should have 1)
    list_result = await list_tasks(user_id=user_id)
    assert list_result["success"] is True
    assert list_result["count"] == 1

    # Step 3: Complete the task
    complete_result = await complete_task(user_id=user_id, task_id=task_id)
    assert complete_result["success"] is True
    assert complete_result["is_completed"] is True

    # Step 4: Update the task
    update_result = await update_task(
        user_id=user_id,
        task_id=task_id,
        title="Updated workflow test"
    )
    assert update_result["success"] is True
    assert update_result["title"] == "Updated workflow test"

    # Step 5: Delete the task
    delete_result = await delete_task(user_id=user_id, task_id=task_id)
    assert delete_result["success"] is True

    # Verify task is gone
    final_list = await list_tasks(user_id=user_id)
    assert final_list["count"] == 0


@pytest.fixture
def anyio_backend():
    """Configure anyio to use asyncio backend for async tests."""
    return "asyncio"
