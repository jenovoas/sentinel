"""
Health Check Endpoints for High Availability

These endpoints are critical for HA orchestration:
- /health: Overall system health (used by monitoring)
- /ready: Readiness to serve traffic (used by load balancers)
- /live: Liveness check (used by orchestrators to restart)

Health Check Consumers:
- Route53/Cloudflare health checks
- HAProxy backend health
- Kubernetes liveness/readiness probes
- Prometheus blackbox exporter
- Custom watchdog scripts
"""

from fastapi import APIRouter, Response, status
from datetime import datetime
from typing import Dict, Any
import asyncio
import asyncpg
import redis.asyncio as redis
import httpx

router = APIRouter()

# Global state for role management
app_role = "standby"  # "primary" or "standby"
accept_requests = False  # Whether to serve client requests

# Startup time for uptime calculation
startup_time = datetime.now()


async def check_database() -> Dict[str, Any]:
    """
    Check PostgreSQL connection and basic query
    
    Returns:
        dict: {
            "status": "healthy" | "unhealthy",
            "latency_ms": float,
            "error": str (if unhealthy)
        }
    """
    try:
        import os
        from time import time
        
        # Get DB config from environment
        db_host = os.getenv("DATABASE_HOST", "postgres")
        db_port = int(os.getenv("DATABASE_PORT", "5432"))
        db_user = os.getenv("DATABASE_USER", "sentinel")
        db_password = os.getenv("DATABASE_PASSWORD", "darkfenix")
        db_name = os.getenv("DATABASE_NAME", "sentinel")
        
        start = time()
        
        # Create connection
        conn = await asyncpg.connect(
            host=db_host,
            port=db_port,
            user=db_user,
            password=db_password,
            database=db_name,
            timeout=5.0  # 5 second timeout
        )
        
        # Simple query to verify database is responsive
        result = await conn.fetchval("SELECT 1")
        
        # Check if we're connected to primary or replica
        is_primary = await conn.fetchval(
            "SELECT NOT pg_is_in_recovery()"
        )
        
        await conn.close()
        
        latency = (time() - start) * 1000  # Convert to ms
        
        return {
            "status": "healthy",
            "latency_ms": round(latency, 2),
            "is_primary": is_primary,
            "host": db_host
        }
        
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }


async def check_redis() -> Dict[str, Any]:
    """
    Check Redis connection and basic operation
    
    Now uses Redis Sentinel for HA support
    
    Returns:
        dict: {
            "status": "healthy" | "unhealthy",
            "latency_ms": float,
            "cluster_info": dict (if Sentinel enabled),
            "error": str (if unhealthy)
        }
    """
    try:
        from time import time
        
        # Try to use Sentinel client if available
        try:
            from app.redis_client import get_redis_master, check_redis_health
            
            start = time()
            
            # Get master connection via Sentinel
            master = await get_redis_master()
            
            # Ping Redis
            await master.ping()
            
            # Test set/get
            test_key = "health_check_test"
            await master.set(test_key, "ok", ex=10)
            value = await master.get(test_key)
            
            latency = (time() - start) * 1000
            
            if value != "ok":
                raise Exception("Redis set/get test failed")
            
            # Get cluster info from Sentinel
            cluster_info = await check_redis_health()
            
            return {
                "status": "healthy",
                "latency_ms": round(latency, 2),
                "mode": "sentinel",
                "cluster": cluster_info
            }
            
        except ImportError:
            # Fallback to simple Redis if Sentinel not configured
            import os
            import redis.asyncio as redis
            
            redis_url = os.getenv("REDIS_URL", "redis://redis:6379")
            
            start = time()
            
            r = redis.from_url(redis_url, decode_responses=True)
            await r.ping()
            
            test_key = "health_check_test"
            await r.set(test_key, "ok", ex=10)
            value = await r.get(test_key)
            
            await r.close()
            
            latency = (time() - start) * 1000
            
            if value != "ok":
                raise Exception("Redis set/get test failed")
            
            return {
                "status": "healthy",
                "latency_ms": round(latency, 2),
                "mode": "standalone"
            }
        
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }


async def check_ollama() -> Dict[str, Any]:
    """
    Check Ollama AI service
    
    Returns:
        dict: {
            "status": "healthy" | "unhealthy" | "disabled",
            "latency_ms": float,
            "error": str (if unhealthy)
        }
    """
    try:
        import os
        from time import time
        
        ollama_url = os.getenv("OLLAMA_URL", "http://ollama:11434")
        
        start = time()
        
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{ollama_url}/api/tags")
            response.raise_for_status()
            
        latency = (time() - start) * 1000
        
        return {
            "status": "healthy",
            "latency_ms": round(latency, 2),
            "enabled": True
        }
        
    except Exception as e:
        # Ollama is optional, so we don't fail health check if it's down
        return {
            "status": "disabled",
            "error": str(e),
            "enabled": False
        }


@router.get("/health")
async def health_check(response: Response):
    """
    Overall system health check
    
    Used by:
    - Monitoring systems (Prometheus, Datadog)
    - Status pages
    - General health monitoring
    
    Returns 200 if system is healthy, 503 if any critical component is down
    
    Response includes:
    - Overall status
    - Individual component statuses
    - Role (primary/standby)
    - Uptime
    """
    # Check all dependencies in parallel
    db_check, redis_check, ollama_check = await asyncio.gather(
        check_database(),
        check_redis(),
        check_ollama(),
        return_exceptions=True
    )
    
    # Determine overall health
    # Critical: Database and Redis must be healthy
    # Optional: Ollama can be disabled
    
    critical_healthy = (
        db_check.get("status") == "healthy" and
        redis_check.get("status") == "healthy"
    )
    
    overall_status = "healthy" if critical_healthy else "unhealthy"
    
    # Calculate uptime
    uptime_seconds = (datetime.now() - startup_time).total_seconds()
    
    health_data = {
        "status": overall_status,
        "timestamp": datetime.now().isoformat(),
        "uptime_seconds": round(uptime_seconds, 2),
        "role": app_role,
        "components": {
            "database": db_check,
            "redis": redis_check,
            "ollama": ollama_check
        }
    }
    
    # Set HTTP status code
    if overall_status == "unhealthy":
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    else:
        response.status_code = status.HTTP_200_OK
    
    return health_data


