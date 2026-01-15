"""User context for agent execution.

Provides the UserContext dataclass that carries authenticated user information
through the agent execution pipeline. The context is passed to all function
tools via RunContextWrapper[UserContext].
"""

from dataclasses import dataclass
from uuid import UUID


@dataclass
class UserContext:
    """Context for agent execution containing authenticated user info.

    This context is created once per agent invocation from the authenticated
    JWT claims. It is passed to the agent runner and made available to all
    function tools via RunContextWrapper[UserContext].

    Attributes:
        user_id: UUID string identifying the authenticated user. Must be a
            valid UUID v4 format string.

    Example:
        >>> context = UserContext(user_id="550e8400-e29b-41d4-a716-446655440000")
        >>> result = Runner.run_sync(agent, "Show my tasks", context=context)
    """

    user_id: str

    def __post_init__(self) -> None:
        """Validate user_id is a valid UUID string after initialization."""
        if not self.user_id or not self.user_id.strip():
            raise ValueError("user_id cannot be empty")

        # Validate UUID format by attempting to parse it
        try:
            UUID(self.user_id)
        except ValueError as e:
            raise ValueError(f"user_id must be a valid UUID: {e}") from e
