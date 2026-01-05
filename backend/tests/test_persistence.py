"""
Persistence Tests for AI-Native Todo Backend

Tests that verify data persists across server restarts:
- Task persistence after server restart
- Conversation persistence after server restart
- Message persistence after server restart

These tests verify that the stateless backend correctly persists
all business data to the database.

@see specs/006-ai-todo-core-foundation/spec.md (US1)
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
from src.models import Conversation, Message, Task

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
) -> str:
    """Create a JWT token for testing."""
    now = datetime.now(timezone.utc)
    exp = now + timedelta(hours=24)

    payload = {
        "sub": user_id,
        "email": email,
        "iat": now,
        "exp": exp,
    }

    return jwt.encode(payload, settings.BETTER_AUTH_SECRET, algorithm="HS256")


# US1: Persistence Tests


@pytest.mark.anyio
async def test_task_persistence_after_restart(client: AsyncClient, session: Session):
    """
    Test that tasks persist after server restart.

    Simulates restart by checking database directly after API creation.
    """
    user_id = str(uuid.uuid4())
    token = create_test_token(user_id)

    # Create a task via API
    create_response = await client.post(
        f"/api/{user_id}/tasks",
        json={"title": "Persistent Task", "description": "Should survive restart"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert create_response.status_code == 201
    task_id = create_response.json()["id"]

    # Simulate server restart by querying database directly
    from sqlmodel import select
    from uuid import UUID

    task = session.exec(select(Task).where(Task.id == UUID(task_id))).first()
    assert task is not None
    assert task.title == "Persistent Task"
    assert task.description == "Should survive restart"
    assert str(task.user_id) == user_id

    # Verify task is still accessible via API after "restart"
    get_response = await client.get(
        f"/api/{user_id}/tasks/{task_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert get_response.status_code == 200
    assert get_response.json()["title"] == "Persistent Task"


@pytest.mark.anyio
async def test_conversation_persistence_after_restart(
    client: AsyncClient, session: Session
):
    """
    Test that conversations persist after server restart.

    Simulates restart by checking database directly after API creation.
    """
    user_id = str(uuid.uuid4())
    token = create_test_token(user_id)

    # Create a conversation via API
    create_response = await client.post(
        f"/api/{user_id}/conversations",
        json={"title": "Persistent Conversation"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert create_response.status_code == 201
    conversation_id = create_response.json()["id"]

    # Simulate server restart by querying database directly
    from sqlmodel import select
    from uuid import UUID

    conversation = session.exec(
        select(Conversation).where(Conversation.id == UUID(conversation_id))
    ).first()
    assert conversation is not None
    assert conversation.title == "Persistent Conversation"
    assert str(conversation.user_id) == user_id

    # Verify conversation is still accessible via API after "restart"
    get_response = await client.get(
        f"/api/{user_id}/conversations/{conversation_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert get_response.status_code == 200
    assert get_response.json()["conversation"]["title"] == "Persistent Conversation"


@pytest.mark.anyio
async def test_message_persistence_after_restart(
    client: AsyncClient, session: Session
):
    """
    Test that messages persist after server restart.

    Simulates restart by checking database directly after API creation.
    """
    user_id = str(uuid.uuid4())
    token = create_test_token(user_id)

    # Create conversation
    create_conv_response = await client.post(
        f"/api/{user_id}/conversations",
        json={"title": "Test Conversation"},
        headers={"Authorization": f"Bearer {token}"},
    )
    conversation_id = create_conv_response.json()["id"]

    # Add messages
    message1_response = await client.post(
        f"/api/{user_id}/conversations/{conversation_id}/messages",
        json={"role": "user", "content": "First message"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert message1_response.status_code == 201
    message1_id = message1_response.json()["id"]

    message2_response = await client.post(
        f"/api/{user_id}/conversations/{conversation_id}/messages",
        json={"role": "assistant", "content": "Second message"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert message2_response.status_code == 201
    message2_id = message2_response.json()["id"]

    # Simulate server restart by querying database directly
    from sqlmodel import select
    from uuid import UUID

    messages = session.exec(
        select(Message).where(Message.conversation_id == UUID(conversation_id))
    ).all()
    assert len(messages) == 2

    # Verify messages are still accessible via API after "restart"
    get_response = await client.get(
        f"/api/{user_id}/conversations/{conversation_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert get_response.status_code == 200
    data = get_response.json()
    assert len(data["messages"]) == 2
    assert data["messages"][0]["content"] == "First message"
    assert data["messages"][1]["content"] == "Second message"


@pytest.mark.anyio
async def test_full_workflow_persistence(client: AsyncClient, session: Session):
    """
    Test complete workflow persists after server restart.

    Creates tasks, conversations, and messages, then verifies all persist.
    """
    user_id = str(uuid.uuid4())
    token = create_test_token(user_id)

    # Create task
    task_response = await client.post(
        f"/api/{user_id}/tasks",
        json={"title": "Build feature", "description": "Implement persistence"},
        headers={"Authorization": f"Bearer {token}"},
    )
    task_id = task_response.json()["id"]

    # Create conversation
    conv_response = await client.post(
        f"/api/{user_id}/conversations",
        json={"title": "Planning session"},
        headers={"Authorization": f"Bearer {token}"},
    )
    conversation_id = conv_response.json()["id"]

    # Add messages
    await client.post(
        f"/api/{user_id}/conversations/{conversation_id}/messages",
        json={"role": "user", "content": "How should I implement persistence?"},
        headers={"Authorization": f"Bearer {token}"},
    )
    await client.post(
        f"/api/{user_id}/conversations/{conversation_id}/messages",
        json={"role": "assistant", "content": "Use PostgreSQL for reliability."},
        headers={"Authorization": f"Bearer {token}"},
    )

    # Simulate server restart - verify all data persists
    from sqlmodel import select
    from uuid import UUID

    # Verify task
    task = session.exec(select(Task).where(Task.id == UUID(task_id))).first()
    assert task is not None
    assert task.title == "Build feature"

    # Verify conversation
    conversation = session.exec(
        select(Conversation).where(Conversation.id == UUID(conversation_id))
    ).first()
    assert conversation is not None
    assert conversation.title == "Planning session"

    # Verify messages
    messages = session.exec(
        select(Message).where(Message.conversation_id == UUID(conversation_id))
    ).all()
    assert len(messages) == 2

    # Verify all accessible via API
    task_get = await client.get(
        f"/api/{user_id}/tasks/{task_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert task_get.status_code == 200

    conv_get = await client.get(
        f"/api/{user_id}/conversations/{conversation_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert conv_get.status_code == 200
    assert len(conv_get.json()["messages"]) == 2
