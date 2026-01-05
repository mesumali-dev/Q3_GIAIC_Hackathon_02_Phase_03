"""
Conversation service for business logic operations.

All methods filter by user_id to enforce multi-user isolation.

@see data-model.md for entity specifications
"""

from datetime import datetime, timezone
from uuid import UUID

from sqlmodel import Session, select

from src.models import Conversation, Message
from src.schemas import ConversationCreate, MessageCreate


def create_conversation(
    db: Session, user_id: UUID, data: ConversationCreate
) -> Conversation:
    """
    Create a new conversation for a user.

    Args:
        db: Database session
        user_id: Owner user ID (from JWT)
        data: Conversation creation data

    Returns:
        Created Conversation instance
    """
    conversation = Conversation(
        user_id=user_id,
        title=data.title,
    )
    db.add(conversation)
    db.commit()
    db.refresh(conversation)
    return conversation


def get_conversations(db: Session, user_id: UUID) -> list[Conversation]:
    """
    Get all conversations for a user, ordered by update date (newest first).

    Args:
        db: Database session
        user_id: Owner user ID (from JWT)

    Returns:
        List of Conversation instances
    """
    statement = (
        select(Conversation)
        .where(Conversation.user_id == user_id)
        .order_by(Conversation.updated_at.desc())
    )
    return list(db.exec(statement).all())


def get_conversation(
    db: Session, user_id: UUID, conversation_id: UUID
) -> Conversation | None:
    """
    Get a single conversation by ID, filtered by user ownership.

    Args:
        db: Database session
        user_id: Owner user ID (from JWT)
        conversation_id: Conversation ID to retrieve

    Returns:
        Conversation instance if found and owned by user, None otherwise
    """
    statement = select(Conversation).where(
        Conversation.id == conversation_id, Conversation.user_id == user_id
    )
    return db.exec(statement).first()


def delete_conversation(db: Session, user_id: UUID, conversation_id: UUID) -> bool:
    """
    Permanently delete a conversation and all its messages (cascade).

    Args:
        db: Database session
        user_id: Owner user ID (from JWT)
        conversation_id: Conversation ID to delete

    Returns:
        True if conversation was deleted, False if not found or not owned
    """
    conversation = get_conversation(db, user_id, conversation_id)
    if not conversation:
        return False

    # Delete all messages first (explicit cascade)
    statement = select(Message).where(Message.conversation_id == conversation_id)
    messages = db.exec(statement).all()
    for message in messages:
        db.delete(message)

    # Delete conversation
    db.delete(conversation)
    db.commit()
    return True


def add_message(db: Session, conversation_id: UUID, data: MessageCreate) -> Message:
    """
    Add a new message to a conversation.

    Also updates the conversation's updated_at timestamp.

    Args:
        db: Database session
        conversation_id: Parent conversation ID
        data: Message creation data

    Returns:
        Created Message instance
    """
    message = Message(
        conversation_id=conversation_id,
        role=data.role,
        content=data.content,
    )
    db.add(message)

    # Update conversation timestamp
    statement = select(Conversation).where(Conversation.id == conversation_id)
    conversation = db.exec(statement).first()
    if conversation:
        conversation.updated_at = datetime.now(timezone.utc)
        db.add(conversation)

    db.commit()
    db.refresh(message)
    return message


def get_messages(db: Session, conversation_id: UUID) -> list[Message]:
    """
    Get all messages for a conversation, ordered chronologically (oldest first).

    Args:
        db: Database session
        conversation_id: Parent conversation ID

    Returns:
        List of Message instances ordered by created_at ascending
    """
    statement = (
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.asc())
    )
    return list(db.exec(statement).all())
