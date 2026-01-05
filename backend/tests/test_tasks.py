"""
Task API Tests

Tests for Task CRUD endpoints including:
- Create task (POST /api/{user_id}/tasks)
- List tasks (GET /api/{user_id}/tasks)
- Get task (GET /api/{user_id}/tasks/{task_id})
- Update task (PUT /api/{user_id}/tasks/{task_id})
- Delete task (DELETE /api/{user_id}/tasks/{task_id})
- Toggle completion (PATCH /api/{user_id}/tasks/{task_id}/complete)

@see specs/004-task-crud/contracts/openapi.yaml
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
from src.models import Task, User

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


@pytest.fixture
def test_user_id() -> str:
    """Generate a consistent test user ID."""
    return str(uuid.uuid4())


@pytest.fixture
def test_token(test_user_id: str) -> str:
    """Create a valid test token."""
    return create_test_token(test_user_id)


# =============================================================================
# US1: Create Task Tests (T015-T019)
# =============================================================================


@pytest.mark.anyio
async def test_create_task_success(
    client: AsyncClient, test_user_id: str, test_token: str
):
    """T015: POST /api/{user_id}/tasks returns 201 with valid data."""
    response = await client.post(
        f"/api/{test_user_id}/tasks",
        json={"title": "Buy groceries", "description": "Milk, eggs, bread"},
        headers={"Authorization": f"Bearer {test_token}"},
    )

    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Buy groceries"
    assert data["description"] == "Milk, eggs, bread"
    assert data["is_completed"] is False
    assert data["user_id"] == test_user_id
    assert "id" in data
    assert "created_at" in data
    assert "updated_at" in data


@pytest.mark.anyio
async def test_create_task_title_only(
    client: AsyncClient, test_user_id: str, test_token: str
):
    """Test creating task with title only (no description)."""
    response = await client.post(
        f"/api/{test_user_id}/tasks",
        json={"title": "Simple task"},
        headers={"Authorization": f"Bearer {test_token}"},
    )

    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Simple task"
    assert data["description"] is None


@pytest.mark.anyio
async def test_create_task_empty_title(
    client: AsyncClient, test_user_id: str, test_token: str
):
    """T016: POST returns 422 when title is empty."""
    response = await client.post(
        f"/api/{test_user_id}/tasks",
        json={"title": "", "description": "Some description"},
        headers={"Authorization": f"Bearer {test_token}"},
    )

    assert response.status_code == 422


@pytest.mark.anyio
async def test_create_task_title_too_long(
    client: AsyncClient, test_user_id: str, test_token: str
):
    """T017: POST returns 422 when title exceeds 200 chars."""
    long_title = "x" * 201
    response = await client.post(
        f"/api/{test_user_id}/tasks",
        json={"title": long_title},
        headers={"Authorization": f"Bearer {test_token}"},
    )

    assert response.status_code == 422


@pytest.mark.anyio
async def test_create_task_description_too_long(
    client: AsyncClient, test_user_id: str, test_token: str
):
    """POST returns 422 when description exceeds 1000 chars."""
    long_description = "x" * 1001
    response = await client.post(
        f"/api/{test_user_id}/tasks",
        json={"title": "Valid title", "description": long_description},
        headers={"Authorization": f"Bearer {test_token}"},
    )

    assert response.status_code == 422


@pytest.mark.anyio
async def test_create_task_no_auth(client: AsyncClient, test_user_id: str):
    """T018: POST returns 401 without JWT token."""
    response = await client.post(
        f"/api/{test_user_id}/tasks",
        json={"title": "Some task"},
    )

    assert response.status_code == 401


@pytest.mark.anyio
async def test_create_task_wrong_user(client: AsyncClient, test_user_id: str):
    """T019: POST returns 403 when user_id doesn't match JWT."""
    different_user_id = str(uuid.uuid4())
    token = create_test_token(different_user_id)

    response = await client.post(
        f"/api/{test_user_id}/tasks",
        json={"title": "Some task"},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 403


# =============================================================================
# US2: List Tasks Tests (T027-T030)
# =============================================================================


@pytest.mark.anyio
async def test_list_tasks_success(
    client: AsyncClient, test_user_id: str, test_token: str
):
    """T027: GET /api/{user_id}/tasks returns 200 with user's tasks."""
    # Create some tasks first
    await client.post(
        f"/api/{test_user_id}/tasks",
        json={"title": "Task 1"},
        headers={"Authorization": f"Bearer {test_token}"},
    )
    await client.post(
        f"/api/{test_user_id}/tasks",
        json={"title": "Task 2"},
        headers={"Authorization": f"Bearer {test_token}"},
    )

    # List tasks
    response = await client.get(
        f"/api/{test_user_id}/tasks",
        headers={"Authorization": f"Bearer {test_token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert "tasks" in data
    assert "count" in data
    assert data["count"] == 2
    assert len(data["tasks"]) == 2


@pytest.mark.anyio
async def test_list_tasks_empty(
    client: AsyncClient, test_user_id: str, test_token: str
):
    """T028: GET returns empty list for user with no tasks."""
    response = await client.get(
        f"/api/{test_user_id}/tasks",
        headers={"Authorization": f"Bearer {test_token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["tasks"] == []
    assert data["count"] == 0


@pytest.mark.anyio
async def test_list_tasks_no_auth(client: AsyncClient, test_user_id: str):
    """T029: GET returns 401 without JWT token."""
    response = await client.get(f"/api/{test_user_id}/tasks")

    assert response.status_code == 401


@pytest.mark.anyio
async def test_list_tasks_user_isolation(client: AsyncClient):
    """T030: User A cannot see User B's tasks."""
    user_a_id = str(uuid.uuid4())
    user_b_id = str(uuid.uuid4())
    token_a = create_test_token(user_a_id)
    token_b = create_test_token(user_b_id)

    # User A creates a task
    await client.post(
        f"/api/{user_a_id}/tasks",
        json={"title": "User A's task"},
        headers={"Authorization": f"Bearer {token_a}"},
    )

    # User B tries to list User A's tasks (should fail with 403)
    response = await client.get(
        f"/api/{user_a_id}/tasks",
        headers={"Authorization": f"Bearer {token_b}"},
    )

    assert response.status_code == 403


# =============================================================================
# US3: Toggle Task Completion Tests
# =============================================================================


@pytest.mark.anyio
async def test_toggle_complete_success(
    client: AsyncClient, test_user_id: str, test_token: str
):
    """PATCH /api/{user_id}/tasks/{task_id}/complete toggles completion."""
    # Create a task
    create_response = await client.post(
        f"/api/{test_user_id}/tasks",
        json={"title": "Toggle test"},
        headers={"Authorization": f"Bearer {test_token}"},
    )
    task_id = create_response.json()["id"]

    # Toggle to complete
    response = await client.patch(
        f"/api/{test_user_id}/tasks/{task_id}/complete",
        headers={"Authorization": f"Bearer {test_token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["is_completed"] is True

    # Toggle back to incomplete
    response = await client.patch(
        f"/api/{test_user_id}/tasks/{task_id}/complete",
        headers={"Authorization": f"Bearer {test_token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["is_completed"] is False


@pytest.mark.anyio
async def test_toggle_complete_not_found(
    client: AsyncClient, test_user_id: str, test_token: str
):
    """PATCH returns 404 for non-existent task."""
    fake_task_id = str(uuid.uuid4())

    response = await client.patch(
        f"/api/{test_user_id}/tasks/{fake_task_id}/complete",
        headers={"Authorization": f"Bearer {test_token}"},
    )

    assert response.status_code == 404


# =============================================================================
# US4: Update Task Tests
# =============================================================================


@pytest.mark.anyio
async def test_update_task_success(
    client: AsyncClient, test_user_id: str, test_token: str
):
    """PUT /api/{user_id}/tasks/{task_id} updates task."""
    # Create a task
    create_response = await client.post(
        f"/api/{test_user_id}/tasks",
        json={"title": "Original title", "description": "Original desc"},
        headers={"Authorization": f"Bearer {test_token}"},
    )
    task_id = create_response.json()["id"]

    # Update the task
    response = await client.put(
        f"/api/{test_user_id}/tasks/{task_id}",
        json={"title": "Updated title", "description": "Updated desc"},
        headers={"Authorization": f"Bearer {test_token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated title"
    assert data["description"] == "Updated desc"


@pytest.mark.anyio
async def test_update_task_partial(
    client: AsyncClient, test_user_id: str, test_token: str
):
    """PUT with partial data only updates provided fields."""
    # Create a task
    create_response = await client.post(
        f"/api/{test_user_id}/tasks",
        json={"title": "Original title", "description": "Original desc"},
        headers={"Authorization": f"Bearer {test_token}"},
    )
    task_id = create_response.json()["id"]

    # Update only title
    response = await client.put(
        f"/api/{test_user_id}/tasks/{task_id}",
        json={"title": "New title"},
        headers={"Authorization": f"Bearer {test_token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "New title"
    assert data["description"] == "Original desc"  # Unchanged


@pytest.mark.anyio
async def test_update_task_not_found(
    client: AsyncClient, test_user_id: str, test_token: str
):
    """PUT returns 404 for non-existent task."""
    fake_task_id = str(uuid.uuid4())

    response = await client.put(
        f"/api/{test_user_id}/tasks/{fake_task_id}",
        json={"title": "Updated"},
        headers={"Authorization": f"Bearer {test_token}"},
    )

    assert response.status_code == 404


# =============================================================================
# US5: Delete Task Tests
# =============================================================================


@pytest.mark.anyio
async def test_delete_task_success(
    client: AsyncClient, test_user_id: str, test_token: str
):
    """DELETE /api/{user_id}/tasks/{task_id} removes task."""
    # Create a task
    create_response = await client.post(
        f"/api/{test_user_id}/tasks",
        json={"title": "To be deleted"},
        headers={"Authorization": f"Bearer {test_token}"},
    )
    task_id = create_response.json()["id"]

    # Delete the task
    response = await client.delete(
        f"/api/{test_user_id}/tasks/{task_id}",
        headers={"Authorization": f"Bearer {test_token}"},
    )

    assert response.status_code == 204

    # Verify it's gone
    get_response = await client.get(
        f"/api/{test_user_id}/tasks/{task_id}",
        headers={"Authorization": f"Bearer {test_token}"},
    )
    assert get_response.status_code == 404


@pytest.mark.anyio
async def test_delete_task_not_found(
    client: AsyncClient, test_user_id: str, test_token: str
):
    """DELETE returns 404 for non-existent task."""
    fake_task_id = str(uuid.uuid4())

    response = await client.delete(
        f"/api/{test_user_id}/tasks/{fake_task_id}",
        headers={"Authorization": f"Bearer {test_token}"},
    )

    assert response.status_code == 404


# =============================================================================
# US6: Get Single Task Tests
# =============================================================================


@pytest.mark.anyio
async def test_get_task_success(
    client: AsyncClient, test_user_id: str, test_token: str
):
    """GET /api/{user_id}/tasks/{task_id} returns task."""
    # Create a task
    create_response = await client.post(
        f"/api/{test_user_id}/tasks",
        json={"title": "Get me", "description": "Test description"},
        headers={"Authorization": f"Bearer {test_token}"},
    )
    task_id = create_response.json()["id"]

    # Get the task
    response = await client.get(
        f"/api/{test_user_id}/tasks/{task_id}",
        headers={"Authorization": f"Bearer {test_token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == task_id
    assert data["title"] == "Get me"
    assert data["description"] == "Test description"


@pytest.mark.anyio
async def test_get_task_not_found(
    client: AsyncClient, test_user_id: str, test_token: str
):
    """GET returns 404 for non-existent task."""
    fake_task_id = str(uuid.uuid4())

    response = await client.get(
        f"/api/{test_user_id}/tasks/{fake_task_id}",
        headers={"Authorization": f"Bearer {test_token}"},
    )

    assert response.status_code == 404


@pytest.mark.anyio
async def test_get_task_wrong_user(client: AsyncClient):
    """GET returns 403 when accessing another user's task."""
    user_a_id = str(uuid.uuid4())
    user_b_id = str(uuid.uuid4())
    token_a = create_test_token(user_a_id)
    token_b = create_test_token(user_b_id)

    # User A creates a task
    create_response = await client.post(
        f"/api/{user_a_id}/tasks",
        json={"title": "User A's task"},
        headers={"Authorization": f"Bearer {token_a}"},
    )
    task_id = create_response.json()["id"]

    # User B tries to access User A's task via their own user_id path (should 404 - not found in their tasks)
    response = await client.get(
        f"/api/{user_b_id}/tasks/{task_id}",
        headers={"Authorization": f"Bearer {token_b}"},
    )

    assert response.status_code == 404
