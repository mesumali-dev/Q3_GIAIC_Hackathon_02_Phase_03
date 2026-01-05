"""
Reminder service for business logic operations.

Handles reminder evaluation, processing, and state transitions.
All methods filter by user_id to enforce multi-user isolation.

@see specs/005-task-reminders/data-model.md for entity specifications
"""

from datetime import datetime, timedelta, timezone
from uuid import UUID

from sqlmodel import Session, select

from src.models import Reminder, Task
from src.schemas import ReminderCreate


def get_due_reminders(db: Session, user_id: UUID) -> list[dict]:
    """
    Fetch all active reminders that are due for a user with task details.

    A reminder is "due" if:
    - is_active is True
    - remind_at is less than or equal to current time (UTC)
    - belongs to the specified user

    Args:
        db: Database session
        user_id: Owner user ID (from JWT)

    Returns:
        List of dictionaries with reminder and task details for notifications
    """
    now = datetime.now(timezone.utc)
    statement = (
        select(Reminder, Task)
        .join(Task, Reminder.task_id == Task.id)
        .where(Reminder.user_id == user_id)
        .where(Reminder.is_active == True)  # noqa: E712
        .where(Reminder.remind_at <= now)
        .order_by(Reminder.remind_at)
    )

    results = db.exec(statement).all()
    return [
        {
            "id": reminder.id,
            "user_id": reminder.user_id,
            "task_id": reminder.task_id,
            "remind_at": reminder.remind_at,
            "repeat_interval_minutes": reminder.repeat_interval_minutes,
            "repeat_count": reminder.repeat_count,
            "triggered_count": reminder.triggered_count,
            "is_active": reminder.is_active,
            "created_at": reminder.created_at,
            "task_title": task.title,
            "task_description": task.description,
        }
        for reminder, task in results
    ]


def process_reminder(db: Session, reminder_id: int, user_id: UUID) -> Reminder | None:
    """
    Process a due reminder by updating its state.

    State transitions:
    1. Increment triggered_count
    2. If repeating and more repeats remain:
       - Calculate next remind_at (current remind_at + interval)
       - Keep is_active = True
    3. If one-time OR no more repeats remain:
       - Set is_active = False (deactivate)

    Args:
        db: Database session
        reminder_id: Reminder ID to process
        user_id: Owner user ID (from JWT) for validation

    Returns:
        Updated Reminder instance if found and owned by user, None otherwise
    """
    # Fetch reminder with user ownership validation
    statement = select(Reminder).where(
        Reminder.id == reminder_id, Reminder.user_id == user_id
    )
    reminder = db.exec(statement).first()

    if not reminder:
        return None

    # Increment triggered count
    reminder.triggered_count += 1

    # Check if this is a repeating reminder with more repeats remaining
    if (
        reminder.repeat_interval_minutes is not None
        and reminder.repeat_count is not None
        and reminder.triggered_count < reminder.repeat_count
    ):
        # Schedule next repeat
        reminder.remind_at = reminder.remind_at + timedelta(
            minutes=reminder.repeat_interval_minutes
        )
    else:
        # No more repeats or one-time reminder - deactivate
        reminder.is_active = False

    db.add(reminder)
    db.commit()
    db.refresh(reminder)
    return reminder


def create_reminder(db: Session, user_id: UUID, data: ReminderCreate) -> Reminder:
    """
    Create a new reminder for a task.

    Validates that the task exists and belongs to the user.

    Args:
        db: Database session
        user_id: Owner user ID (from JWT)
        data: Reminder creation data

    Returns:
        Created Reminder instance

    Raises:
        ValueError: If task not found or doesn't belong to user
    """
    # Validate task exists and belongs to user
    task_statement = select(Task).where(Task.id == data.task_id, Task.user_id == user_id)
    task = db.exec(task_statement).first()
    if not task:
        raise ValueError(f"Task {data.task_id} not found or doesn't belong to user")

    reminder = Reminder(
        user_id=user_id,
        task_id=data.task_id,
        remind_at=data.remind_at,
        repeat_interval_minutes=data.repeat_interval_minutes,
        repeat_count=data.repeat_count,
    )
    db.add(reminder)
    db.commit()
    db.refresh(reminder)
    return reminder


def delete_reminder(db: Session, reminder_id: int, user_id: UUID) -> bool:
    """
    Delete a reminder (permanently remove from database).

    Args:
        db: Database session
        reminder_id: Reminder ID to delete
        user_id: Owner user ID (from JWT) for validation

    Returns:
        True if reminder was deleted, False if not found or not owned by user
    """
    # Fetch reminder with user ownership validation
    statement = select(Reminder).where(
        Reminder.id == reminder_id, Reminder.user_id == user_id
    )
    reminder = db.exec(statement).first()

    if not reminder:
        return False

    db.delete(reminder)
    db.commit()
    return True
