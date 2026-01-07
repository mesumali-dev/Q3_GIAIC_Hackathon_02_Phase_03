"""Pydantic schemas for MCP tool input/output validation.

These schemas define the data contracts for all MCP tools, ensuring
type safety and validation for AI agent interactions.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_validator, field_serializer


# ============================================================================
# Input Schemas
# ============================================================================


class AddTaskInput(BaseModel):
    """Input schema for add_task tool."""

    user_id: str = Field(..., description="Authenticated user UUID")
    title: str = Field(..., min_length=1, max_length=200, description="Task title (1-200 characters)")
    description: Optional[str] = Field(None, max_length=1000, description="Optional task description (max 1000 characters)")

    @field_validator("user_id")
    @classmethod
    def validate_user_id(cls, v: str) -> str:
        """Ensure user_id is a valid UUID string."""
        try:
            UUID(v)
        except ValueError:
            raise ValueError("user_id must be a valid UUID string")
        return v

    @field_validator("title")
    @classmethod
    def validate_title_not_empty(cls, v: str) -> str:
        """Ensure title is not just whitespace."""
        if not v.strip():
            raise ValueError("Title cannot be empty or whitespace")
        return v.strip()


class ListTasksInput(BaseModel):
    """Input schema for list_tasks tool."""

    user_id: str = Field(..., description="Authenticated user UUID")

    @field_validator("user_id")
    @classmethod
    def validate_user_id(cls, v: str) -> str:
        """Ensure user_id is a valid UUID string."""
        try:
            UUID(v)
        except ValueError:
            raise ValueError("user_id must be a valid UUID string")
        return v


class CompleteTaskInput(BaseModel):
    """Input schema for complete_task tool."""

    user_id: str = Field(..., description="Authenticated user UUID")
    task_id: str = Field(..., description="Task UUID to complete")

    @field_validator("user_id", "task_id")
    @classmethod
    def validate_uuid_fields(cls, v: str) -> str:
        """Ensure UUID fields are valid UUID strings."""
        try:
            UUID(v)
        except ValueError:
            raise ValueError("Must be a valid UUID string")
        return v


class DeleteTaskInput(BaseModel):
    """Input schema for delete_task tool."""

    user_id: str = Field(..., description="Authenticated user UUID")
    task_id: str = Field(..., description="Task UUID to delete")

    @field_validator("user_id", "task_id")
    @classmethod
    def validate_uuid_fields(cls, v: str) -> str:
        """Ensure UUID fields are valid UUID strings."""
        try:
            UUID(v)
        except ValueError:
            raise ValueError("Must be a valid UUID string")
        return v


class UpdateTaskInput(BaseModel):
    """Input schema for update_task tool."""

    user_id: str = Field(..., description="Authenticated user UUID")
    task_id: str = Field(..., description="Task UUID to update")
    title: Optional[str] = Field(None, min_length=1, max_length=200, description="New task title (optional)")
    description: Optional[str] = Field(None, max_length=1000, description="New description (optional)")

    @field_validator("user_id", "task_id")
    @classmethod
    def validate_uuid_fields(cls, v: str) -> str:
        """Ensure UUID fields are valid UUID strings."""
        try:
            UUID(v)
        except ValueError:
            raise ValueError("Must be a valid UUID string")
        return v

    @field_validator("title")
    @classmethod
    def validate_title_if_provided(cls, v: Optional[str]) -> Optional[str]:
        """Ensure title is not empty if provided."""
        if v is not None and not v.strip():
            raise ValueError("Title cannot be empty or whitespace")
        return v.strip() if v else None

    def model_post_init(self, __context) -> None:
        """Validate that at least one field is provided for update."""
        if self.title is None and self.description is None:
            raise ValueError("At least one field (title or description) must be provided for update")


# ============================================================================
# Output Schemas
# ============================================================================


class TaskOutput(BaseModel):
    """Output schema for task data (used by add_task, complete_task, update_task)."""

    success: bool = True
    task_id: str
    user_id: str
    title: str
    description: Optional[str]
    is_completed: bool
    created_at: str  # ISO 8601 format
    updated_at: str  # ISO 8601 format

    @classmethod
    def from_task(cls, task) -> "TaskOutput":
        """Convert Task model to TaskOutput schema.

        Args:
            task: Task SQLModel instance

        Returns:
            TaskOutput instance with converted data
        """
        return cls(
            task_id=str(task.id),
            user_id=str(task.user_id),
            title=task.title,
            description=task.description,
            is_completed=task.is_completed,
            created_at=task.created_at.isoformat() + "Z" if isinstance(task.created_at, datetime) else task.created_at,
            updated_at=task.updated_at.isoformat() + "Z" if isinstance(task.updated_at, datetime) else task.updated_at,
        )


class ListTasksOutput(BaseModel):
    """Output schema for list_tasks tool."""

    success: bool = True
    tasks: list[dict]
    count: int

    @classmethod
    def from_tasks(cls, tasks: list) -> "ListTasksOutput":
        """Convert list of Task models to ListTasksOutput schema.

        Args:
            tasks: List of Task SQLModel instances

        Returns:
            ListTasksOutput instance with converted data
        """
        task_dicts = [TaskOutput.from_task(task).model_dump() for task in tasks]
        return cls(tasks=task_dicts, count=len(tasks))


class DeleteTaskOutput(BaseModel):
    """Output schema for delete_task tool."""

    success: bool = True
    task_id: str
    message: str = "Task deleted successfully"


class ErrorResponse(BaseModel):
    """Output schema for error responses."""

    success: bool = False
    error: dict

    @classmethod
    def from_error(cls, code: str, message: str) -> "ErrorResponse":
        """Create error response from code and message.

        Args:
            code: Error code (e.g., 'VALIDATION_ERROR')
            message: Human-readable error message

        Returns:
            ErrorResponse instance
        """
        return cls(error={"code": code, "message": message})


# ============================================================================
# Reminder Schemas
# ============================================================================


class ScheduleReminderInput(BaseModel):
    """Input schema for schedule_reminder tool."""

    user_id: str = Field(..., description="Authenticated user UUID")
    task_id: str = Field(..., description="Task UUID to set reminder for")
    remind_at: str = Field(..., description="When to trigger reminder (ISO 8601 datetime string)")
    repeat_interval_minutes: Optional[int] = Field(
        None,
        gt=0,
        le=1440,
        description="Minutes between repeats (optional, max 1440 = 24 hours)"
    )
    repeat_count: Optional[int] = Field(
        None,
        gt=0,
        le=100,
        description="Total times to repeat (optional, max 100)"
    )

    @field_validator("user_id", "task_id")
    @classmethod
    def validate_uuid_fields(cls, v: str) -> str:
        """Ensure UUID fields are valid UUID strings."""
        try:
            UUID(v)
        except ValueError:
            raise ValueError("Must be a valid UUID string")
        return v

    @field_validator("remind_at")
    @classmethod
    def validate_remind_at(cls, v: str) -> str:
        """Ensure remind_at is a valid ISO 8601 datetime string."""
        try:
            datetime.fromisoformat(v.replace("Z", "+00:00"))
        except ValueError:
            raise ValueError("remind_at must be a valid ISO 8601 datetime string")
        return v


class ReminderOutput(BaseModel):
    """Output schema for reminder data (used by schedule_reminder)."""

    success: bool = True
    reminder_id: int
    user_id: str
    task_id: str
    remind_at: str  # ISO 8601 format
    repeat_interval_minutes: Optional[int]
    repeat_count: Optional[int]
    triggered_count: int
    is_active: bool
    created_at: str  # ISO 8601 format

    @classmethod
    def from_reminder(cls, reminder) -> "ReminderOutput":
        """Convert Reminder model to ReminderOutput schema.

        Args:
            reminder: Reminder SQLModel instance

        Returns:
            ReminderOutput instance with converted data
        """
        return cls(
            reminder_id=reminder.id,
            user_id=str(reminder.user_id),
            task_id=str(reminder.task_id),
            remind_at=reminder.remind_at.isoformat() + "Z" if isinstance(reminder.remind_at, datetime) else reminder.remind_at,
            repeat_interval_minutes=reminder.repeat_interval_minutes,
            repeat_count=reminder.repeat_count,
            triggered_count=reminder.triggered_count,
            is_active=reminder.is_active,
            created_at=reminder.created_at.isoformat() + "Z" if isinstance(reminder.created_at, datetime) else reminder.created_at,
        )
