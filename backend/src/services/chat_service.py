"""
Chat service for stateless conversation processing.

Orchestrates conversation management, message persistence, and agent execution
for the chat API endpoint. All operations are stateless - conversation context
is reconstructed from the database on every request.

This design enables:
- Horizontal scaling (any server can handle any request)
- Zero-downtime deployments
- Resilience to server restarts

NOTE: No module-level state variables are used. All state comes from
the database, ensuring true statelessness per FR-015.

@see specs/009-stateless-chat-api/plan.md for architecture details
@see specs/009-stateless-chat-api/research.md for design decisions
"""

from datetime import datetime, timezone
from uuid import UUID

import structlog
from sqlmodel import Session

from src.agent.runner import (
    extract_tool_calls,
    messages_to_input_list,
    run_agent_with_history,
)
from src.models import Conversation, Message
from src.schemas import ConversationCreate, MessageCreate
from src.schemas.chat import ChatRequest, ChatResponse
from src.services.conversation_service import (
    add_message,
    create_conversation,
    get_conversation,
    get_messages,
)

logger = structlog.get_logger(__name__)


def get_or_create_conversation(
    db: Session,
    user_id: UUID,
    conversation_id: UUID | None,
) -> Conversation:
    """Get existing conversation or create a new one.

    If conversation_id is provided, verifies ownership and returns
    the existing conversation. If None, creates a new conversation.

    Args:
        db: Database session
        user_id: Authenticated user's UUID
        conversation_id: Optional existing conversation ID

    Returns:
        Conversation instance (existing or newly created)

    Raises:
        ValueError: If conversation_id is provided but not found or not owned
    """
    if conversation_id is not None:
        conversation = get_conversation(db, user_id, conversation_id)
        if conversation is None:
            raise ValueError("Conversation not found or access denied")
        return conversation

    # Create new conversation
    return create_conversation(db, user_id, ConversationCreate(title=None))


def verify_conversation_ownership(
    db: Session,
    user_id: UUID,
    conversation_id: UUID,
) -> Conversation:
    """Verify that a conversation exists and belongs to the user.

    Args:
        db: Database session
        user_id: Authenticated user's UUID
        conversation_id: Conversation ID to verify

    Returns:
        Conversation instance if valid

    Raises:
        ValueError: If conversation not found
        PermissionError: If user doesn't own the conversation
    """
    conversation = get_conversation(db, user_id, conversation_id)
    if conversation is None:
        # Check if conversation exists at all
        from sqlmodel import select

        exists = db.exec(
            select(Conversation).where(Conversation.id == conversation_id)
        ).first()
        if exists:
            raise PermissionError("Access denied to conversation")
        raise ValueError("Conversation not found")
    return conversation


async def process_chat_message(
    db: Session,
    user_id: UUID,
    request: ChatRequest,
) -> ChatResponse:
    """Process a chat message through the AI agent.

    This is the main entry point for chat processing. It:
    1. Gets or creates a conversation
    2. Loads message history for context
    3. Persists the user message BEFORE agent execution
    4. Executes the agent with full history
    5. Persists the assistant response AFTER execution
    6. Returns the structured response

    Args:
        db: Database session
        user_id: Authenticated user's UUID
        request: Chat request with message and optional conversation_id

    Returns:
        ChatResponse with conversation_id, assistant_message, tool_calls

    Raises:
        ValueError: If conversation not found
        PermissionError: If user doesn't own conversation
        Various agent exceptions on execution errors
    """
    # Step 1: Get or create conversation
    is_new_conversation = request.conversation_id is None
    if request.conversation_id is not None:
        conversation = verify_conversation_ownership(
            db, user_id, request.conversation_id
        )
    else:
        conversation = get_or_create_conversation(db, user_id, None)

    logger.info(
        "chat_message_processing_start",
        user_id=str(user_id),
        conversation_id=str(conversation.id),
        is_new_conversation=is_new_conversation,
        message_length=len(request.message),
    )

    # Step 2: Load message history for context
    history = get_messages(db, conversation.id)

    logger.debug(
        "conversation_history_loaded",
        conversation_id=str(conversation.id),
        history_count=len(history),
    )

    # Step 3: Persist user message BEFORE agent execution (FR-006)
    user_message = add_message(
        db,
        conversation.id,
        MessageCreate(role="user", content=request.message),
    )

    # Step 4: Build input with history + new message
    input_messages = messages_to_input_list(history)
    input_messages.append({"role": "user", "content": request.message})

    # Step 5: Execute agent with full context
    result = await run_agent_with_history(input_messages, str(user_id))

    # Step 6: Extract response and tool calls
    assistant_message = result.final_output or ""
    tool_calls = extract_tool_calls(result)

    logger.info(
        "agent_execution_complete",
        user_id=str(user_id),
        conversation_id=str(conversation.id),
        response_length=len(assistant_message),
        tool_call_count=len(tool_calls),
    )

    # Step 7: Persist assistant message AFTER execution (FR-010)
    add_message(
        db,
        conversation.id,
        MessageCreate(role="assistant", content=assistant_message),
    )

    # Step 8: Build and return response
    return ChatResponse(
        conversation_id=conversation.id,
        assistant_message=assistant_message,
        tool_calls=tool_calls,
        created_at=datetime.now(timezone.utc),
    )
