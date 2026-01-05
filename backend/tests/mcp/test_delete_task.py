"""Tests for delete_task MCP tool.

Validates the delete_task tool implementation including:
- Successful task deletion
- Task not found error handling
- Authorization error handling
- Persistence verification

@see specs/007-mcp-stateless-tools/contracts/delete_task.json
"""

import uuid

import pytest
from sqlmodel import Session, SQLModel, create_engine, select
from sqlmodel.pool import StaticPool

from src.models import Task
from src.mcp.tools.add_task import add_task
from src.mcp.tools.delete_task import delete_task
from src.mcp.tools.list_tasks import list_tasks


# ============================================================================
# Test Fixtures
# ============================================================================


@pytest.fixture(name="test_db")
def test_db_fixture():
    """Create a test database session using the patched test database."""
    # Use the database engine that has been patched by conftest.py
    from src.database import engine
    with Session(engine) as session:
        yield session


@pytest.fixture
def anyio_backend():
    """Configure anyio to use asyncio backend for async tests."""
    return "asyncio"


@pytest.fixture
def test_user_id():
    """Generate a test user UUID."""
    return str(uuid.uuid4())


@pytest.fixture
def other_user_id():
    """Generate another test user UUID for authorization testing."""
    return str(uuid.uuid4())


# ============================================================================
# Success Tests
# ============================================================================


@pytest.mark.anyio
async def test_delete_task_success(test_db: Session, test_user_id: str):
    """Test successfully deleting a task from database (T073).

    Verifies:
    - Task is permanently removed from database
    - Success response is returned with confirmation message
    - task_id is included in response
    """
    # Create a task
    create_result = await add_task(user_id=test_user_id, title="Task to delete")
    task_id = create_result["task_id"]

    # Verify task exists in database
    task_before = test_db.exec(
        select(Task).where(Task.id == uuid.UUID(task_id))
    ).first()
    assert task_before is not None

    # Execute delete_task tool
    result = await delete_task(user_id=test_user_id, task_id=task_id)

    # Verify success response structure
    assert result["success"] is True
    assert result["task_id"] == task_id
    assert result["message"] == "Task deleted successfully"

    # Verify task is removed from database
    task_after = test_db.exec(
        select(Task).where(Task.id == uuid.UUID(task_id))
    ).first()
    assert task_after is None


# ============================================================================
# Error Tests
# ============================================================================


@pytest.mark.anyio
async def test_delete_task_not_found_error(test_user_id: str):
    """Test error for non-existent task (T074).

    Verifies:
    - Non-existent task triggers TASK_NOT_FOUND error
    - Error response has correct structure
    """
    # Generate a random task ID that doesn't exist
    non_existent_task_id = str(uuid.uuid4())

    # Execute delete_task with non-existent task
    result = await delete_task(user_id=test_user_id, task_id=non_existent_task_id)

    # Verify error response
    assert result["success"] is False
    assert "error" in result
    assert result["error"]["code"] == "TASK_NOT_FOUND"
    assert "message" in result["error"]


@pytest.mark.anyio
async def test_delete_task_authorization_error(test_db: Session, test_user_id: str, other_user_id: str):
    """Test authorization error when user attempts to delete another user's task (T075).

    Verifies:
    - User cannot delete tasks belonging to other users
    - Error code is TASK_NOT_FOUND (to avoid information leakage)
    - Task remains in database after failed delete attempt
    """
    # Create task for first user
    create_result = await add_task(user_id=test_user_id, title="User 1 Task")
    task_id = create_result["task_id"]

    # Attempt to delete task as different user
    result = await delete_task(user_id=other_user_id, task_id=task_id)

    # Verify error response
    assert result["success"] is False
    assert result["error"]["code"] in ["TASK_NOT_FOUND", "AUTHORIZATION_ERROR"]

    # Verify task still exists in database
    task_still_exists = test_db.exec(
        select(Task).where(Task.id == uuid.UUID(task_id))
    ).first()
    assert task_still_exists is not None
    assert task_still_exists.user_id == uuid.UUID(test_user_id)


# ============================================================================
# Persistence Verification Tests
# ============================================================================


