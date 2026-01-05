"""
Conversation model for chat sessions.

Each conversation belongs to exactly one user and contains zero or more messages.

@see data-model.md for schema specifications
"""

from datetime import datetime, timezone
from uuid import UUID, uuid4

from sqlmodel import Field, SQLModel


class Conversation(SQLModel, table=True):
    """
    Conversation model for chat sessions.

    Each conversation belongs to exactly one user and contains
    zero or more messages.
    """

    __tablename__ = "conversations"

    id: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
        description="Unique conversation identifier",
    )
    user_id: UUID = Field(
        index=True,
        foreign_key="users.id",
        nullable=False,
        description="Owner user ID (from JWT)",
    )
    title: str | None = Field(
        default=None,
        max_length=200,
        description="Optional conversation title/summary",
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Conversation creation timestamp",
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Last message timestamp",
    )
