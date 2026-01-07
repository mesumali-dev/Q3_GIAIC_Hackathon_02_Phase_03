"""Tests for schedule_reminder MCP tool.

Validates the schedule_reminder tool implementation including:
- Successful reminder creation with valid inputs
- Reminder creation with repeat options
- Validation error handling for invalid inputs
- Task not found error handling
- Database persistence verification
"""

import uuid
from datetime import datetime, timedelta, timezone

import pytest
from sqlmodel import Session, select

from src.models import Task, Reminder
from src.mcp.tools.schedule_reminder import schedule_reminder


# ============================================================================
# Test Fixtures
# ============================================================================


@pytest.fixture(name="test_db")
def test_db_fixture():
    """Create a test database session using the patched test database."""
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
def test_task(test_db: Session, test_user_id: str):
    """Create a test task for reminder tests."""
    task = Task(
        user_id=uuid.UUID(test_user_id),
        title="Test Task for Reminder",
        description="A task to attach reminders to"
    )
    test_db.add(task)
    test_db.commit()
    test_db.refresh(task)
    return task


@pytest.fixture
def future_datetime():
    """Generate a future datetime string in ISO 8601 format."""
    future = datetime.now(timezone.utc) + timedelta(hours=1)
    return future.isoformat().replace("+00:00", "Z")


# ============================================================================
# Success Tests
# ============================================================================


@pytest.mark.anyio
async def test_schedule_reminder_success(test_db: Session, test_user_id: str, test_task: Task, future_datetime: str):
    """Test successful reminder creation with valid inputs."""
    result = await schedule_reminder(
        user_id=test_user_id,
        task_id=str(test_task.id),
        remind_at=future_datetime
    )

    assert result["success"] is True
    assert "reminder_id" in result
    assert result["user_id"] == test_user_id
    assert result["task_id"] == str(test_task.id)
    assert result["is_active"] is True
    assert result["triggered_count"] == 0

    # Verify reminder persisted in database
    reminder = test_db.exec(
        select(Reminder).where(Reminder.user_id == uuid.UUID(test_user_id))
    ).first()
    assert reminder is not None
    assert reminder.task_id == test_task.id


@pytest.mark.anyio
async def test_schedule_reminder_with_repeat(test_db: Session, test_user_id: str, test_task: Task, future_datetime: str):
    """Test reminder creation with repeat options."""
    result = await schedule_reminder(
        user_id=test_user_id,
        task_id=str(test_task.id),
        remind_at=future_datetime,
        repeat_interval_minutes=60,
        repeat_count=5
    )

    assert result["success"] is True
    assert result["repeat_interval_minutes"] == 60
    assert result["repeat_count"] == 5

    # Verify database persistence
    reminder = test_db.exec(
        select(Reminder).where(Reminder.id == result["reminder_id"])
    ).first()
    assert reminder is not None
    assert reminder.repeat_interval_minutes == 60
    assert reminder.repeat_count == 5


# ============================================================================
# Validation Error Tests
# ============================================================================


@pytest.mark.anyio
async def test_schedule_reminder_invalid_user_id():
    """Test validation error for invalid user_id format."""
    result = await schedule_reminder(
        user_id="not-a-valid-uuid",
        task_id=str(uuid.uuid4()),
        remind_at="2025-12-25T10:00:00Z"
    )

    assert result["success"] is False
    assert result["error"]["code"] == "VALIDATION_ERROR"


@pytest.mark.anyio
async def test_schedule_reminder_invalid_task_id(test_user_id: str):
    """Test validation error for invalid task_id format."""
    result = await schedule_reminder(
        user_id=test_user_id,
        task_id="not-a-valid-uuid",
        remind_at="2025-12-25T10:00:00Z"
    )

    assert result["success"] is False
    assert result["error"]["code"] == "VALIDATION_ERROR"


@pytest.mark.anyio
async def test_schedule_reminder_invalid_datetime(test_user_id: str):
    """Test validation error for invalid datetime format."""
    result = await schedule_reminder(
        user_id=test_user_id,
        task_id=str(uuid.uuid4()),
        remind_at="not-a-valid-datetime"
    )

    assert result["success"] is False
    assert result["error"]["code"] == "VALIDATION_ERROR"


# ============================================================================
# Task Not Found Tests
# ============================================================================


@pytest.mark.anyio
async def test_schedule_reminder_task_not_found(test_user_id: str, future_datetime: str):
    """Test error when task does not exist."""
    non_existent_task_id = str(uuid.uuid4())

    result = await schedule_reminder(
        user_id=test_user_id,
        task_id=non_existent_task_id,
        remind_at=future_datetime
    )

    assert result["success"] is False
    assert "error" in result


@pytest.mark.anyio
async def test_schedule_reminder_task_belongs_to_other_user(test_db: Session, test_task: Task, future_datetime: str):
    """Test error when task belongs to a different user."""
    other_user_id = str(uuid.uuid4())

    result = await schedule_reminder(
        user_id=other_user_id,
        task_id=str(test_task.id),
        remind_at=future_datetime
    )

    assert result["success"] is False
    assert "error" in result
