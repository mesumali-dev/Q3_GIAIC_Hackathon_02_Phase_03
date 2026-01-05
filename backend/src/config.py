"""
Configuration module for the backend application.

Loads environment variables and provides application configuration.
All sensitive values MUST be loaded from environment variables.
"""

import os
from functools import lru_cache
from dotenv import load_dotenv

# Load .env file if it exists
load_dotenv()


class Settings:
    """Application settings loaded from environment variables."""

    # Server Configuration
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"

    # Database Configuration (placeholder - not connected in foundation phase)
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql://user:password@localhost:5432/todo_db"
    )

    # Authentication Configuration
    # CRITICAL: This secret MUST match the frontend's BETTER_AUTH_SECRET
    BETTER_AUTH_SECRET: str = os.getenv("BETTER_AUTH_SECRET", "")

    # JWT Configuration
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRY_HOURS: int = int(os.getenv("JWT_EXPIRY_HOURS", "24"))

    # CORS Configuration
    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "http://localhost:3000")

    def validate(self) -> list[str]:
        """
        Validate that required environment variables are set.
        Returns a list of missing required variables.
        """
        missing = []

        # In production, these should be required
        if not self.BETTER_AUTH_SECRET:
            missing.append("BETTER_AUTH_SECRET")

        return missing


@lru_cache
def get_settings() -> Settings:
    """
    Get cached settings instance.
    Uses lru_cache to ensure settings are loaded only once.
    """
    return Settings()
