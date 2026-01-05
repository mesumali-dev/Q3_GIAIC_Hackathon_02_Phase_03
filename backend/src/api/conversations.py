"""
Conversation API routes for CRUD operations.

All endpoints require JWT authentication and verify user ownership.

@see contracts/openapi.yaml for API contract
@see spec.md for functional requirements FR-008 through FR-015
"""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from src.database import get_db
from src.middleware.auth import CurrentUser, verify_user_ownership
from src.schemas import (
    ConversationCreate,
    ConversationListResponse,
    ConversationResponse,
    ConversationWithMessagesResponse,
    MessageCreate,
    MessageResponse,
)
from src.services import (
    add_message,
    create_conversation,
    delete_conversation,
    get_conversation,
    get_conversations,
    get_messages,
)

router = APIRouter(prefix="/api", tags=["Conversations"])


@router.get("/{user_id}/conversations", response_model=ConversationListResponse)
def list_conversations(
    user_id: UUID,
    current_user: CurrentUser,
    db: Annotated[Session, Depends(get_db)],
) -> ConversationListResponse:
    """
    List all conversations for the authenticated user.

    Conversations are ordered by last update (newest first).

    @see FR-009: GET /api/{user_id}/conversations endpoint
    """
    verify_user_ownership(current_user["user_id"], str(user_id))
    conversations = get_conversations(db, user_id)
    return ConversationListResponse(
        conversations=[ConversationResponse.model_validate(c) for c in conversations],
        count=len(conversations),
    )


@router.post(
    "/{user_id}/conversations",
    response_model=ConversationResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_conversation_endpoint(
    user_id: UUID,
    data: ConversationCreate,
    current_user: CurrentUser,
    db: Annotated[Session, Depends(get_db)],
) -> ConversationResponse:
    """
    Create a new conversation for the authenticated user.

    @see FR-008: POST /api/{user_id}/conversations endpoint
    """
    verify_user_ownership(current_user["user_id"], str(user_id))
    conversation = create_conversation(db, user_id, data)
    return ConversationResponse.model_validate(conversation)


@router.get(
    "/{user_id}/conversations/{conversation_id}",
    response_model=ConversationWithMessagesResponse,
)
def get_conversation_with_messages(
    user_id: UUID,
    conversation_id: UUID,
    current_user: CurrentUser,
    db: Annotated[Session, Depends(get_db)],
) -> ConversationWithMessagesResponse:
    """
    Get a conversation with all its messages.

    Messages are ordered chronologically (oldest first).

    @see FR-010: GET /api/{user_id}/conversations/{id} endpoint
    """
    verify_user_ownership(current_user["user_id"], str(user_id))
    conversation = get_conversation(db, user_id, conversation_id)
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found",
        )

    messages = get_messages(db, conversation_id)
    return ConversationWithMessagesResponse(
        conversation=ConversationResponse.model_validate(conversation),
        messages=[MessageResponse.model_validate(m) for m in messages],
    )


@router.delete(
    "/{user_id}/conversations/{conversation_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_conversation_endpoint(
    user_id: UUID,
    conversation_id: UUID,
    current_user: CurrentUser,
    db: Annotated[Session, Depends(get_db)],
) -> None:
    """
    Permanently delete a conversation and all its messages.

    @see FR-011: DELETE /api/{user_id}/conversations/{id} endpoint
    """
    verify_user_ownership(current_user["user_id"], str(user_id))
    deleted = delete_conversation(db, user_id, conversation_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found",
        )


@router.post(
    "/{user_id}/conversations/{conversation_id}/messages",
    response_model=MessageResponse,
    status_code=status.HTTP_201_CREATED,
)
def add_message_endpoint(
    user_id: UUID,
    conversation_id: UUID,
    data: MessageCreate,
    current_user: CurrentUser,
    db: Annotated[Session, Depends(get_db)],
) -> MessageResponse:
    """
    Add a message to a conversation.

    @see FR-012: POST /api/{user_id}/conversations/{id}/messages endpoint
    """
    verify_user_ownership(current_user["user_id"], str(user_id))

    # Verify conversation exists and belongs to user
    conversation = get_conversation(db, user_id, conversation_id)
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found",
        )

    message = add_message(db, conversation_id, data)
    return MessageResponse.model_validate(message)
