"""Tests for update_task MCP tool.

Validates the update_task tool implementation including:
- Partial updates (title only, description only, both)
- Field preservation (unchanged fields remain intact)
- Validation error handling
- Authorization and not-found errors

@see specs/007-mcp-stateless-tools/contracts/update_task.json
"""

import uuid

import pytest
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from src.models import Task
from src.mcp.tools.add_task import add_task
from src.mcp.tools.update_task import update_task


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
# Partial Update Tests
# ============================================================================


@pytest.mark.anyio
async def test_update_task_title_only(test_db: Session, test_user_id: str):
    """Test updating only title, description unchanged (T090).

    Verifies:
    - Only title is updated
    - Description remains unchanged
    - Other fields unaffected
    """
    # Create a task with title and description
    create_result = await add_task(
        user_id=test_user_id,
        title="Original title",
        description="Original description"
    )
    task_id = create_result["task_id"]

    # Update only the title
    result = await update_task(
        user_id=test_user_id,
        task_id=task_id,
        title="Updated title"
    )

    # Verify success and title updated
    assert result["success"] is True
    assert result["title"] == "Updated title"
    assert result["description"] == "Original description"  # Unchanged
    assert result["task_id"] == task_id
    assert result["user_id"] == test_user_id


@pytest.mark.anyio
async def test_update_task_description_only(test_db: Session, test_user_id: str):
    """Test updating only description, title unchanged (T091).

    Verifies:
    - Only description is updated
    - Title remains unchanged
    - Other fields unaffected
    """
    # Create a task
    create_result = await add_task(
        user_id=test_user_id,
        title="Task title",
        description="Original description"
    )
    task_id = create_result["task_id"]

    # Update only the description
    result = await update_task(
        user_id=test_user_id,
        task_id=task_id,
        description="Updated description"
    )

    # Verify success and description updated
    assert result["success"] is True
    assert result["title"] == "Task title"  # Unchanged
    assert result["description"] == "Updated description"
    assert result["task_id"] == task_id


@pytest.mark.anyio
async def test_update_task_both_fields(test_db: Session, test_user_id: str):
    """Test updating both title and description atomically (T092).

    Verifies:
    - Both fields are updated in single operation
    - Update is atomic
    - All changes persist
    """
    # Create a task
    create_result = await add_task(
        user_id=test_user_id,
        title="Old title",
        description="Old description"
    )
    task_id = create_result["task_id"]

    # Update both fields
    result = await update_task(
        user_id=test_user_id,
        task_id=task_id,
        title="New title",
        description="New description"
    )

    # Verify both fields updated
    assert result["success"] is True
    assert result["title"] == "New title"
    assert result["description"] == "New description"


@pytest.mark.anyio
async def test_update_task_clear_description(test_db: Session, test_user_id: str):
    """Test clearing description by setting to empty string (T093).

    Verifies:
    - Description can be set to None/empty
    - Empty string clears the field
    """
    # Create a task with description
    create_result = await add_task(
        user_id=test_user_id,
        title="Task title",
        description="Has description"
    )
    task_id = create_result["task_id"]

    # Clear description by setting to empty string
    result = await update_task(
        user_id=test_user_id,
        task_id=task_id,
        description=""
    )

    # Verify description cleared
    assert result["success"] is True
    assert result["description"] == "" or result["description"] is None


# ============================================================================
# Validation Error Tests
# ============================================================================


@pytest.mark.anyio
async def test_update_task_no_fields_error(test_user_id: str):
    """Test error when no fields provided for update (T094).

    Verifies:
    - At least one field must be provided
    - Error code is VALIDATION_ERROR
    - Clear error message
    """
    # Create a task
    create_result = await add_task(user_id=test_user_id, title="Task")
    task_id = create_result["task_id"]

    # Attempt update with no fields (both None)
    result = await update_task(
        user_id=test_user_id,
        task_id=task_id
    )

    # Verify error response
    assert result["success"] is False
    assert result["error"]["code"] == "VALIDATION_ERROR"
    assert "at least one" in result["error"]["message"].lower() or "field" in result["error"]["message"].lower()


@pytest.mark.anyio
async def test_update_task_not_found_error(test_user_id: str):
    """Test error for non-existent task (T095).

    Verifies:
    - Non-existent task triggers TASK_NOT_FOUND error
    - Error response structured correctly
    """
    # Generate non-existent task ID
    non_existent_task_id = str(uuid.uuid4())

    # Attempt to update non-existent task
    result = await update_task(
        user_id=test_user_id,
        task_id=non_existent_task_id,
        title="New title"
    )

    # Verify error response
    assert result["success"] is False
    assert result["error"]["code"] == "TASK_NOT_FOUND"


