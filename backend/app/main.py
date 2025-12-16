"""
Sentinel API - Main FastAPI Application.

Async-first REST API for multi-tenant SaaS platform. Built with FastAPI 0.104
and SQLAlchemy 2.0 async support for high-performance request handling.

Features:
    - CORS for cross-origin requests
    - Structured logging for monitoring
    - Health checks for orchestration
    - Multi-tenant support via RLS
    - Async request handling with proper error handling
    - Automatic database connection management

Performance:
    - asyncpg driver: 3-5x faster than psycopg2
    - Non-blocking I/O: Handle 1000+ concurrent users
    - Connection pooling: Docker-ready with NullPool
    - Health checks: Kubernetes-ready readiness probes

Start with: uvicorn app.main:app --host 0.0.0.0 --port 8000
"""

from contextlib import asynccontextmanager
import logging
import os

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from prometheus_fastapi_instrumentator import Instrumentator

from app.config import get_settings, get_allowed_origins
from app.logging_config import setup_logging
from app.database import init_db, close_db, check_db_connection
from app.routers import health, users, tenants, dashboard, analytics, ai, auth, backup, failsafe
from app.shutdown import setup_signal_handlers  # Graceful shutdown

settings = get_settings()
logger = setup_logging(settings.log_level)


# ============================================================================
# APPLICATION LIFESPAN
# ============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan context manager.
    
    Handles startup and shutdown events for the application:
    - Startup: Initialize database, create tables, verify connections
    - Shutdown: Clean up resources gracefully
    
    This replaces the deprecated @app.on_event decorators.
    Called automatically by FastAPI.
    """
    # ========================================================================
    # STARTUP - Runs once when the application starts
    # ========================================================================
    logger.info("🚀 Starting Sentinel API...")
    
    # Create logs directory
    os.makedirs("logs", exist_ok=True)
    
    # Initialize database (create tables, extensions)
    # This is async and uses asyncpg driver
    await init_db()
    logger.info("✅ Database initialized (using asyncpg driver)")
    
    # Verify database connectivity
    db_status = await check_db_connection()
    if db_status.get("db_connection", False):
        logger.info(f"✅ Database connection verified")
    else:
        logger.error(f"❌ Database connection failed: {db_status.get('error', 'Unknown error')}")
    
    # Setup graceful shutdown handlers
    setup_signal_handlers(app)
    logger.info("✅ Graceful shutdown handlers configured")
    
    yield  # Application runs here
    
    # ========================================================================
    # SHUTDOWN - Runs once when the application stops
    # ========================================================================
    logger.info("👋 Shutting down Sentinel API...")
    
    # Close all database connections
    # Important for clean shutdown and preventing connection leaks
    await close_db()


# ============================================================================
# FASTAPI APPLICATION INITIALIZATION
# ============================================================================

app = FastAPI(
    title=settings.app_name,
    description="Multi-tenant SaaS platform with async-first architecture",
    version=settings.app_version,
    lifespan=lifespan,
)

# ============================================================================
# PROMETHEUS INSTRUMENTATION
# ============================================================================
# Add Prometheus metrics collection
Instrumentator().instrument(app).expose(
    app,
    endpoint="/metrics",  # Expose metrics at /metrics
    include_in_schema=False,  # Hide from OpenAPI docs
)

# ============================================================================
# MIDDLEWARE CONFIGURATION
# ============================================================================
"""
Middleware order matters! They execute in the order added.
"""

# CORS Middleware - Handle cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=get_allowed_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    """
    Middleware to log all HTTP requests.
    
    Logs HTTP method, path, and response status code.
    Useful for debugging and monitoring API usage.
    """
    logger.info(f"{request.method} {request.url.path}")
    response = await call_next(request)
    return response


# ============================================================================
# EXCEPTION HANDLERS
# ============================================================================

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """
    Global exception handler for unhandled exceptions.
    
    Catches any exception not caught by more specific handlers and returns
    a safe error response without leaking internal details.
    
    Args:
        request: The HTTP request that caused the error
        exc: The exception that was raised
        
    Returns:
        JSONResponse with 500 status code
    """
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )


# ============================================================================
# ROUTE INCLUSION
# ============================================================================
"""
Include routers from separate modules for better organization.
Each router handles a specific domain of functionality.
"""

# Health endpoints (no prefix - top level)
app.include_router(health.router, tags=["health"])

# API endpoints
app.include_router(analytics.router, prefix="/api/v1/analytics", tags=["analytics"])
app.include_router(ai.router, prefix="/api/v1/ai", tags=["ai"])
app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(users.router, prefix="/api/v1/users", tags=["users"])
app.include_router(tenants.router, prefix="/api/v1/tenants", tags=["tenants"])
app.include_router(dashboard.router, prefix="/api/v1/dashboard", tags=["dashboard"])
app.include_router(backup.router)  # Backup API (prefix defined in router)
app.include_router(failsafe.router)  # Fail-Safe Security Layer


# ============================================================================
# ROOT ENDPOINTS
# ============================================================================

@app.get("/")
async def root():
    """
    Root endpoint for API information.
    
    Returns basic information about the API and links to documentation.
    Useful for health checks and verifying the API is running.
    
    Returns:
        dict: API information including version and docs link
    """
    return {
        "message": "Welcome to Sentinel API",
        "version": settings.app_version,
        "docs": "/docs",
        "async_driver": "asyncpg",
    }


# ============================================================================
# ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    """
    Entry point for running the application directly.
    
    Not recommended for production. Use:
        uvicorn app.main:app --host 0.0.0.0 --port 8000
    """
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level=settings.log_level.lower(),
    )
