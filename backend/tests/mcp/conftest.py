"""Pytest configuration for MCP tests.

This module configures the test environment to use an in-memory SQLite database
instead of the production PostgreSQL database, ensuring test isolation.
"""

import pytest
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool


@pytest.fixture(scope="function", autouse=True)
def setup_test_database(monkeypatch):
    """Configure MCP tools to use in-memory test database.

    This fixture automatically applies to all tests in the mcp/ directory.
    It monkeypatches the database engine and get_db_session to use SQLite
    instead of the production PostgreSQL database.
    """
    # Create in-memory SQLite engine for tests
    test_engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    # Create all tables in the test database
    SQLModel.metadata.create_all(test_engine)

    # Monkeypatch the database module to use test engine
    import src.database
    monkeypatch.setattr(src.database, "engine", test_engine)

    # Monkeypatch the MCP server module to use test engine
    import src.mcp.server

    # Create a new get_db_session that uses the test engine
    from contextlib import contextmanager
    from typing import Generator

    @contextmanager
    def test_get_db_session() -> Generator[Session, None, None]:
        """Test version of get_db_session using in-memory database."""
        with Session(test_engine) as session:
            yield session

    monkeypatch.setattr(src.mcp.server, "get_db_session", test_get_db_session)
    monkeypatch.setattr(src.mcp.server, "engine", test_engine)

    yield test_engine

    # Cleanup after test
    SQLModel.metadata.drop_all(test_engine)
    test_engine.dispose()


@pytest.fixture
def anyio_backend():
    """Configure anyio to use asyncio backend for async tests."""
    return "asyncio"
