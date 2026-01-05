"""
Task model for the todo application.

Each task belongs to exactly one user and is isolated from other users.

@see data-model.md for schema specifications
"""

from datetime import datetime, timezone
from uuid import UUID, uuid4

from sqlmodel import Field, SQLModel


class Task(SQLModel, table=True):
    """
    Task model for todo items.

    Each task belongs to exactly one user and is isolated from other users.
    """

    __tablename__ = "tasks"

    id: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
        description="Unique task identifier",
    )
    user_id: UUID = Field(
        index=True,
        foreign_key="users.id",
        nullable=False,
        description="Owner user ID (from JWT)",
    )
    title: str = Field(
        min_length=1,
        max_length=200,
        description="Task title (required)",
    )
    description: str | None = Field(
        default=None,
        max_length=1000,
        description="Task description (optional)",
    )
    is_completed: bool = Field(
        default=False,
        index=True,
        description="Completion status",
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Creation timestamp",
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Last update timestamp",
    )
