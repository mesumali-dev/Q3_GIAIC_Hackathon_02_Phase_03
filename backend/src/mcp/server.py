"""MCP server initialization and configuration.

This module sets up the MCP server instance and provides database session
management for tool execution.
"""

import os
from contextlib import contextmanager
from typing import Generator

from mcp.server.fastmcp import FastMCP
from sqlmodel import Session

from src.database import engine

# ============================================================================
# Server Configuration
# ============================================================================

# Get configuration from environment variables
MCP_SERVER_NAME = os.getenv("MCP_SERVER_NAME", "todo-mcp-server")
MCP_SERVER_VERSION = os.getenv("MCP_SERVER_VERSION", "1.0.0")

# Initialize MCP server instance using FastMCP for decorator-based tool registration
server = FastMCP(MCP_SERVER_NAME)


# ============================================================================
# Database Session Management
# ============================================================================


@contextmanager
def get_db_session() -> Generator[Session, None, None]:
    """Create database session context manager for MCP tools.

    This context manager ensures each tool invocation gets a fresh
    database session that is automatically closed after use, maintaining
    stateless operation.

    Usage:
        with get_db_session() as db:
            task = create_task(db, user_id, data)

    Yields:
        Session: SQLModel database session

    Example:
        @server.tool()
        async def add_task(user_id: str, title: str) -> dict:
            with get_db_session() as db:
                task = create_task(db, UUID(user_id), data)
            return {"success": True, "task_id": str(task.id)}
    """
    with Session(engine) as session:
        yield session


# ============================================================================
# Server Entry Point
# ============================================================================


async def main() -> None:
    """Main entry point for MCP server.

    Starts the MCP server with all registered tools and stdio transport.
    The server remains stateless with all state persisted to the database.

    The server uses stdio transport for communication with MCP clients.
    """
    import structlog

    logger = structlog.get_logger(__name__)

    # Tool registrations
    # Phase 3: add_task tool (T019)
    from src.mcp.tools.add_task import add_task  # noqa: F401

    # Phase 4: list_tasks tool (T036)
    from src.mcp.tools.list_tasks import list_tasks  # noqa: F401

    # Phase 5: complete_task tool (T053)
    from src.mcp.tools.complete_task import complete_task  # noqa: F401

    # Phase 6: delete_task tool (T071)
    from src.mcp.tools.delete_task import delete_task  # noqa: F401

    # Phase 7: update_task tool (T088)
    from src.mcp.tools.update_task import update_task  # noqa: F401

    # Log server startup
    logger.info(
        "mcp_server_startup",
        server_name=MCP_SERVER_NAME,
        server_version=MCP_SERVER_VERSION,
        tools=["add_task", "list_tasks", "complete_task", "delete_task", "update_task"],
    )

    try:
        # Start server with stdio transport using FastMCP
        await server.run_stdio_async()
    except Exception as e:
        logger.error("mcp_server_error", error=str(e), error_type=type(e).__name__)
        raise
    finally:
        # Log server shutdown
        logger.info("mcp_server_shutdown", server_name=MCP_SERVER_NAME)


# ============================================================================
# Module Execution
# ============================================================================

if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
