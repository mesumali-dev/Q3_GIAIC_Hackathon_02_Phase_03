"""
Reminder API routes for creating and fetching reminders.

All endpoints require JWT authentication and verify user ownership.

@see specs/005-task-reminders/contracts/reminders.openapi.yaml for API contract
@see specs/005-task-reminders/spec.md for functional requirements
"""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from src.database import get_db
from src.middleware.auth import CurrentUser, verify_user_ownership
from src.models import Reminder, Task
from src.schemas import ReminderCreate, ReminderRead, ReminderWithTask
from src.services.reminder_service import create_reminder, delete_reminder, get_due_reminders

router = APIRouter(prefix="/api", tags=["Reminders"])


@router.post(
    "/{user_id}/reminders",
    response_model=ReminderRead,
    status_code=status.HTTP_201_CREATED,
)
def create_reminder_endpoint(
    user_id: UUID,
    data: ReminderCreate,
    current_user: CurrentUser,
    db: Annotated[Session, Depends(get_db)],
) -> ReminderRead:
    """
    Create a new reminder for a task.

    Validates that:
    - User is authenticated (JWT required)
    - user_id from JWT matches route parameter
    - task_id exists and belongs to the user
    - remind_at is a valid datetime
    - Optional repeat fields are valid (positive integers within limits)

    Returns:
        Created reminder with all fields

    Raises:
        401: If JWT is missing or invalid
        403: If user_id from JWT doesn't match route parameter
        404: If task not found or doesn't belong to user
        422: If validation fails (invalid datetime, repeat params out of range)
    """
    verify_user_ownership(current_user["user_id"], str(user_id))

    try:
        reminder = create_reminder(db, user_id, data)
        return ReminderRead.model_validate(reminder)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.get("/{user_id}/reminders/due", response_model=list[ReminderWithTask])
def get_due_reminders_endpoint(
    user_id: UUID,
    current_user: CurrentUser,
    db: Annotated[Session, Depends(get_db)],
) -> list[ReminderWithTask]:
    """
    Get all active reminders that are due for the authenticated user.

    A reminder is "due" if:
    - is_active is True
    - remind_at <= current time (UTC)

    Returns reminders ordered by remind_at (oldest first) with full task details.
    This is used to display notifications to the user.

    Returns:
        List of due reminders with task titles and descriptions

    Raises:
        401: If JWT is missing or invalid
        403: If user_id from JWT doesn't match route parameter
    """
    verify_user_ownership(current_user["user_id"], str(user_id))

    due_reminders = get_due_reminders(db, user_id)

    # Convert dict results to ReminderWithTask schema
    return [ReminderWithTask(**reminder) for reminder in due_reminders]


@router.put("/{user_id}/reminders/{reminder_id}", response_model=ReminderRead)
def update_reminder_endpoint(
    user_id: UUID,
    reminder_id: int,
    data: ReminderCreate,
    current_user: CurrentUser,
    db: Annotated[Session, Depends(get_db)],
) -> ReminderRead:
    """
    Update an existing reminder.

    Validates that:
    - User is authenticated (JWT required)
    - user_id from JWT matches route parameter
    - reminder exists and belongs to the user
    - task_id exists and belongs to the user
    - Optional repeat fields are valid (positive integers within limits)

    Returns:
        Updated reminder with all fields

    Raises:
        401: If JWT is missing or invalid
        403: If user_id from JWT doesn't match route parameter
        404: If reminder or task not found or doesn't belong to user
        422: If validation fails (invalid datetime, repeat params out of range)
    """
    verify_user_ownership(current_user["user_id"], str(user_id))

    # First verify the reminder belongs to the user
    existing_reminder = db.get(Reminder, reminder_id)
    if not existing_reminder or existing_reminder.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reminder not found or doesn't belong to user",
        )

    # Validate task exists and belongs to user
    task_statement = select(Task).where(Task.id == data.task_id, Task.user_id == user_id)
    task = db.exec(task_statement).first()
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task {data.task_id} not found or doesn't belong to user",
        )

    # Update the reminder with new data
    existing_reminder.task_id = data.task_id
    existing_reminder.remind_at = data.remind_at
    existing_reminder.repeat_interval_minutes = data.repeat_interval_minutes
    existing_reminder.repeat_count = data.repeat_count

    db.add(existing_reminder)
    db.commit()
    db.refresh(existing_reminder)

    return ReminderRead.model_validate(existing_reminder)


@router.get("/{user_id}/reminders", response_model=list[ReminderWithTask])
def get_all_user_reminders_endpoint(
    user_id: UUID,
    current_user: CurrentUser,
    db: Annotated[Session, Depends(get_db)],
) -> list[ReminderWithTask]:
    """
    Get all reminders for the authenticated user.

    Returns all reminders (active and inactive) with task details.
    This is used to display all user's reminders in the reminder management interface.

    Returns:
        List of all user's reminders with task titles and descriptions

    Raises:
        401: If JWT is missing or invalid
        403: If user_id from JWT doesn't match route parameter
    """
    verify_user_ownership(current_user["user_id"], str(user_id))

    # Get all reminders for the user (not just due ones)
    statement = (
        select(Reminder, Task)
        .join(Task, Reminder.task_id == Task.id)
        .where(Reminder.user_id == user_id)
        .order_by(Reminder.created_at.desc())
    )

    results = db.exec(statement).all()
    reminders = []

    for reminder, task in results:
        reminder_dict = {
            "id": reminder.id,
            "user_id": str(reminder.user_id),  # Ensure UUID is converted to string
            "task_id": str(reminder.task_id),  # Ensure UUID is converted to string
            "remind_at": reminder.remind_at,
            "repeat_interval_minutes": reminder.repeat_interval_minutes,
            "repeat_count": reminder.repeat_count,
            "triggered_count": reminder.triggered_count,
            "is_active": reminder.is_active,
            "created_at": reminder.created_at,
            "task_title": task.title if task else "Unknown Task",
            "task_description": task.description if task else None,
        }
        reminders.append(ReminderWithTask(**reminder_dict))

    return reminders


@router.delete(
    "/{user_id}/reminders/{reminder_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_reminder_endpoint(
    user_id: UUID,
    reminder_id: int,
    current_user: CurrentUser,
    db: Annotated[Session, Depends(get_db)],
) -> None:
    """
    Delete a reminder (permanently remove from database).

    Validates that:
    - User is authenticated (JWT required)
    - user_id from JWT matches route parameter
    - reminder exists and belongs to the user

    Returns:
        204 No Content on successful deletion

    Raises:
        401: If JWT is missing or invalid
        403: If user_id from JWT doesn't match route parameter
        404: If reminder not found or doesn't belong to user
    """
    verify_user_ownership(current_user["user_id"], str(user_id))

    deleted = delete_reminder(db, reminder_id, user_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reminder not found",
        )