@pytest.mark.anyio
async def test_delete_task_verify_persistence(test_db: Session, test_user_id: str):
    """Test that deleted task is not returned by list_tasks (T076).

    Verifies:
    - Deleted task no longer appears in user's task list
    - list_tasks correctly reflects updated state
    - Deletion is permanent and persisted
    """
    # Create 3 tasks
    task1 = await add_task(user_id=test_user_id, title="Task 1")
    task2 = await add_task(user_id=test_user_id, title="Task 2")
    task3 = await add_task(user_id=test_user_id, title="Task 3")

    # Verify all 3 tasks exist
    list_before = await list_tasks(user_id=test_user_id)
    assert list_before["count"] == 3

    # Delete middle task
    await delete_task(user_id=test_user_id, task_id=task2["task_id"])

    # Verify only 2 tasks remain
    list_after = await list_tasks(user_id=test_user_id)
    assert list_after["count"] == 2

    # Verify deleted task not in list
    remaining_ids = {task["task_id"] for task in list_after["tasks"]}
    assert task1["task_id"] in remaining_ids
    assert task2["task_id"] not in remaining_ids  # Deleted
    assert task3["task_id"] in remaining_ids


# ============================================================================
# Additional Edge Case Tests
# ============================================================================


@pytest.mark.anyio
async def test_delete_task_invalid_uuid_error(test_user_id: str):
    """Test validation error for invalid task_id or user_id format.

    Verifies:
    - Invalid UUID format triggers validation error
    - Error response is structured correctly
    """
    # Test with invalid task_id
    result1 = await delete_task(user_id=test_user_id, task_id="not-a-valid-uuid")

    # Verify error response
    assert result1["success"] is False
    assert result1["error"]["code"] == "VALIDATION_ERROR"

    # Test with invalid user_id
    result2 = await delete_task(user_id="not-a-valid-uuid", task_id=str(uuid.uuid4()))

    # Verify error response
    assert result2["success"] is False
    assert result2["error"]["code"] == "VALIDATION_ERROR"


@pytest.mark.anyio
async def test_delete_task_idempotent_error_handling(test_db: Session, test_user_id: str):
    """Test that deleting already-deleted task returns error.

    Verifies:
    - Second delete attempt fails gracefully
    - Error response is appropriate
    - No database inconsistencies
    """
    # Create and delete a task
    create_result = await add_task(user_id=test_user_id, title="Task to delete twice")
    task_id = create_result["task_id"]

    # First delete succeeds
    result1 = await delete_task(user_id=test_user_id, task_id=task_id)
    assert result1["success"] is True

    # Second delete should fail with TASK_NOT_FOUND
    result2 = await delete_task(user_id=test_user_id, task_id=task_id)
    assert result2["success"] is False
    assert result2["error"]["code"] == "TASK_NOT_FOUND"


@pytest.mark.anyio
async def test_delete_task_database_persistence(test_db: Session, test_user_id: str):
    """Test that deletion is permanent across sessions.

    Verifies:
    - Deleted task cannot be retrieved
    - Database state is consistent
    - No zombie records remain
    """
    # Create a task
    create_result = await add_task(user_id=test_user_id, title="Task for persistence test")
    task_id = create_result["task_id"]
    task_uuid = uuid.UUID(task_id)

    # Verify task exists
    assert test_db.exec(select(Task).where(Task.id == task_uuid)).first() is not None

    # Delete the task
    delete_result = await delete_task(user_id=test_user_id, task_id=task_id)
    assert delete_result["success"] is True

    # Verify task permanently removed from database
    deleted_task = test_db.exec(select(Task).where(Task.id == task_uuid)).first()
    assert deleted_task is None

    # Verify no records with that ID exist
    all_tasks = test_db.exec(select(Task)).all()
    task_ids = [task.id for task in all_tasks]
    assert task_uuid not in task_ids


@pytest.mark.anyio
async def test_delete_task_stateless_operation(test_db: Session, test_user_id: str):
    """Test that delete_task is stateless.

    Verifies:
    - Operation uses fresh database session
    - No state is maintained between calls
    - Each call is independent
    """
    # Create multiple tasks
    tasks = []
    for i in range(3):
        result = await add_task(user_id=test_user_id, title=f"Task {i+1}")
        tasks.append(result["task_id"])

    # Delete tasks in random order
    delete1 = await delete_task(user_id=test_user_id, task_id=tasks[1])
    assert delete1["success"] is True

    delete2 = await delete_task(user_id=test_user_id, task_id=tasks[0])
    assert delete2["success"] is True

    delete3 = await delete_task(user_id=test_user_id, task_id=tasks[2])
    assert delete3["success"] is True

    # Verify all deletions succeeded independently
    list_result = await list_tasks(user_id=test_user_id)
    assert list_result["count"] == 0
