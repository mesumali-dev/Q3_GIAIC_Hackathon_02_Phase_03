"""
Chat API request/response schemas.

Defines Pydantic models for the stateless chat API endpoint.

@see specs/009-stateless-chat-api/data-model.md for schema specifications
@see specs/009-stateless-chat-api/contracts/openapi.yaml for API contract
"""

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """Request schema for chat endpoint."""

    message: str = Field(
        ...,
        min_length=1,
        max_length=50000,
        description="User message content",
    )
    conversation_id: UUID | None = Field(
        default=None,
        description="Existing conversation ID to continue (omit for new conversation)",
    )


class ToolCall(BaseModel):
    """Information about an MCP tool invocation."""

    tool_name: str = Field(..., description="Name of the invoked MCP tool")
    parameters: dict[str, Any] = Field(
        default_factory=dict,
        description="Parameters passed to the tool",
    )
    result: dict[str, Any] | None = Field(
        default=None,
        description="Tool result (null if failed)",
    )
    success: bool = Field(..., description="Whether the tool call succeeded")


class ChatResponse(BaseModel):
    """Response schema for chat endpoint."""

    conversation_id: UUID = Field(
        ...,
        description="Conversation ID (new or existing)",
    )
    assistant_message: str = Field(
        ...,
        description="AI agent's response text",
    )
    tool_calls: list[ToolCall] = Field(
        default_factory=list,
        description="Array of MCP tool invocations (can be empty)",
    )
    created_at: datetime = Field(
        ...,
        description="Response timestamp",
    )

    model_config = {"from_attributes": True}
