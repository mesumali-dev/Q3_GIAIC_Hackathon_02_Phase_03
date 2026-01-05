"""Tests for add_task MCP tool.

Validates the add_task tool implementation including:
- Successful task creation with valid inputs
- Task creation with minimal required fields
- Validation error handling for invalid inputs
- Database persistence verification

@see specs/007-mcp-stateless-tools/contracts/add_task.json
"""

import uuid

import pytest
from sqlmodel import Session, SQLModel, create_engine, select
from sqlmodel.pool import StaticPool

from src.models import Task
from src.mcp.tools.add_task import add_task


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


# ============================================================================
# Success Tests
# ============================================================================


@pytest.mark.anyio
async def test_add_task_success(test_db: Session, test_user_id: str):
    """Test successful task creation with valid inputs (T021).

    Verifies:
    - Task is created in database
    - All fields are correctly set
    - Success response is returned
    - Task ID is generated
    """
    # Execute add_task tool
    result = await add_task(
        user_id=test_user_id,
        title="Buy groceries",
        description="Milk, eggs, bread"
    )

    # Verify success response structure
    assert result["success"] is True
    assert "task_id" in result
    assert result["user_id"] == test_user_id
    assert result["title"] == "Buy groceries"
    assert result["description"] == "Milk, eggs, bread"
    assert result["is_completed"] is False
    assert "created_at" in result
    assert "updated_at" in result

    # Verify task persisted in database
    task = test_db.exec(
        select(Task).where(Task.user_id == uuid.UUID(test_user_id))
    ).first()
    assert task is not None
    assert task.title == "Buy groceries"
    assert task.description == "Milk, eggs, bread"
    assert task.is_completed is False


@pytest.mark.anyio
async def test_add_task_minimal(test_db: Session, test_user_id: str):
    """Test task creation with only required fields (T022).

    Verifies:
    - Task can be created with only title and user_id
    - Description defaults to None
    - Default values are correctly set
    """
    # Execute add_task tool with minimal inputs
    result = await add_task(
        user_id=test_user_id,
        title="Call mom"
    )

    # Verify success response
    assert result["success"] is True
    assert result["title"] == "Call mom"
    assert result["description"] is None
    assert result["is_completed"] is False

    # Verify database persistence
    task = test_db.exec(
        select(Task).where(Task.user_id == uuid.UUID(test_user_id))
    ).first()
    assert task is not None
    assert task.title == "Call mom"
    assert task.description is None


# ============================================================================
# Validation Error Tests
# ============================================================================


@pytest.mark.anyio
async def test_add_task_validation_error_missing_title(test_user_id: str):
    """Test validation error for missing title (T023).

    Verifies:
    - Empty title triggers validation error
    - Error response has correct structure
    - Error code is VALIDATION_ERROR
    """
    # Execute add_task with empty title
    result = await add_task(
        user_id=test_user_id,
        title=""
    )

    # Verify error response
    assert result["success"] is False
    assert "error" in result
    assert result["error"]["code"] == "VALIDATION_ERROR"
    assert "message" in result["error"]


@pytest.mark.anyio
async def test_add_task_empty_title_error(test_user_id: str):
    """Test validation error for empty string title (T024).

    Verifies:
    - Whitespace-only title triggers validation error
    - Error message is clear
    """
    # Execute add_task with whitespace title
    result = await add_task(
        user_id=test_user_id,
        title="   "
    )

    # Verify error response
    assert result["success"] is False
    assert result["error"]["code"] == "VALIDATION_ERROR"
    assert "empty" in result["error"]["message"].lower() or "whitespace" in result["error"]["message"].lower()


@pytest.mark.anyio
async def test_add_task_title_too_long_error(test_user_id: str):
    """Test validation error for title exceeding 200 characters (T025).

    Verifies:
    - Title longer than 200 characters triggers validation error
    - Error code is VALIDATION_ERROR
    """
    # Create a title exceeding 200 characters
    long_title = "a" * 201

    # Execute add_task with too-long title
    result = await add_task(
        user_id=test_user_id,
        title=long_title
    )

    # Verify error response
    assert result["success"] is False
    assert result["error"]["code"] == "VALIDATION_ERROR"


@pytest.mark.anyio
async def test_add_task_invalid_uuid_error():
    """Test validation error for invalid user_id format (T026).

    Verifies:
    - Invalid UUID format triggers validation error
    - Error response is structured correctly
    """
    # Execute add_task with invalid UUID
    result = await add_task(
        user_id="not-a-valid-uuid",
        title="Test task"
    )

    # Verify error response
    assert result["success"] is False
    assert result["error"]["code"] == "VALIDATION_ERROR"


# ============================================================================
# Additional Edge Case Tests
# ============================================================================


@pytest.mark.anyio
async def test_add_task_description_max_length(test_user_id: str):
    """Test task creation with maximum allowed description length.

    Verifies:
    - Description of exactly 1000 characters is accepted
    - Task is created successfully
    """
    # Create 1000-character description (max allowed)
    max_description = "a" * 1000

    result = await add_task(
        user_id=test_user_id,
        title="Test task",
        description=max_description
    )

    # Verify success
    assert result["success"] is True
    assert result["description"] == max_description


@pytest.mark.anyio
async def test_add_task_description_too_long_error(test_user_id: str):
    """Test validation error for description exceeding 1000 characters.

    Verifies:
    - Description longer than 1000 characters triggers validation error
    """
    # Create 1001-character description (exceeds max)
    long_description = "a" * 1001

    result = await add_task(
        user_id=test_user_id,
        title="Test task",
        description=long_description
    )

    # Verify error response
    assert result["success"] is False
    assert result["error"]["code"] == "VALIDATION_ERROR"


@pytest.mark.anyio
async def test_add_task_multiple_tasks_same_user(test_db: Session, test_user_id: str):
    """Test creating multiple tasks for the same user.

    Verifies:
    - Multiple tasks can be created for same user
    - Each task gets unique ID
    - All tasks are persisted correctly
    """
    # Create first task
    result1 = await add_task(
        user_id=test_user_id,
        title="First task"
    )

    # Create second task
    result2 = await add_task(
        user_id=test_user_id,
        title="Second task"
    )

    # Verify both succeeded
    assert result1["success"] is True
    assert result2["success"] is True

    # Verify different task IDs
    assert result1["task_id"] != result2["task_id"]

    # Verify both persisted in database
    tasks = test_db.exec(
        select(Task).where(Task.user_id == uuid.UUID(test_user_id))
    ).all()
    assert len(tasks) == 2
    task_titles = {task.title for task in tasks}
    assert "First task" in task_titles
    assert "Second task" in task_titles
