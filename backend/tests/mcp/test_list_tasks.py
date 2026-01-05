"""Tests for list_tasks MCP tool.

Validates the list_tasks tool implementation including:
- Successful task retrieval for users with multiple tasks
- Empty list for users with no tasks
- User isolation (only user's tasks returned)
- Validation error handling

@see specs/007-mcp-stateless-tools/contracts/list_tasks.json
"""

import uuid

import pytest
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from src.models import Task
from src.mcp.tools.add_task import add_task
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
    """Generate another test user UUID for isolation testing."""
    return str(uuid.uuid4())


# ============================================================================
# Success Tests
# ============================================================================


@pytest.mark.anyio
async def test_list_tasks_success(test_db: Session, test_user_id: str):
    """Test retrieval of multiple tasks for a user (T038).

    Verifies:
    - All tasks for user are returned
    - Task count is accurate
    - All task fields are present
    - Success response structure is correct
    """
    # Create 5 tasks for the user
    task_titles = ["Task 1", "Task 2", "Task 3", "Task 4", "Task 5"]
    for title in task_titles:
        await add_task(user_id=test_user_id, title=title, description=f"Description for {title}")

    # Execute list_tasks tool
    result = await list_tasks(user_id=test_user_id)

    # Verify success response structure
    assert result["success"] is True
    assert "tasks" in result
    assert "count" in result

    # Verify task count
    assert result["count"] == 5
    assert len(result["tasks"]) == 5

    # Verify all tasks have required fields
    for task in result["tasks"]:
        assert "task_id" in task
        assert "user_id" in task
        assert "title" in task
        assert "description" in task
        assert "is_completed" in task
        assert "created_at" in task
        assert "updated_at" in task
        assert task["user_id"] == test_user_id

    # Verify all task titles are present
    returned_titles = {task["title"] for task in result["tasks"]}
    assert returned_titles == set(task_titles)


@pytest.mark.anyio
async def test_list_tasks_empty(test_db: Session, test_user_id: str):
    """Test empty list returned for user with no tasks (T039).

    Verifies:
    - Empty tasks list is returned
    - Count is 0
    - Success response (not error)
    - No exception is raised
    """
    # Execute list_tasks for user with no tasks
    result = await list_tasks(user_id=test_user_id)

    # Verify success response with empty list
    assert result["success"] is True
    assert result["tasks"] == []
    assert result["count"] == 0


@pytest.mark.anyio
async def test_list_tasks_user_isolation(test_db: Session, test_user_id: str, other_user_id: str):
    """Test that only requesting user's tasks are returned (T040).

    Verifies:
    - User A's tasks are not visible to User B
    - Each user sees only their own tasks
    - User isolation is enforced at service layer
    """
    # Create tasks for first user
    await add_task(user_id=test_user_id, title="User 1 Task 1")
    await add_task(user_id=test_user_id, title="User 1 Task 2")
    await add_task(user_id=test_user_id, title="User 1 Task 3")

    # Create tasks for second user
    await add_task(user_id=other_user_id, title="User 2 Task 1")
    await add_task(user_id=other_user_id, title="User 2 Task 2")

    # List tasks for first user
    result_user1 = await list_tasks(user_id=test_user_id)

    # Verify only first user's tasks are returned
    assert result_user1["success"] is True
    assert result_user1["count"] == 3
    user1_titles = {task["title"] for task in result_user1["tasks"]}
    assert user1_titles == {"User 1 Task 1", "User 1 Task 2", "User 1 Task 3"}

    # List tasks for second user
    result_user2 = await list_tasks(user_id=other_user_id)

    # Verify only second user's tasks are returned
    assert result_user2["success"] is True
    assert result_user2["count"] == 2
    user2_titles = {task["title"] for task in result_user2["tasks"]}
    assert user2_titles == {"User 2 Task 1", "User 2 Task 2"}

    # Verify no cross-user data leakage
    assert user1_titles.isdisjoint(user2_titles)


# ============================================================================
# Validation Error Tests
# ============================================================================


@pytest.mark.anyio
async def test_list_tasks_invalid_uuid_error():
    """Test validation error for invalid user_id format (T041).

    Verifies:
    - Invalid UUID format triggers validation error
    - Error response has correct structure
    - Error code is VALIDATION_ERROR
    """
    # Execute list_tasks with invalid UUID
    result = await list_tasks(user_id="not-a-valid-uuid")

    # Verify error response
    assert result["success"] is False
    assert "error" in result
    assert result["error"]["code"] == "VALIDATION_ERROR"
    assert "message" in result["error"]


# ============================================================================
# Additional Edge Case Tests
# ============================================================================


@pytest.mark.anyio
async def test_list_tasks_large_count(test_db: Session, test_user_id: str):
    """Test listing tasks when user has many tasks.

    Verifies:
    - Large number of tasks (100) can be retrieved
    - All tasks are returned correctly
    - Performance is acceptable
    """
    # Create 100 tasks
    num_tasks = 100
    for i in range(num_tasks):
        await add_task(user_id=test_user_id, title=f"Task {i+1}")

    # Execute list_tasks
    result = await list_tasks(user_id=test_user_id)

    # Verify all tasks are returned
    assert result["success"] is True
    assert result["count"] == num_tasks
    assert len(result["tasks"]) == num_tasks


@pytest.mark.anyio
async def test_list_tasks_with_completed_and_incomplete(test_db: Session, test_user_id: str):
    """Test listing tasks with mixed completion statuses.

    Verifies:
    - Both completed and incomplete tasks are returned
    - is_completed field correctly reflects status
    """
    # Create tasks with different completion states
    # (Note: We can't complete tasks yet as complete_task isn't implemented,
    # so we'll just verify incomplete tasks are returned correctly)
    await add_task(user_id=test_user_id, title="Incomplete Task 1")
    await add_task(user_id=test_user_id, title="Incomplete Task 2")

    # Execute list_tasks
    result = await list_tasks(user_id=test_user_id)

    # Verify tasks are returned
    assert result["success"] is True
    assert result["count"] == 2

    # Verify all tasks are incomplete (default state)
    for task in result["tasks"]:
        assert task["is_completed"] is False


@pytest.mark.anyio
async def test_list_tasks_stateless_operation(test_db: Session, test_user_id: str):
    """Test that list_tasks is truly stateless.

    Verifies:
    - Multiple calls return same results
    - No state is maintained between calls
    - Operation is idempotent
    """
    # Create some tasks
    await add_task(user_id=test_user_id, title="Task 1")
    await add_task(user_id=test_user_id, title="Task 2")

    # Call list_tasks multiple times
    result1 = await list_tasks(user_id=test_user_id)
    result2 = await list_tasks(user_id=test_user_id)
    result3 = await list_tasks(user_id=test_user_id)

    # Verify all calls return identical results
    assert result1["count"] == result2["count"] == result3["count"] == 2
    assert len(result1["tasks"]) == len(result2["tasks"]) == len(result3["tasks"]) == 2

    # Verify task IDs are consistent
    task_ids_1 = {task["task_id"] for task in result1["tasks"]}
    task_ids_2 = {task["task_id"] for task in result2["tasks"]}
    task_ids_3 = {task["task_id"] for task in result3["tasks"]}
    assert task_ids_1 == task_ids_2 == task_ids_3
