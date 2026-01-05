"""
Reminder schemas for request/response validation.

@see specs/005-task-reminders/data-model.md for schema specifications
@see specs/005-task-reminders/contracts/reminders.openapi.yaml for API contract
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class ReminderCreate(BaseModel):
    """Request schema for creating a new reminder."""

    task_id: UUID = Field(..., description="ID of the task to remind about")
    remind_at: datetime = Field(..., description="When to trigger reminder (ISO 8601)")
    repeat_interval_minutes: Optional[int] = Field(
        default=None,
        gt=0,
        le=1440,  # Max 24 hours
        description="Minutes between repeats (optional)",
    )
    repeat_count: Optional[int] = Field(
        default=None,
        gt=0,
        le=100,  # Max 100 repeats
        description="Total times to repeat (optional)",
    )


class ReminderRead(BaseModel):
    """Response schema for reading reminder data."""

    id: int
    user_id: UUID
    task_id: UUID
    remind_at: datetime
    repeat_interval_minutes: Optional[int]
    repeat_count: Optional[int]
    triggered_count: int
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class ReminderWithTask(ReminderRead):
    """Response schema for reminder with task details (for notifications)."""

    task_title: str = Field(..., description="Title of the associated task")
    task_description: Optional[str] = Field(
        default=None, description="Description of the task"
    )

    model_config = {"from_attributes": True}


class ReminderListResponse(BaseModel):
    """Response schema for reminder list."""

    reminders: list[ReminderRead]
    count: int
