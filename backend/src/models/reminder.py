"""
Reminder model for task notifications.

Represents a scheduled notification for a task with optional repeat functionality.
Reminders are evaluated on-demand during API requests.

@see specs/005-task-reminders/data-model.md for schema specifications
"""

from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from sqlmodel import Field, SQLModel


class Reminder(SQLModel, table=True):
    """
    Reminder entity for task notifications.

    Represents a scheduled notification for a task with optional repeat functionality.
    Reminders are evaluated on-demand during API requests (no background workers).
    """

    __tablename__ = "reminders"

    id: Optional[int] = Field(
        default=None,
        primary_key=True,
        description="Unique reminder identifier",
    )

    # Foreign keys (adjusted to match existing UUID-based schema)
    user_id: UUID = Field(
        foreign_key="users.id",
        index=True,
        nullable=False,
        description="Owner of the reminder (from JWT)",
    )
    task_id: UUID = Field(
        foreign_key="tasks.id",
        nullable=False,
        description="Associated task",
    )

    # Timing fields
    remind_at: datetime = Field(
        index=True,
        description="When to trigger reminder (UTC)",
    )
    repeat_interval_minutes: Optional[int] = Field(
        default=None,
        gt=0,
        description="Minutes between repeats (null = one-time)",
    )
    repeat_count: Optional[int] = Field(
        default=None,
        gt=0,
        description="Total times to repeat (null = one-time)",
    )

    # State fields
    triggered_count: int = Field(
        default=0,
        ge=0,
        description="How many times reminder has triggered",
    )
    is_active: bool = Field(
        default=True,
        index=True,
        description="Whether reminder is active",
    )

    # Audit
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="When reminder was created (UTC)",
    )
