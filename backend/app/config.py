"""
Configuration module for Sentinel application.

This module manages all application settings loaded from environment variables.
It provides a centralized place for configuration management with sensible defaults.

Environment Variables:
    - DATABASE_URL: PostgreSQL connection string
    - REDIS_URL: Redis connection string
    - SECRET_KEY: JWT signing key (change in production!)
    - FASTAPI_ENV: Environment (development/production)
    - LOG_LEVEL: Logging level (DEBUG/INFO/WARNING/ERROR)
    - ALLOWED_ORIGINS: CORS allowed origins (comma-separated)
"""

from pydantic_settings import BaseSettings
import os
from typing import List


class Settings(BaseSettings):
    """
    Application configuration loaded from environment variables.
    
    All settings have sensible defaults for development. In production,
    ensure critical values like SECRET_KEY are properly set via environment.
    """
    
    # ============================================================================
    # DATABASE CONFIGURATION
    # ============================================================================
    database_url: str = os.getenv(
        "DATABASE_URL", 
        "postgresql+asyncpg://sentinel_user:sentinel_password@localhost:5432/sentinel_db"
    )
    """PostgreSQL connection string for the application database."""
    
    # ============================================================================
    # CACHE CONFIGURATION
    # ============================================================================
    redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    """Redis connection string for caching and session management."""
    
    # ============================================================================
    # APPLICATION METADATA
    # ============================================================================
    app_name: str = os.getenv("APP_NAME", "Sentinel")
    """Application name displayed in API documentation."""
    
    app_version: str = os.getenv("APP_VERSION", "1.0.0")
    """Application version for API versioning and documentation."""
    
    environment: str = os.getenv("FASTAPI_ENV", "development")
    """Deployment environment (development/production)."""
    
    debug: bool = environment == "development"
    """Enable debug mode in development environment."""
    
    # ============================================================================
    # SECURITY CONFIGURATION
    # ============================================================================
    secret_key: str = os.getenv(
        "SECRET_KEY", 
        "your-secret-key-change-in-production-min-32-chars-xyz123"
    )
    """
    JWT signing key for token generation.
    
    WARNING: Change this in production to a secure random string!
    Use: openssl rand -hex 32
    """
    
    algorithm: str = os.getenv("ALGORITHM", "HS256")
    """JWT algorithm for token signing."""
    
    access_token_expire_minutes: int = int(
        os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30")
    )
    """JWT access token expiration time in minutes."""
    
    refresh_token_expire_days: int = int(
        os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7")
    )
    """Refresh token expiration time in days."""
    
    # ============================================================================
    # ASYNC TASK CONFIGURATION (CELERY)
    # ============================================================================
    celery_broker_url: str = os.getenv(
        "CELERY_BROKER_URL", 
        "redis://localhost:6379/0"
    )
    """Redis URL for Celery message broker."""
    
    celery_result_backend: str = os.getenv(
        "CELERY_RESULT_BACKEND", 
        "redis://localhost:6379/1"
    )
    """Redis URL for storing Celery task results."""
    
    # ============================================================================
    # LOGGING CONFIGURATION
    # ============================================================================
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    """Logging level (DEBUG/INFO/WARNING/ERROR/CRITICAL)."""
    
    class Config:
        """Pydantic configuration for Settings."""
        env_file = ".env"
        case_sensitive = False


# Global settings instance (singleton pattern)
_settings: Settings | None = None


def get_settings() -> Settings:
    """
    Get or create the global settings instance.
    
    Uses singleton pattern to ensure settings are loaded only once
    at application startup. Subsequent calls return the cached instance.
    
    Returns:
        Settings: Application settings instance
        
    Example:
        >>> settings = get_settings()
        >>> db_url = settings.database_url
    """
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings


def get_allowed_origins() -> List[str]:
    """
    Parse CORS allowed origins from environment variable.
    
    The ALLOWED_ORIGINS environment variable should be a comma-separated
    string of URLs. This function parses it into a list suitable for
    FastAPI's CORSMiddleware.
    
    Returns:
        List[str]: List of allowed CORS origins
        
    Example:
        Environment: ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8000
        Returns: ["http://localhost:3000", "http://localhost:8000"]
    """
    origins_str = os.getenv(
        "ALLOWED_ORIGINS",
        "http://localhost:3000,http://localhost:8000,http://frontend:3000"
    )
    # Strip whitespace from each origin for robustness
    return [origin.strip() for origin in origins_str.split(",")]
