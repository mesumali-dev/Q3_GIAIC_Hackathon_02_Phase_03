"""
Chat API router for stateless conversation handling.

Provides the POST /api/{user_id}/chat endpoint for conversational AI interactions.
All conversation state is persisted to the database, enabling stateless operation.

@see specs/009-stateless-chat-api/contracts/openapi.yaml for API contract
@see specs/009-stateless-chat-api/quickstart.md for usage examples
"""

from typing import Annotated
from uuid import UUID

import structlog
from agents.exceptions import MaxTurnsExceeded
from fastapi import APIRouter, Depends, HTTPException, status
from openai import APIError, APIConnectionError, RateLimitError
from sqlmodel import Session

from src.database import get_db
from src.middleware.auth import CurrentUser, verify_user_ownership
from src.schemas.chat import ChatRequest, ChatResponse
from src.services.chat_service import process_chat_message

router = APIRouter(prefix="/api", tags=["Chat"])
logger = structlog.get_logger(__name__)


@router.post(
    "/{user_id}/chat",
    response_model=ChatResponse,
    status_code=status.HTTP_200_OK,
    summary="Send a message to the AI assistant",
    description="""
Send a user message and receive an AI response.

If `conversation_id` is not provided, a new conversation is created.
If `conversation_id` is provided, the message is added to the existing conversation.

The system reconstructs conversation context from the database on every request,
ensuring stateless operation and conversation persistence across server restarts.
""",
    responses={
        200: {"description": "Successful response with AI assistant message"},
        401: {"description": "Missing or invalid JWT token"},
        403: {"description": "User ID mismatch or conversation belongs to another user"},
        404: {"description": "Conversation not found"},
        422: {"description": "Validation error (empty message, invalid format)"},
        502: {"description": "AI service unavailable"},
        504: {"description": "Agent execution timeout"},
    },
)
async def send_chat_message(
    user_id: UUID,
    request: ChatRequest,
    current_user: CurrentUser,
    db: Annotated[Session, Depends(get_db)],
) -> ChatResponse:
    """Process a chat message and return AI response.

    This endpoint handles:
    - JWT authentication (via CurrentUser dependency)
    - User ID ownership validation
    - Conversation creation or continuation
    - Message persistence before/after agent execution
    - Tool call extraction and response formatting
    - Graceful error handling for agent failures

    Args:
        user_id: User ID from path (must match JWT)
        request: Chat request with message and optional conversation_id
        current_user: Authenticated user from JWT
        db: Database session

    Returns:
        ChatResponse with conversation_id, assistant_message, tool_calls

    Raises:
        HTTPException 401: If JWT is missing or invalid
        HTTPException 403: If user_id doesn't match JWT
        HTTPException 404: If conversation not found
        HTTPException 422: If message validation fails or guardrail triggered
        HTTPException 502: If AI service unavailable
        HTTPException 504: If agent takes too long
    """
    # Validate user ownership (T021)
    verify_user_ownership(current_user["user_id"], str(user_id))

    try:
        response = await process_chat_message(db, user_id, request)
        return response

    except ValueError as e:
        # Conversation not found (T028)
        logger.warning("conversation_not_found", user_id=str(user_id), error=str(e))
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found",
        )

    except PermissionError:
        # Conversation ownership mismatch (T029)
        logger.warning("conversation_access_denied", user_id=str(user_id))
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied",
        )

    except MaxTurnsExceeded:
        # Agent took too many turns (T040)
        logger.warning("agent_max_turns_exceeded", user_id=str(user_id))
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="The assistant took too long to respond",
        )

    except (APIError, APIConnectionError, RateLimitError) as e:
        # OpenAI API errors (T042)
        logger.error(
            "openai_api_error",
            user_id=str(user_id),
            error_type=type(e).__name__,
        )
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="AI service temporarily unavailable",
        )

    except Exception as e:
        # Generic exception handler (T043)
        # Log error details but don't expose to user (T044)
        logger.exception(
            "chat_processing_error",
            user_id=str(user_id),
            error_type=type(e).__name__,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred",
        )
