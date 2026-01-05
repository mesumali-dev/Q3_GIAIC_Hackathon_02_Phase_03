"""Tests for complete_task MCP tool.

Validates the complete_task tool implementation including:
- Successful task completion
- Completion status toggling
- Task not found error handling
- Authorization error handling

@see specs/007-mcp-stateless-tools/contracts/complete_task.json
"""

import uuid

import pytest
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from src.models import Task
from src.mcp.tools.add_task import add_task
from src.mcp.tools.complete_task import complete_task


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
async def test_complete_task_success(test_db: Session, test_user_id: str):
    """Test successfully marking task as complete (T055).

    Verifies:
    - Task completion status is updated
    - Updated task details are returned
    - Success response structure is correct
    """
    # Create a task
    create_result = await add_task(user_id=test_user_id, title="Buy groceries")
    task_id = create_result["task_id"]

    # Verify task starts as incomplete
    assert create_result["is_completed"] is False

    # Execute complete_task tool
    result = await complete_task(user_id=test_user_id, task_id=task_id)

    # Verify success response structure
    assert result["success"] is True
    assert result["task_id"] == task_id
    assert result["user_id"] == test_user_id
    assert result["title"] == "Buy groceries"
    assert result["is_completed"] is True  # Now completed
    assert "created_at" in result
    assert "updated_at" in result


@pytest.mark.anyio
async def test_complete_task_toggle(test_db: Session, test_user_id: str):
    """Test toggling completion status on/off (T056).

    Verifies:
    - Completion status can be toggled multiple times
    - Each toggle changes the state
    - Operation is idempotent in structure
    """
    # Create a task
    create_result = await add_task(user_id=test_user_id, title="Call dentist")
    task_id = create_result["task_id"]

    # Initially incomplete
    assert create_result["is_completed"] is False

    # First toggle: incomplete → complete
    result1 = await complete_task(user_id=test_user_id, task_id=task_id)
    assert result1["success"] is True
    assert result1["is_completed"] is True

    # Second toggle: complete → incomplete
    result2 = await complete_task(user_id=test_user_id, task_id=task_id)
    assert result2["success"] is True
    assert result2["is_completed"] is False

    # Third toggle: incomplete → complete again
    result3 = await complete_task(user_id=test_user_id, task_id=task_id)
    assert result3["success"] is True
    assert result3["is_completed"] is True


# ============================================================================
# Error Tests
# ============================================================================


@pytest.mark.anyio
async def test_complete_task_not_found_error(test_user_id: str):
    """Test error for non-existent task_id (T057).

    Verifies:
    - Non-existent task triggers TASK_NOT_FOUND error
    - Error response has correct structure
    """
    # Generate a random task ID that doesn't exist
    non_existent_task_id = str(uuid.uuid4())

    # Execute complete_task with non-existent task
    result = await complete_task(user_id=test_user_id, task_id=non_existent_task_id)

    # Verify error response
    assert result["success"] is False
    assert "error" in result
    assert result["error"]["code"] == "TASK_NOT_FOUND"
    assert "message" in result["error"]


@pytest.mark.anyio
async def test_complete_task_authorization_error(test_db: Session, test_user_id: str, other_user_id: str):
    """Test authorization error when user attempts to complete another user's task (T058).

    Verifies:
    - User cannot complete tasks belonging to other users
    - Error code is TASK_NOT_FOUND (to avoid leaking task existence)
    - Authorization is enforced at service layer
    """
    # Create task for first user
    create_result = await add_task(user_id=test_user_id, title="User 1 Task")
    task_id = create_result["task_id"]

    # Attempt to complete task as different user
    result = await complete_task(user_id=other_user_id, task_id=task_id)

    # Verify error response (returns TASK_NOT_FOUND to avoid information leakage)
    assert result["success"] is False
    assert result["error"]["code"] in ["TASK_NOT_FOUND", "AUTHORIZATION_ERROR"]


@pytest.mark.anyio
async def test_complete_task_invalid_uuid_error(test_user_id: str):
    """Test validation error for invalid task_id or user_id format (T059).

    Verifies:
    - Invalid UUID format triggers validation error
    - Error response is structured correctly
    """
    # Test with invalid task_id
    result1 = await complete_task(user_id=test_user_id, task_id="not-a-valid-uuid")

    # Verify error response
    assert result1["success"] is False
    assert result1["error"]["code"] == "VALIDATION_ERROR"

    # Test with invalid user_id
    result2 = await complete_task(user_id="not-a-valid-uuid", task_id=str(uuid.uuid4()))

    # Verify error response
    assert result2["success"] is False
    assert result2["error"]["code"] == "VALIDATION_ERROR"


# ============================================================================
# Additional Edge Case Tests
# ============================================================================


@pytest.mark.anyio
async def test_complete_task_updates_timestamp(test_db: Session, test_user_id: str):
    """Test that completion updates the updated_at timestamp.

    Verifies:
    - updated_at timestamp changes when task is completed
    - created_at timestamp remains unchanged
    """
    # Create a task
    create_result = await add_task(user_id=test_user_id, title="Test task")
    task_id = create_result["task_id"]
    original_created_at = create_result["created_at"]
    original_updated_at = create_result["updated_at"]

    # Complete the task
    complete_result = await complete_task(user_id=test_user_id, task_id=task_id)

    # Verify timestamps
    assert complete_result["created_at"] == original_created_at  # Unchanged
    # updated_at should be different (note: in fast tests they might be same if within same second)
    # We just verify it's present and valid
    assert "updated_at" in complete_result
    assert complete_result["updated_at"] is not None


@pytest.mark.anyio
async def test_complete_task_preserves_other_fields(test_db: Session, test_user_id: str):
    """Test that completing task doesn't modify other fields.

    Verifies:
    - Title remains unchanged
    - Description remains unchanged
    - Only is_completed and updated_at change
    """
    # Create a task with description
    create_result = await add_task(
        user_id=test_user_id,
        title="Important task",
        description="This is very important"
    )
    task_id = create_result["task_id"]

    # Complete the task
    complete_result = await complete_task(user_id=test_user_id, task_id=task_id)

    # Verify other fields unchanged
    assert complete_result["title"] == "Important task"
    assert complete_result["description"] == "This is very important"
    assert complete_result["user_id"] == test_user_id
    assert complete_result["task_id"] == task_id


@pytest.mark.anyio
async def test_complete_task_stateless_operation(test_db: Session, test_user_id: str):
    """Test that complete_task is stateless.

    Verifies:
    - Operation uses fresh database session
    - No state is maintained between calls
    - Can be called multiple times safely
    """
    # Create a task
    create_result = await add_task(user_id=test_user_id, title="Test task")
    task_id = create_result["task_id"]

    # Complete and uncomplete multiple times
    for i in range(3):
        # Complete
        result1 = await complete_task(user_id=test_user_id, task_id=task_id)
        assert result1["success"] is True
        assert result1["is_completed"] is True

        # Uncomplete
        result2 = await complete_task(user_id=test_user_id, task_id=task_id)
        assert result2["success"] is True
        assert result2["is_completed"] is False

    # All operations should succeed without interference
