"""
Conversation API Tests

Tests for Conversation CRUD endpoints including:
- Create conversation (POST /api/{user_id}/conversations)
- List conversations (GET /api/{user_id}/conversations)
- Get conversation with messages (GET /api/{user_id}/conversations/{id})
- Delete conversation (DELETE /api/{user_id}/conversations/{id})
- Add message to conversation (POST /api/{user_id}/conversations/{id}/messages)
- User isolation (cross-user access denial)
- Message ordering (chronological)

@see specs/006-ai-todo-core-foundation/contracts/openapi.yaml
"""

import uuid
from datetime import datetime, timedelta, timezone

import jwt
import pytest
from httpx import ASGITransport, AsyncClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from src.config import get_settings
from src.database import get_db
from src.main import app
from src.models import Conversation, Message, User

# Get settings for test configuration
settings = get_settings()


# Test database setup
@pytest.fixture(name="session")
def session_fixture():
    """Create a test database session with in-memory SQLite."""
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(session: Session):
    """Create a test client with dependency overrides."""

    def get_session_override():
        return session

    app.dependency_overrides[get_db] = get_session_override
    transport = ASGITransport(app=app)
    client = AsyncClient(transport=transport, base_url="http://test")
    yield client
    app.dependency_overrides.clear()


@pytest.fixture
def anyio_backend():
    return "asyncio"


def create_test_token(
    user_id: str,
    email: str = "test@example.com",
    expired: bool = False,
    invalid_secret: bool = False,
) -> str:
    """
    Create a JWT token for testing.

    Args:
        user_id: User ID to include in token
        email: Email to include in token
        expired: If True, create an expired token
        invalid_secret: If True, sign with wrong secret

    Returns:
        JWT token string
    """
    now = datetime.now(timezone.utc)

    if expired:
        exp = now - timedelta(hours=1)
    else:
        exp = now + timedelta(hours=24)

    payload = {
        "sub": user_id,
        "email": email,
        "iat": now,
        "exp": exp,
    }

    secret = "wrong-secret" if invalid_secret else settings.BETTER_AUTH_SECRET

    return jwt.encode(payload, secret, algorithm="HS256")


# US3: Conversation and Message Storage Tests


