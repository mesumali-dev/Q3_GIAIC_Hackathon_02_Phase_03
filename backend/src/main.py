"""
FastAPI application entry point for the AI-Native Todo Backend.

This module initializes the FastAPI application and registers routes.
Foundation phase includes only the health check endpoint.
"""

from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.config import get_settings
from src.database import init_db, close_db

# Get application settings
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Application lifespan manager.

    Handles startup and shutdown events.
    """
    # Startup
    await init_db()
    print(f"🚀 Backend server starting on {settings.HOST}:{settings.PORT}")

    # Validate configuration
    missing = settings.validate()
    if missing:
        print(f"⚠️  Warning: Missing environment variables: {', '.join(missing)}")

    yield

    # Shutdown
    await close_db()
    print("👋 Backend server shutting down")


# Create FastAPI application instance
app = FastAPI(
    title="AI-Native Todo API",
    description="Backend API for the AI-Native Todo Full-Stack Web Application",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Configure CORS for frontend communication
# Uses FRONTEND_URL from environment for production flexibility
cors_origins = [
    settings.FRONTEND_URL,
    "http://localhost:3000",  # Next.js development server fallback
    "http://127.0.0.1:3000",
]
# Remove duplicates while preserving order
cors_origins = list(dict.fromkeys(cors_origins))

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["Authorization", "Content-Type", "*"],  # Explicit Authorization header
)


@app.get("/health")
async def health_check():
    """
    Health check endpoint.

    Returns the current health status of the backend service.
    This endpoint is unauthenticated and used for monitoring.

    Returns:
        dict: Health status with timestamp
    """
    return {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "service": "todo-backend",
        "version": "0.1.0"
    }


@app.get("/")
async def root():
    """
    Root endpoint.

    Provides basic API information and links to documentation.
    """
    return {
        "message": "AI-Native Todo API",
        "version": "0.1.0",
        "docs": "/docs",
        "health": "/health"
    }


# Register auth routes
from src.api.auth import router as auth_router
app.include_router(auth_router)

# Register task routes
from src.api.tasks import router as tasks_router
app.include_router(tasks_router)

# Register reminder routes
from src.api.reminders import router as reminders_router
app.include_router(reminders_router)

# Register conversation routes
from src.api.conversations import router as conversations_router
app.include_router(conversations_router)
