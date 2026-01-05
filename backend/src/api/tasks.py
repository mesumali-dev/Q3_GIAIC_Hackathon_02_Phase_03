"""
Task API routes for CRUD operations.

All endpoints require JWT authentication and verify user ownership.

@see contracts/openapi.yaml for API contract
@see spec.md for functional requirements FR-001 through FR-016
"""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from src.database import get_db
from src.middleware.auth import CurrentUser, verify_user_ownership
from src.schemas import TaskCreate, TaskListResponse, TaskResponse, TaskUpdate
from src.services import (
    create_task,
    delete_task,
    get_task,
    get_tasks,
    toggle_complete,
    update_task,
)

router = APIRouter(prefix="/api", tags=["Tasks"])


@router.get("/{user_id}/tasks", response_model=TaskListResponse)
def list_tasks(
    user_id: UUID,
    current_user: CurrentUser,
    db: Annotated[Session, Depends(get_db)],
) -> TaskListResponse:
    """
    List all tasks for the authenticated user.

    Tasks are ordered by creation date (newest first).

    @see FR-001: GET /api/{user_id}/tasks endpoint
    """
    verify_user_ownership(current_user["user_id"], str(user_id))
    tasks = get_tasks(db, user_id)
    return TaskListResponse(
        tasks=[TaskResponse.model_validate(t) for t in tasks],
        count=len(tasks),
    )


@router.post(
    "/{user_id}/tasks",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_task_endpoint(
    user_id: UUID,
    data: TaskCreate,
    current_user: CurrentUser,
    db: Annotated[Session, Depends(get_db)],
) -> TaskResponse:
    """
    Create a new task for the authenticated user.

    @see FR-002: POST /api/{user_id}/tasks endpoint
    @see FR-013: Title validation (1-200 chars)
    @see FR-014: Description validation (max 1000 chars)
    """
    verify_user_ownership(current_user["user_id"], str(user_id))
    task = create_task(db, user_id, data)
    return TaskResponse.model_validate(task)


@router.get("/{user_id}/tasks/{task_id}", response_model=TaskResponse)
def get_task_endpoint(
    user_id: UUID,
    task_id: UUID,
    current_user: CurrentUser,
    db: Annotated[Session, Depends(get_db)],
) -> TaskResponse:
    """
    Get a single task by ID.

    @see FR-003: GET /api/{user_id}/tasks/{id} endpoint
    @see FR-011: 404 for non-existent task
    """
    verify_user_ownership(current_user["user_id"], str(user_id))
    task = get_task(db, user_id, task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )
    return TaskResponse.model_validate(task)


@router.put("/{user_id}/tasks/{task_id}", response_model=TaskResponse)
def update_task_endpoint(
    user_id: UUID,
    task_id: UUID,
    data: TaskUpdate,
    current_user: CurrentUser,
    db: Annotated[Session, Depends(get_db)],
) -> TaskResponse:
    """
    Update a task's title and/or description.

    @see FR-004: PUT /api/{user_id}/tasks/{id} endpoint
    @see FR-013: Title validation (1-200 chars)
    @see FR-014: Description validation (max 1000 chars)
    """
    verify_user_ownership(current_user["user_id"], str(user_id))
    task = update_task(db, user_id, task_id, data)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )
    return TaskResponse.model_validate(task)


@router.delete(
    "/{user_id}/tasks/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_task_endpoint(
    user_id: UUID,
    task_id: UUID,
    current_user: CurrentUser,
    db: Annotated[Session, Depends(get_db)],
) -> None:
    """
    Permanently delete a task.

    @see FR-005: DELETE /api/{user_id}/tasks/{id} endpoint
    @see FR-011: 404 for non-existent task
    """
    verify_user_ownership(current_user["user_id"], str(user_id))
    deleted = delete_task(db, user_id, task_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )


@router.patch("/{user_id}/tasks/{task_id}/complete", response_model=TaskResponse)
def toggle_task_complete_endpoint(
    user_id: UUID,
    task_id: UUID,
    current_user: CurrentUser,
    db: Annotated[Session, Depends(get_db)],
) -> TaskResponse:
    """
    Toggle the completion status of a task.

    @see FR-006: PATCH /api/{user_id}/tasks/{id}/complete endpoint
    """
    verify_user_ownership(current_user["user_id"], str(user_id))
    task = toggle_complete(db, user_id, task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )
    return TaskResponse.model_validate(task)
