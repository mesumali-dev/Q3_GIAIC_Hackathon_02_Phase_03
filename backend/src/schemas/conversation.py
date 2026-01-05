"""
Conversation and Message schemas for request/response validation.

@see data-model.md for schema specifications
@see contracts/openapi.yaml for API contract
"""

from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field


# Conversation Schemas
class ConversationCreate(BaseModel):
    """Request schema for creating a conversation."""

    title: str | None = Field(default=None, max_length=200)


class ConversationResponse(BaseModel):
    """Response schema for conversation data."""

    id: UUID
    user_id: UUID
    title: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ConversationListResponse(BaseModel):
    """Response schema for conversation list."""

    conversations: list[ConversationResponse]
    count: int


# Message Schemas
class MessageCreate(BaseModel):
    """Request schema for creating a message."""

    role: Literal["user", "assistant", "system"] = Field(
        ..., description="Message role: user, assistant, or system"
    )
    content: str = Field(..., min_length=1, max_length=50000)


class MessageResponse(BaseModel):
    """Response schema for message data."""

    id: UUID
    conversation_id: UUID
    role: str
    content: str
    created_at: datetime

    model_config = {"from_attributes": True}


# Combined Schema
class ConversationWithMessagesResponse(BaseModel):
    """Response schema for conversation with messages."""

    conversation: ConversationResponse
    messages: list[MessageResponse]
