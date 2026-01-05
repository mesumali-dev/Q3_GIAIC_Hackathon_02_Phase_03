"""
Message model for conversation history.

Each message belongs to exactly one conversation and has a role
indicating who sent it (user, assistant, or system).

@see data-model.md for schema specifications
"""

from datetime import datetime, timezone
from uuid import UUID, uuid4

from sqlmodel import Field, SQLModel


class Message(SQLModel, table=True):
    """
    Message model for conversation history.

    Each message belongs to exactly one conversation and has a role
    indicating who sent it (user, assistant, or system).
    """

    __tablename__ = "messages"

    id: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
        description="Unique message identifier",
    )
    conversation_id: UUID = Field(
        index=True,
        foreign_key="conversations.id",
        nullable=False,
        description="Parent conversation ID",
    )
    role: str = Field(
        max_length=20,
        description="Message role: user, assistant, or system",
    )
    content: str = Field(
        max_length=50000,
        description="Message text content",
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Message creation timestamp",
    )