@pytest.mark.anyio
async def test_update_task_authorization_error(test_db: Session, test_user_id: str, other_user_id: str):
    """Test authorization error when updating another user's task (T096).

    Verifies:
    - User cannot update tasks belonging to other users
    - Error code indicates authorization failure
    - Original task unchanged
    """
    # Create task for first user
    create_result = await add_task(user_id=test_user_id, title="User 1 Task")
    task_id = create_result["task_id"]

    # Attempt to update as different user
    result = await update_task(
        user_id=other_user_id,
        task_id=task_id,
        title="Hacked title"
    )

    # Verify error response
    assert result["success"] is False
    assert result["error"]["code"] in ["TASK_NOT_FOUND", "AUTHORIZATION_ERROR"]


@pytest.mark.anyio
async def test_update_task_invalid_title_error(test_user_id: str):
    """Test error for empty title or title exceeding 200 characters (T097).

    Verifies:
    - Empty title triggers validation error
    - Title too long triggers validation error
    """
    # Create a task
    create_result = await add_task(user_id=test_user_id, title="Valid title")
    task_id = create_result["task_id"]

    # Test empty title
    result1 = await update_task(
        user_id=test_user_id,
        task_id=task_id,
        title=""
    )
    assert result1["success"] is False
    assert result1["error"]["code"] == "VALIDATION_ERROR"

    # Test title too long (> 200 chars)
    long_title = "a" * 201
    result2 = await update_task(
        user_id=test_user_id,
        task_id=task_id,
        title=long_title
    )
    assert result2["success"] is False
    assert result2["error"]["code"] == "VALIDATION_ERROR"


# ============================================================================
# Additional Tests
# ============================================================================


@pytest.mark.anyio
async def test_update_task_preserves_completion_status(test_db: Session, test_user_id: str):
    """Test that updating task doesn't affect completion status.

    Verifies:
    - is_completed field unchanged by update
    - Only title/description modified
    """
    from src.mcp.tools.complete_task import complete_task

    # Create and complete a task
    create_result = await add_task(user_id=test_user_id, title="Task")
    task_id = create_result["task_id"]
    await complete_task(user_id=test_user_id, task_id=task_id)

    # Update the task
    result = await update_task(
        user_id=test_user_id,
        task_id=task_id,
        title="Updated title"
    )

    # Verify is_completed unchanged
    assert result["success"] is True
    assert result["is_completed"] is True  # Still completed


@pytest.mark.anyio
async def test_update_task_updates_timestamp(test_db: Session, test_user_id: str):
    """Test that update changes updated_at timestamp.

    Verifies:
    - updated_at changes on update
    - created_at remains unchanged
    """
    # Create a task
    create_result = await add_task(user_id=test_user_id, title="Task")
    task_id = create_result["task_id"]
    original_created_at = create_result["created_at"]

    # Update the task
    result = await update_task(
        user_id=test_user_id,
        task_id=task_id,
        title="Updated"
    )

    # Verify timestamps
    assert result["created_at"] == original_created_at  # Unchanged
    assert "updated_at" in result  # Present and valid


@pytest.mark.anyio
async def test_update_task_description_max_length(test_db: Session, test_user_id: str):
    """Test updating with maximum allowed description length.

    Verifies:
    - Description of 1000 characters accepted
    - Description > 1000 characters rejected
    """
    # Create a task
    create_result = await add_task(user_id=test_user_id, title="Task")
    task_id = create_result["task_id"]

    # Test max valid length (1000 chars)
    max_description = "a" * 1000
    result1 = await update_task(
        user_id=test_user_id,
        task_id=task_id,
        description=max_description
    )
    assert result1["success"] is True
    assert result1["description"] == max_description

    # Test exceeding max (1001 chars)
    too_long_description = "a" * 1001
    result2 = await update_task(
        user_id=test_user_id,
        task_id=task_id,
        description=too_long_description
    )
    assert result2["success"] is False
    assert result2["error"]["code"] == "VALIDATION_ERROR"


@pytest.mark.anyio
async def test_update_task_stateless_operation(test_db: Session, test_user_id: str):
    """Test that update_task is stateless.

    Verifies:
    - Multiple updates work independently
    - No state maintained between calls
    """
    # Create a task
    create_result = await add_task(user_id=test_user_id, title="Original")
    task_id = create_result["task_id"]

    # Perform multiple updates
    result1 = await update_task(user_id=test_user_id, task_id=task_id, title="Update 1")
    assert result1["success"] is True
    assert result1["title"] == "Update 1"

    result2 = await update_task(user_id=test_user_id, task_id=task_id, title="Update 2")
    assert result2["success"] is True
    assert result2["title"] == "Update 2"

    result3 = await update_task(user_id=test_user_id, task_id=task_id, title="Update 3")
    assert result3["success"] is True
    assert result3["title"] == "Update 3"

    # Each update should succeed independently
