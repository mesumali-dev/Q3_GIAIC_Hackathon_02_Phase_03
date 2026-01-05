"""
Task service for business logic operations.

All methods filter by user_id to enforce multi-user isolation.

@see data-model.md for entity specifications
"""

from datetime import datetime, timezone
from uuid import UUID

from sqlmodel import Session, select

from src.models import Task
from src.schemas import TaskCreate, TaskUpdate


def create_task(db: Session, user_id: UUID, data: TaskCreate) -> Task:
    """
    Create a new task for a user.

    Args:
        db: Database session
        user_id: Owner user ID (from JWT)
        data: Task creation data

    Returns:
        Created Task instance
    """
    task = Task(
        user_id=user_id,
        title=data.title,
        description=data.description,
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


def get_tasks(db: Session, user_id: UUID) -> list[Task]:
    """
    Get all tasks for a user, ordered by creation date (newest first).

    Args:
        db: Database session
        user_id: Owner user ID (from JWT)

    Returns:
        List of Task instances
    """
    statement = (
        select(Task)
        .where(Task.user_id == user_id)
        .order_by(Task.created_at.desc())
    )
    return list(db.exec(statement).all())


def get_task(db: Session, user_id: UUID, task_id: UUID) -> Task | None:
    """
    Get a single task by ID, filtered by user ownership.

    Args:
        db: Database session
        user_id: Owner user ID (from JWT)
        task_id: Task ID to retrieve

    Returns:
        Task instance if found and owned by user, None otherwise
    """
    statement = select(Task).where(Task.id == task_id, Task.user_id == user_id)
    return db.exec(statement).first()


def update_task(
    db: Session, user_id: UUID, task_id: UUID, data: TaskUpdate
) -> Task | None:
    """
    Update a task's title and/or description.

    Only updates fields that are provided (not None).
    Automatically updates the updated_at timestamp.

    Args:
        db: Database session
        user_id: Owner user ID (from JWT)
        task_id: Task ID to update
        data: Update data (title and/or description)

    Returns:
        Updated Task instance if found and owned by user, None otherwise
    """
    task = get_task(db, user_id, task_id)
    if not task:
        return None

    if data.title is not None:
        task.title = data.title
    if data.description is not None:
        task.description = data.description

    task.updated_at = datetime.now(timezone.utc)
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


def delete_task(db: Session, user_id: UUID, task_id: UUID) -> bool:
    """
    Permanently delete a task.

    Args:
        db: Database session
        user_id: Owner user ID (from JWT)
        task_id: Task ID to delete

    Returns:
        True if task was deleted, False if not found or not owned
    """
    task = get_task(db, user_id, task_id)
    if not task:
        return False

    db.delete(task)
    db.commit()
    return True


def toggle_complete(db: Session, user_id: UUID, task_id: UUID) -> Task | None:
    """
    Toggle the completion status of a task.

    Args:
        db: Database session
        user_id: Owner user ID (from JWT)
        task_id: Task ID to toggle

    Returns:
        Updated Task instance if found and owned by user, None otherwise
    """
    task = get_task(db, user_id, task_id)
    if not task:
        return None

    task.is_completed = not task.is_completed
    task.updated_at = datetime.now(timezone.utc)
    db.add(task)
    db.commit()
    db.refresh(task)
    return task
