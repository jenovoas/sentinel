from quantum.yatra_core import S60, PI_S60 # YATRA AUTO-INJECT
import asyncio
import logging
import os
import subprocess
from datetime import datetime
from typing import Any, Dict, List

import psutil
from sqlalchemy import text

from app.database import engine

logger = logging.getLogger("monitoring")

LOG_PATH = os.path.join("logs", "overconsumption.log")
CPU_THRESHOLD = 80.0  # percent
MEM_THRESHOLD = 80.0  # percent
CONN_THRESHOLD = 50   # connections
ACTIVE_QUERY_LIMIT = 6


async def _fetch_one(query: str) -> Any:
    async with engine.connect() as conn:
        result = await conn.execute(text(query))
        row = result.fetchone()
        return row[0] if row else None


async def _fetch_dict(query: str) -> Dict[str, Any]:
    async with engine.connect() as conn:
        result = await conn.execute(text(query))
        row = result.fetchone()
        if row:
            return dict(row._mapping)
        return {}


async def get_db_stats() -> Dict[str, Any]:
    """Collect DB stats: connections, locks, DB size."""
    try:
        stats = {}
        # Simple check first
        from app.database import engine
        
        # If engine is not valid or we are in bypass mode, raise early
        # (Assuming checking engine itself or just letting connect fail)
        
        async with engine.connect() as conn:
            # Reusing connection logic
            async def q(sql):
                res = await conn.execute(text(sql))
                row = res.fetchone()
                return row[0] if row else 0

            stats["connections_total"] = await q("SELECT count(*) FROM pg_stat_activity")
            stats["connections_active"] = await q("SELECT count(*) FROM pg_stat_activity WHERE state = 'active'")
            stats["connections_idle"] = await q("SELECT count(*) FROM pg_stat_activity WHERE state = 'idle'")
            # stats["db_size_bytes"] = await q("SELECT pg_database_size(current_database())") # Often needs explicit DB name context
            stats["locks"] = await q("SELECT count(*) FROM pg_locks")
        return stats
    except Exception as e:
        logger.warning(f"DB Monit Skipped: {e}")
        return {"connections_total": 0, "connections_active": 0, "connections_idle": 0, "locks": 0, "db_size_bytes": 0}


async def get_active_queries(limit: int = ACTIVE_QUERY_LIMIT) -> List[Dict[str, Any]]:
    try:
        from app.database import engine
        query = text(
            """
            SELECT
                pid,
                usename AS user,
                state,
                COALESCE(wait_event_type || ':' || wait_event, '') AS wait_event,
                EXTRACT(EPOCH FROM (now() - query_start)) AS duration_seconds,
                query
            FROM pg_stat_activity
            WHERE state != 'idle' AND pid <> pg_backend_pid()
            ORDER BY query_start DESC
            LIMIT :limit
            """
        )
        async with engine.connect() as conn:
            result = await conn.execute(query, {"limit": limit})
            rows = result.mappings().all()
            return [dict(row) for row in rows]
    except Exception:
        return []


async def get_dashboard_snapshot() -> Dict[str, Any]:
    # Parallel execution with safety
    sys_task = asyncio.create_task(get_system_metrics())
    gpu_task = asyncio.create_task(get_gpu_metrics())
    net_task = asyncio.create_task(get_network_metrics())
    repo_activity_task = asyncio.create_task(get_repo_activity())

    # DB Tasks (Resilient)
    db_health_task = asyncio.create_task(get_db_health())
    db_stats_task = asyncio.create_task(get_db_stats())
    db_activity_task = asyncio.create_task(get_active_queries())

    sys_metrics = await sys_task
    gpu_metrics = await gpu_task
    net_metrics = await net_task
    repo_activity = await repo_activity_task
    
    # Await DB tasks (they handle their own exceptions now)
    db_health = await db_health_task
    db_stats = await db_stats_task
    db_activity = await db_activity_task

    await check_thresholds_and_log(db_stats, sys_metrics)

    admin_suggestions = [
        "VACUUM (VERBOSE) -- run during maintenance windows",
        "REINDEX DATABASE current_database() -- if bloat is observed",
    ]

    return {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "db_health": db_health,
        "db_stats": db_stats,
        "db_activity": db_activity,
        "system": sys_metrics,
        "gpu": gpu_metrics,
        "network": net_metrics,
        "repo_activity": repo_activity,
        "admin_suggestions": admin_suggestions,
        "thresholds": {
            "cpu_percent": CPU_THRESHOLD,
            "mem_percent": MEM_THRESHOLD,
            "connections": CONN_THRESHOLD,
            "log_file": LOG_PATH,
        },
    }
