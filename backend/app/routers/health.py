"""
Health check endpoints for monitoring and orchestration.

Provides status information about the API and its dependencies.
"""

from fastapi import APIRouter
from app.config import get_settings
from app.schemas import HealthResponse
from app.database import check_db_connection
import redis

router = APIRouter(prefix="/api/v1", tags=["health"])
settings = get_settings()


def check_redis_connection() -> bool:
    """Check Redis connection (sync)."""
    try:
        r = redis.from_url(settings.redis_url)
        r.ping()
        return True
    except Exception:
        return False


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint for monitoring.
    
    Returns status of API and all dependencies.
    Used by Kubernetes readiness probes and load balancers.
    """
    return HealthResponse(
        status="healthy",
        version=settings.app_version,
        environment=settings.environment,
        database=await check_db_connection(),
        redis=check_redis_connection(),
        celery=check_redis_connection(),
    )


@router.get("/ready")
async def readiness_check():
    """
    Readiness check for Kubernetes orchestrators.
    
    Returns 200 only if API is ready to accept traffic.
    """
    db_ok = await check_db_connection()
    redis_ok = check_redis_connection()
    
    if db_ok and redis_ok:
        return {"status": "ready"}
    else:
        return {"status": "not_ready"}, 503


@router.get("/live")
async def liveness_check():
    """
    Liveness check for Kubernetes orchestrators.
    
    Returns 200 if API process is alive and responsive.
    """
    return {"status": "alive"}
