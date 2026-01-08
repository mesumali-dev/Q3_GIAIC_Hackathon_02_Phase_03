"""
Schemas package for Pydantic models.

Exports all request/response schemas for use throughout the application.
"""

from src.schemas.auth import (
    AuthResponse,
    ErrorResponse,
    LoginRequest,
    RegisterRequest,
    UserResponse,
)
from src.schemas.conversation import (
    ConversationCreate,
    ConversationListResponse,
    ConversationResponse,
    ConversationWithMessagesResponse,
    MessageCreate,
    MessageResponse,
)
from src.schemas.reminder import (
    ReminderCreate,
    ReminderListResponse,
    ReminderRead,
    ReminderWithTask,
)
from src.schemas.task import (
    TaskCreate,
    TaskListResponse,
    TaskResponse,
    TaskUpdate,
)
from src.schemas.chat import (
    ChatRequest,
    ChatResponse,
    ToolCall,
)

__all__ = [
    "RegisterRequest",
    "LoginRequest",
    "UserResponse",
    "AuthResponse",
    "ErrorResponse",
    "TaskCreate",
    "TaskUpdate",
    "TaskResponse",
    "TaskListResponse",
    "ReminderCreate",
    "ReminderRead",
    "ReminderWithTask",
    "ReminderListResponse",
    "ConversationCreate",
    "ConversationResponse",
    "ConversationListResponse",
    "ConversationWithMessagesResponse",
    "MessageCreate",
    "MessageResponse",
    "ChatRequest",
    "ChatResponse",
    "ToolCall",
]
