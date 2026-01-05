"""Error handling for MCP tools.

Defines custom exception types and error response formatting
for consistent, AI-friendly error communication.
"""

from typing import Any


# ============================================================================
# Exception Classes
# ============================================================================


class MCPToolError(Exception):
    """Base class for MCP tool errors.

    All MCP-specific errors inherit from this base class to enable
    consistent error handling across all tools.
    """

    error_code: str = "UNKNOWN_ERROR"
    user_message: str = "An unknown error occurred"

    def __init__(self, message: str | None = None):
        """Initialize MCP tool error.

        Args:
            message: Optional custom error message (defaults to user_message)
        """
        self.message = message or self.user_message
        super().__init__(self.message)


class TaskNotFoundError(MCPToolError):
    """Raised when a requested task does not exist or user lacks access.

    This error intentionally combines "not found" and "access denied"
    to avoid leaking information about whether tasks exist for other users.
    """

    error_code = "TASK_NOT_FOUND"
    user_message = "Task not found or access denied"


class ValidationError(MCPToolError):
    """Raised when input parameters fail validation.

    Examples:
    - Invalid UUID format
    - Empty or too-long title
    - Missing required fields
    - Constraint violations
    """

    error_code = "VALIDATION_ERROR"
    user_message = "Invalid input parameters"


class AuthorizationError(MCPToolError):
    """Raised when user is not authorized for the requested operation.

    This error is used when:
    - User attempts to access another user's task
    - User lacks permissions for the operation
    """

    error_code = "AUTHORIZATION_ERROR"
    user_message = "User not authorized for this operation"


class DatabaseError(MCPToolError):
    """Raised when database operations fail.

    Examples:
    - Connection failures
    - Query timeouts
    - Transaction rollbacks
    - Constraint violations at database level
    """

    error_code = "DATABASE_ERROR"
    user_message = "Database operation failed"


# ============================================================================
# Error Response Handler
# ============================================================================


def handle_tool_error(exception: Exception) -> dict[str, Any]:
    """Convert exceptions to structured MCP error responses.

    This function ensures all errors returned to AI agents follow
    a consistent format with appropriate error codes and safe messages.

    Args:
        exception: Exception to convert to error response

    Returns:
        dict with success=False and error details suitable for AI consumption

    Examples:
        >>> handle_tool_error(TaskNotFoundError())
        {'success': False, 'error': {'code': 'TASK_NOT_FOUND', 'message': '...'}}

        >>> handle_tool_error(ValidationError("Empty title"))
        {'success': False, 'error': {'code': 'VALIDATION_ERROR', 'message': 'Empty title'}}
    """
    # Handle known MCP tool errors
    if isinstance(exception, MCPToolError):
        return {
            "success": False,
            "error": {
                "code": exception.error_code,
                "message": exception.message,
            },
        }

    # Handle Pydantic validation errors
    if exception.__class__.__name__ == "ValidationError":
        # Extract user-friendly error message from Pydantic validation error
        try:
            import re
            error_str = str(exception)
            # Look for the specific error message after "Value error,"
            match = re.search(r'Value error, ([^\n\[]+)', error_str)
            if match:
                error_msg = match.group(1).strip()
            else:
                # Fallback to first line if pattern not found
                error_msg = error_str.split("\n")[0]
        except Exception:
            error_msg = "Invalid input parameters"

        return {
            "success": False,
            "error": {
                "code": "VALIDATION_ERROR",
                "message": error_msg,
            },
        }

    # Handle database-related exceptions
    if "database" in exception.__class__.__name__.lower() or "sql" in exception.__class__.__name__.lower():
        return {
            "success": False,
            "error": {
                "code": "DATABASE_ERROR",
                "message": "Database operation failed",
            },
        }

    # Handle all other exceptions as unknown errors
    # Don't leak internal details to AI agents
    return {
        "success": False,
        "error": {
            "code": "UNKNOWN_ERROR",
            "message": "An unexpected error occurred",
        },
    }
