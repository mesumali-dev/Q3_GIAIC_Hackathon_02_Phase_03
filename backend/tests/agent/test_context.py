"""Tests for UserContext validation."""

import pytest
from uuid import uuid4

from src.agent.context import UserContext


class TestUserContextCreation:
    """Tests for UserContext initialization and validation."""

    def test_valid_uuid_creates_context(self) -> None:
        """UserContext accepts valid UUID strings."""
        user_id = str(uuid4())
        context = UserContext(user_id=user_id)
        assert context.user_id == user_id

    def test_fixed_uuid_creates_context(self) -> None:
        """UserContext accepts specific UUID format."""
        user_id = "550e8400-e29b-41d4-a716-446655440000"
        context = UserContext(user_id=user_id)
        assert context.user_id == user_id

    def test_empty_string_raises_error(self) -> None:
        """Empty user_id string raises ValueError."""
        with pytest.raises(ValueError, match="user_id cannot be empty"):
            UserContext(user_id="")

    def test_whitespace_only_raises_error(self) -> None:
        """Whitespace-only user_id raises ValueError."""
        with pytest.raises(ValueError, match="user_id cannot be empty"):
            UserContext(user_id="   ")

    def test_invalid_uuid_format_raises_error(self) -> None:
        """Invalid UUID format raises ValueError."""
        with pytest.raises(ValueError, match="user_id must be a valid UUID"):
            UserContext(user_id="not-a-uuid")

    def test_partial_uuid_raises_error(self) -> None:
        """Incomplete UUID raises ValueError."""
        with pytest.raises(ValueError, match="user_id must be a valid UUID"):
            UserContext(user_id="550e8400-e29b-41d4")

    def test_uuid_with_wrong_length_raises_error(self) -> None:
        """UUID with wrong number of characters raises ValueError."""
        with pytest.raises(ValueError, match="user_id must be a valid UUID"):
            UserContext(user_id="550e8400-e29b-41d4-a716-44665544000")  # Missing one char


class TestUserContextWithFixtures:
    """Tests using pytest fixtures."""

    def test_fixture_creates_valid_context(self, user_context: UserContext) -> None:
        """Test that the user_context fixture creates a valid context."""
        assert user_context is not None
        assert user_context.user_id is not None

    def test_fixture_user_id_is_valid_uuid(self, valid_user_id: str) -> None:
        """Test that the valid_user_id fixture is a valid UUID."""
        # Should not raise
        context = UserContext(user_id=valid_user_id)
        assert context.user_id == valid_user_id

    def test_fixed_user_context_is_deterministic(self, fixed_user_context: UserContext) -> None:
        """Test that fixed_user_context has the expected fixed UUID."""
        assert fixed_user_context.user_id == "550e8400-e29b-41d4-a716-446655440000"