@pytest.mark.anyio
async def test_create_conversation(client: AsyncClient, session: Session):
    """Test creating a new conversation."""
    user_id = str(uuid.uuid4())
    token = create_test_token(user_id)

    response = await client.post(
        f"/api/{user_id}/conversations",
        json={"title": "My First Conversation"},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert data["user_id"] == user_id
    assert data["title"] == "My First Conversation"
    assert "created_at" in data
    assert "updated_at" in data


@pytest.mark.anyio
async def test_create_conversation_no_title(client: AsyncClient, session: Session):
    """Test creating a conversation without a title."""
    user_id = str(uuid.uuid4())
    token = create_test_token(user_id)

    response = await client.post(
        f"/api/{user_id}/conversations",
        json={},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 201
    data = response.json()
    assert data["title"] is None


@pytest.mark.anyio
async def test_list_conversations(client: AsyncClient, session: Session):
    """Test listing all conversations for a user."""
    user_id = str(uuid.uuid4())
    token = create_test_token(user_id)

    # Create two conversations
    await client.post(
        f"/api/{user_id}/conversations",
        json={"title": "Conversation 1"},
        headers={"Authorization": f"Bearer {token}"},
    )
    await client.post(
        f"/api/{user_id}/conversations",
        json={"title": "Conversation 2"},
        headers={"Authorization": f"Bearer {token}"},
    )

    # List conversations
    response = await client.get(
        f"/api/{user_id}/conversations",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["count"] == 2
    assert len(data["conversations"]) == 2
    # Verify ordering (newest first)
    assert data["conversations"][0]["title"] == "Conversation 2"
    assert data["conversations"][1]["title"] == "Conversation 1"


@pytest.mark.anyio
async def test_get_conversation_with_messages(client: AsyncClient, session: Session):
    """Test getting a conversation with its messages."""
    user_id = str(uuid.uuid4())
    token = create_test_token(user_id)

    # Create conversation
    create_response = await client.post(
        f"/api/{user_id}/conversations",
        json={"title": "Test Conversation"},
        headers={"Authorization": f"Bearer {token}"},
    )
    conversation_id = create_response.json()["id"]

    # Add messages
    await client.post(
        f"/api/{user_id}/conversations/{conversation_id}/messages",
        json={"role": "user", "content": "Hello"},
        headers={"Authorization": f"Bearer {token}"},
    )
    await client.post(
        f"/api/{user_id}/conversations/{conversation_id}/messages",
        json={"role": "assistant", "content": "Hi there!"},
        headers={"Authorization": f"Bearer {token}"},
    )

    # Get conversation with messages
    response = await client.get(
        f"/api/{user_id}/conversations/{conversation_id}",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["conversation"]["id"] == conversation_id
    assert data["conversation"]["title"] == "Test Conversation"
    assert len(data["messages"]) == 2
    # Verify chronological ordering (oldest first)
    assert data["messages"][0]["role"] == "user"
    assert data["messages"][0]["content"] == "Hello"
    assert data["messages"][1]["role"] == "assistant"
    assert data["messages"][1]["content"] == "Hi there!"


@pytest.mark.anyio
async def test_add_message_to_conversation(client: AsyncClient, session: Session):
    """Test adding a message to a conversation."""
    user_id = str(uuid.uuid4())
    token = create_test_token(user_id)

    # Create conversation
    create_response = await client.post(
        f"/api/{user_id}/conversations",
        json={"title": "Test Conversation"},
        headers={"Authorization": f"Bearer {token}"},
    )
    conversation_id = create_response.json()["id"]

    # Add message
    response = await client.post(
        f"/api/{user_id}/conversations/{conversation_id}/messages",
        json={"role": "user", "content": "Test message"},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert data["conversation_id"] == conversation_id
    assert data["role"] == "user"
    assert data["content"] == "Test message"
    assert "created_at" in data


@pytest.mark.anyio
async def test_delete_conversation_cascade(client: AsyncClient, session: Session):
    """Test deleting a conversation cascades to delete all messages."""
    user_id = str(uuid.uuid4())
    token = create_test_token(user_id)

    # Create conversation with messages
    create_response = await client.post(
        f"/api/{user_id}/conversations",
        json={"title": "Test Conversation"},
        headers={"Authorization": f"Bearer {token}"},
    )
    conversation_id = create_response.json()["id"]

    await client.post(
        f"/api/{user_id}/conversations/{conversation_id}/messages",
        json={"role": "user", "content": "Message 1"},
        headers={"Authorization": f"Bearer {token}"},
    )
    await client.post(
        f"/api/{user_id}/conversations/{conversation_id}/messages",
        json={"role": "user", "content": "Message 2"},
        headers={"Authorization": f"Bearer {token}"},
    )

    # Delete conversation
    delete_response = await client.delete(
        f"/api/{user_id}/conversations/{conversation_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert delete_response.status_code == 204

    # Verify conversation is gone
    get_response = await client.get(
        f"/api/{user_id}/conversations/{conversation_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert get_response.status_code == 404

    # Verify messages are gone (check database directly)
    from sqlmodel import select
    from uuid import UUID

    messages = session.exec(
        select(Message).where(Message.conversation_id == UUID(conversation_id))
    ).all()
    assert len(messages) == 0


@pytest.mark.anyio
async def test_chronological_message_ordering(client: AsyncClient, session: Session):
    """Test that messages are returned in chronological order."""
    user_id = str(uuid.uuid4())
    token = create_test_token(user_id)

    # Create conversation
    create_response = await client.post(
        f"/api/{user_id}/conversations",
        json={"title": "Test Conversation"},
        headers={"Authorization": f"Bearer {token}"},
    )
    conversation_id = create_response.json()["id"]

    # Add messages with slight delays
    await client.post(
        f"/api/{user_id}/conversations/{conversation_id}/messages",
        json={"role": "user", "content": "First message"},
        headers={"Authorization": f"Bearer {token}"},
    )
    await client.post(
        f"/api/{user_id}/conversations/{conversation_id}/messages",
        json={"role": "assistant", "content": "Second message"},
        headers={"Authorization": f"Bearer {token}"},
    )
    await client.post(
        f"/api/{user_id}/conversations/{conversation_id}/messages",
        json={"role": "user", "content": "Third message"},
        headers={"Authorization": f"Bearer {token}"},
    )

    # Get conversation
    response = await client.get(
        f"/api/{user_id}/conversations/{conversation_id}",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    data = response.json()
    messages = data["messages"]
    assert len(messages) == 3
    assert messages[0]["content"] == "First message"
    assert messages[1]["content"] == "Second message"
    assert messages[2]["content"] == "Third message"


# US4: User Isolation and Authentication Scoping Tests


@pytest.mark.anyio
async def test_cross_user_conversation_access_denial(
    client: AsyncClient, session: Session
):
    """Test that User A cannot access User B's conversations."""
    user_a_id = str(uuid.uuid4())
    user_b_id = str(uuid.uuid4())
    token_a = create_test_token(user_a_id)
    token_b = create_test_token(user_b_id)

    # User B creates a conversation
    create_response = await client.post(
        f"/api/{user_b_id}/conversations",
        json={"title": "User B's Conversation"},
        headers={"Authorization": f"Bearer {token_b}"},
    )
    conversation_id = create_response.json()["id"]

    # User A tries to access User B's conversation
    response = await client.get(
        f"/api/{user_b_id}/conversations/{conversation_id}",
        headers={"Authorization": f"Bearer {token_a}"},
    )

    # Should return 403 due to user_id mismatch
    assert response.status_code == 403


@pytest.mark.anyio
async def test_cross_user_message_creation_denial(
    client: AsyncClient, session: Session
):
    """Test that User A cannot add messages to User B's conversation."""
    user_a_id = str(uuid.uuid4())
    user_b_id = str(uuid.uuid4())
    token_a = create_test_token(user_a_id)
    token_b = create_test_token(user_b_id)

    # User B creates a conversation
    create_response = await client.post(
        f"/api/{user_b_id}/conversations",
        json={"title": "User B's Conversation"},
        headers={"Authorization": f"Bearer {token_b}"},
    )
    conversation_id = create_response.json()["id"]

    # User A tries to add a message to User B's conversation
    response = await client.post(
        f"/api/{user_b_id}/conversations/{conversation_id}/messages",
        json={"role": "user", "content": "Trying to hack in"},
        headers={"Authorization": f"Bearer {token_a}"},
    )

    # Should return 403 due to user_id mismatch
    assert response.status_code == 403


@pytest.mark.anyio
async def test_user_id_mismatch_returns_403(client: AsyncClient, session: Session):
    """Test that mismatched user_id in JWT and route returns 403."""
    user_id = str(uuid.uuid4())
    different_user_id = str(uuid.uuid4())
    token = create_test_token(user_id)

    # Try to access a different user's conversations
    response = await client.get(
        f"/api/{different_user_id}/conversations",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 403
    assert "Cannot access another user's resources" in response.json()["detail"]


@pytest.mark.anyio
async def test_missing_jwt_returns_401(client: AsyncClient, session: Session):
    """Test that missing JWT returns 401."""
    user_id = str(uuid.uuid4())

    response = await client.get(f"/api/{user_id}/conversations")

    assert response.status_code == 401
    assert "Missing Authorization header" in response.json()["detail"]


# Validation Tests


@pytest.mark.anyio
async def test_invalid_message_role(client: AsyncClient, session: Session):
    """Test that invalid message role returns 422."""
    user_id = str(uuid.uuid4())
    token = create_test_token(user_id)

    # Create conversation
    create_response = await client.post(
        f"/api/{user_id}/conversations",
        json={"title": "Test Conversation"},
        headers={"Authorization": f"Bearer {token}"},
    )
    conversation_id = create_response.json()["id"]

    # Try to add message with invalid role
    response = await client.post(
        f"/api/{user_id}/conversations/{conversation_id}/messages",
        json={"role": "invalid_role", "content": "Test message"},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 422


@pytest.mark.anyio
async def test_message_content_too_long(client: AsyncClient, session: Session):
    """Test that message content exceeding 50,000 chars returns 422."""
    user_id = str(uuid.uuid4())
    token = create_test_token(user_id)

    # Create conversation
    create_response = await client.post(
        f"/api/{user_id}/conversations",
        json={"title": "Test Conversation"},
        headers={"Authorization": f"Bearer {token}"},
    )
    conversation_id = create_response.json()["id"]

    # Try to add message with content too long
    long_content = "a" * 50001
    response = await client.post(
        f"/api/{user_id}/conversations/{conversation_id}/messages",
        json={"role": "user", "content": long_content},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 422


@pytest.mark.anyio
async def test_conversation_title_too_long(client: AsyncClient, session: Session):
    """Test that conversation title exceeding 200 chars returns 422."""
    user_id = str(uuid.uuid4())
    token = create_test_token(user_id)

    long_title = "a" * 201
    response = await client.post(
        f"/api/{user_id}/conversations",
        json={"title": long_title},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 422
