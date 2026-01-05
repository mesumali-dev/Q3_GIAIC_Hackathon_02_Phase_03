"""
Database connection module for the backend application.

Provides SQLModel database connection, session management, and table creation.
Uses Neon PostgreSQL as the database backend.

@see data-model.md for schema specifications
"""

from typing import Generator

from sqlmodel import Session, SQLModel, create_engine

from src.config import get_settings

# Get database URL from settings
settings = get_settings()

# Create engine with connection pool settings suitable for serverless
engine = create_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,  # Log SQL queries in debug mode
    pool_pre_ping=True,  # Verify connections before use
)


def create_tables() -> None:
    """
    Create all database tables defined in SQLModel models.

    This function should be called on application startup to ensure
    all tables exist in the database.
    """
    # Import models to ensure they are registered with SQLModel
    from src.models.conversation import Conversation  # noqa: F401
    from src.models.message import Message  # noqa: F401
    from src.models.reminder import Reminder  # noqa: F401
    from src.models.task import Task  # noqa: F401
    from src.models.user import User  # noqa: F401

    SQLModel.metadata.create_all(engine)


def get_db() -> Generator[Session, None, None]:
    """
    Database session dependency for FastAPI routes.

    Yields a database session that is automatically closed after use.

    Usage:
        @app.get("/items")
        def get_items(db: Session = Depends(get_db)):
            return db.exec(select(Item)).all()

    Yields:
        Session: SQLModel database session
    """
    with Session(engine) as session:
        yield session


async def init_db() -> None:
    """
    Initialize database on application startup.

    Creates all tables if they don't exist.
    """
    create_tables()
    print("✅ Database tables created/verified")


async def close_db() -> None:
    """
    Close database connections on application shutdown.

    Disposes of the engine connection pool.
    """
    engine.dispose()
    print("✅ Database connections closed")
