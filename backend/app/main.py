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
import asyncio
import logging
import os
import uuid
import time

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from prometheus_fastapi_instrumentator import Instrumentator

from app.config import get_settings, get_allowed_origins
from app.logging_config import setup_logging
from app.database import init_db, close_db, check_db_connection
# Import only essential routers for TUI
from app.routers import (
    health, users, tenants, dashboard, analytics, ai, auth, 
    backup, failsafe, incidents, gamma, cortex, metrics_summary, 
    websocket, truthsync, ai_tools
)
# Commented out routers with missing dependencies:
# from app.routers import quantum, terminal, infrastructure
from app.api import workflows
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
    # Initialize database (create tables, extensions)
    # This is async and uses asyncpg driver
    try:
        await init_db()
        logger.info("✅ Database initialized (using asyncpg driver)")
    except Exception as e:
        logger.error(f"❌ Database Initialization Failed: {e}")
    
    # Verify database connectivity
    # Verify database connectivity
    db_status = await check_db_connection()
    if db_status.get("db_connection", False):
        logger.info(f"✅ Database connection verified")
    else:
        logger.error(f"❌ Database connection failed: {db_status.get('error', 'Unknown error')}")
    
    # Setup graceful shutdown handlers
    setup_signal_handlers(app)
    logger.info("✅ Graceful shutdown handlers configured")
    
    # --- QUANTUM HEARTBEAT START ---
    # Start the biological pulse listener in background
    from app.routers.health import quantum_pulse_listener
    asyncio.create_task(quantum_pulse_listener())
    logger.info("💓 Quantum Heartbeat Listener STARTED")
    # -------------------------------
    
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
    Middleware para loguear todas las peticiones HTTP con trazabilidad.
    """
    start_time = time.time()
    
    # Intentar obtener el ID (será 'unknown' si este middleware es el más externo en la fase de petición)
    correlation_id = getattr(request.state, "correlation_id", "unknown")
    
    try:
        response = await call_next(request)
        process_time = (time.time() - start_time) * 1000
        
        # Refrescar el correlation_id después de que otros middlewares lo hayan podido establecer
        correlation_id = getattr(request.state, "correlation_id", correlation_id)
        extra = {"correlation_id": correlation_id}
        
        logger.info(
            f"📥 {request.method} {request.url.path} - "
            f"Status: {response.status_code} - "
            f"Time: {process_time:.2f}ms",
            extra=extra
        )
        return response
    except Exception as e:
        process_time = (time.time() - start_time) * 1000
        correlation_id = getattr(request.state, "correlation_id", correlation_id)
        extra = {"correlation_id": correlation_id}
        
        logger.error(
            f"❌ Error: {request.method} {request.url.path} - "
            f"Error: {str(e)} - "
            f"Time: {process_time:.2f}ms",
            extra=extra,
            exc_info=True
        )
        raise


@app.middleware("http")
async def add_correlation_id(request: Request, call_next):
    """
    Middleware que añade un ID de correlación único a cada petición.
    Al estar definido DESPUÉS de log_requests, será el MÁS EXTERNO en la fase de petición.
    """
    correlation_id = request.headers.get("X-Correlation-ID", str(uuid.uuid4()))
    request.state.correlation_id = correlation_id
    
    response = await call_next(request)
    response.headers["X-Correlation-ID"] = correlation_id
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
app.include_router(analytics.router, tags=["analytics"])
app.include_router(ai.router, tags=["ai"])
app.include_router(auth.router, tags=["auth"])
app.include_router(users.router, tags=["users"])
app.include_router(tenants.router, tags=["tenants"])
app.include_router(dashboard.router, tags=["dashboard"])
app.include_router(cortex.router)  # Cortex Decision Engine
app.include_router(incidents.router)  # Incident Management (ITIL)
app.include_router(backup.router)  # Backup API
app.include_router(failsafe.router)  # Fail-Safe Security Layer
app.include_router(workflows.router)  # Workflow Recommendations
app.include_router(gamma.router)  # Guardian Gamma (HITL)
app.include_router(metrics_summary.router)  # Metrics Summary for GUI
app.include_router(websocket.router)  # Real-time Battlefield UI
app.include_router(truthsync.router)  # Truth verification service
app.include_router(ai_tools.router)  # AI Autonomous Tools (File/Command access)
# Commented out routers with missing dependencies:
# app.include_router(quantum.router)  # Quantum membrane visualization
# app.include_router(terminal.router)  # Secure Terminal Service
# app.include_router(infrastructure.router)  # Sovereign Matrix (Docker, Network, Logs)



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
