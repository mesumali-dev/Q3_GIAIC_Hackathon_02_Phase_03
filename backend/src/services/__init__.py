"""
Services package for business logic.

Exports service functions for use throughout the application.
"""

from src.services.auth_service import (
    authenticate_user,
    create_access_token,
    create_user,
    hash_password,
    verify_password,
)
from src.services.conversation_service import (
    add_message,
    create_conversation,
    delete_conversation,
    get_conversation,
    get_conversations,
    get_messages,
)
from src.services.task_service import (
    create_task,
    delete_task,
    get_task,
    get_tasks,
    toggle_complete,
    update_task,
)
from src.services.chat_service import (
    get_or_create_conversation,
    process_chat_message,
    verify_conversation_ownership,
)

__all__ = [
    "hash_password",
    "verify_password",
    "create_access_token",
    "create_user",
    "authenticate_user",
    "create_task",
    "get_tasks",
    "get_task",
    "update_task",
    "delete_task",
    "toggle_complete",
    "create_conversation",
    "get_conversations",
    "get_conversation",
    "delete_conversation",
    "add_message",
    "get_messages",
    "get_or_create_conversation",
    "process_chat_message",
    "verify_conversation_ownership",
]