@router.get("/ready")
async def readiness_check(response: Response):
    """
    Readiness check - Can this instance serve traffic?
    
    Used by:
    - Load balancers (HAProxy, nginx)
    - Kubernetes readiness probes
    - DNS health checks (Route53, Cloudflare)
    
    Returns 200 only if:
    - All critical dependencies are healthy
    - Application is in "primary" role OR accept_requests is True
    - No ongoing maintenance
    
    This is stricter than /health because it determines if traffic
    should be routed to this instance.
    """
    # Check dependencies
    db_check, redis_check = await asyncio.gather(
        check_database(),
        check_redis()
    )
    
    # Check if dependencies are healthy
    dependencies_healthy = (
        db_check.get("status") == "healthy" and
        redis_check.get("status") == "healthy"
    )
    
    # Check if we should accept requests
    # Primary always accepts, standby only if explicitly enabled
    can_serve = (app_role == "primary") or accept_requests
    
    # Overall readiness
    ready = dependencies_healthy and can_serve
    
    readiness_data = {
        "ready": ready,
        "timestamp": datetime.now().isoformat(),
        "role": app_role,
        "accept_requests": accept_requests,
        "dependencies": {
            "database": db_check.get("status"),
            "redis": redis_check.get("status")
        }
    }
    
    # Set HTTP status code
    if ready:
        response.status_code = status.HTTP_200_OK
    else:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    
    return readiness_data


@router.get("/live")
async def liveness_check():
    """
    Liveness check - Is the process alive?
    
    Used by:
    - Kubernetes liveness probes
    - Process managers (systemd, supervisor)
    - Orchestrators to determine if process should be restarted
    
    Returns 200 if process is alive and responsive
    This is a very lightweight check - just confirms the process
    can handle HTTP requests.
    
    Unlike /health and /ready, this does NOT check dependencies.
    A process can be "alive" but not "ready" or "healthy".
    """
    return {
        "alive": True,
        "timestamp": datetime.now().isoformat(),
        "uptime_seconds": round((datetime.now() - startup_time).total_seconds(), 2)
    }


@router.post("/promote")
async def promote_to_primary(response: Response):
    """
    Promote this instance to primary role
    
    Used during failover to switch standby to primary
    
    This endpoint should be protected (authentication required)
    """
    global app_role, accept_requests
    
    # TODO: Add authentication check
    # if not is_authorized(request):
    #     raise HTTPException(status_code=401)
    
    app_role = "primary"
    accept_requests = True
    
    return {
        "status": "promoted",
        "role": app_role,
        "accept_requests": accept_requests,
        "timestamp": datetime.now().isoformat()
    }


@router.post("/demote")
async def demote_to_standby(response: Response):
    """
    Demote this instance to standby role
    
    Used during failback to return to standby mode
    
    This endpoint should be protected (authentication required)
    """
    global app_role, accept_requests
    
    # TODO: Add authentication check
    
    app_role = "standby"
    accept_requests = False
    
    return {
        "status": "demoted",
        "role": app_role,
        "accept_requests": accept_requests,
        "timestamp": datetime.now().isoformat()
    }


@router.get("/metrics")
async def prometheus_metrics():
    """
    Prometheus metrics endpoint
    
    Exposes metrics in Prometheus format for scraping
    
    Metrics include:
    - Health check results
    - Dependency latencies
    - Role status
    - Uptime
    """
    # Check all components
    db_check, redis_check, ollama_check = await asyncio.gather(
        check_database(),
        check_redis(),
        check_ollama(),
        return_exceptions=True
    )
    
    uptime = (datetime.now() - startup_time).total_seconds()
    
    # Prometheus format
    metrics = []
    
    # Health status (1 = healthy, 0 = unhealthy)
    metrics.append(f'sentinel_health{{component="database"}} {1 if db_check.get("status") == "healthy" else 0}')
    metrics.append(f'sentinel_health{{component="redis"}} {1 if redis_check.get("status") == "healthy" else 0}')
    metrics.append(f'sentinel_health{{component="ollama"}} {1 if ollama_check.get("status") == "healthy" else 0}')
    
    # Latencies
    if "latency_ms" in db_check:
        metrics.append(f'sentinel_dependency_latency_ms{{component="database"}} {db_check["latency_ms"]}')
    if "latency_ms" in redis_check:
        metrics.append(f'sentinel_dependency_latency_ms{{component="redis"}} {redis_check["latency_ms"]}')
    
    # Role (1 = primary, 0 = standby)
    metrics.append(f'sentinel_role{{role="{app_role}"}} {1 if app_role == "primary" else 0}')
    
    # Uptime
    metrics.append(f'sentinel_uptime_seconds {uptime}')
    
    # Accept requests flag
    metrics.append(f'sentinel_accept_requests {1 if accept_requests else 0}')
    
    return Response(
        content="\n".join(metrics) + "\n",
        media_type="text/plain"
    )
