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
    stats = {}
    stats["connections_total"] = await _fetch_one(
        "SELECT count(*) FROM pg_stat_activity"
    )
    stats["connections_active"] = await _fetch_one(
        "SELECT count(*) FROM pg_stat_activity WHERE state = 'active'"
    )
    stats["connections_idle"] = await _fetch_one(
        "SELECT count(*) FROM pg_stat_activity WHERE state = 'idle'"
    )
    stats["db_size_bytes"] = await _fetch_one(
        "SELECT pg_database_size(current_database())"
    )
    stats["locks"] = await _fetch_one("SELECT count(*) FROM pg_locks")
    return stats


async def get_active_queries(limit: int = ACTIVE_QUERY_LIMIT) -> List[Dict[str, Any]]:
    """List current active queries with duration and wait events."""
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


async def get_db_health() -> Dict[str, Any]:
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        return {"status": "healthy"}
    except Exception as exc:  # pragma: no cover - just safety
        return {"status": "unhealthy", "error": str(exc)}


async def _run_in_executor(func, *args):
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, func, *args)


async def get_system_metrics() -> Dict[str, Any]:
    """Collect CPU and memory metrics using psutil off the main loop."""
    cpu = await _run_in_executor(psutil.cpu_percent, 0.5)
    mem_info = await _run_in_executor(psutil.virtual_memory)
    return {
        "cpu_percent": cpu,
        "mem_percent": mem_info.percent,
        "mem_used": mem_info.used,
        "mem_total": mem_info.total,
    }


def _run_git(repo_path: str, args: List[str]) -> Dict[str, Any]:
    cmd = ["git", "-C", repo_path, *args]
    try:
        completed = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )
    except Exception as exc:  # pragma: no cover - guard rails
        return {"ok": False, "error": str(exc)}

    if completed.returncode != 0:
        return {"ok": False, "error": completed.stderr.strip() or "git error"}

    return {"ok": True, "output": completed.stdout.strip()}


async def get_repo_activity(repo_path: str = "/app") -> Dict[str, Any]:
    """Return recent commits and working tree changes for visibility."""
    # Check if we're in a git repo first
    check_result = await _run_in_executor(
        _run_git,
        repo_path,
        ["rev-parse", "--git-dir"],
    )
    
    if not check_result.get("ok"):
        # Not a git repo, return empty data without warning (expected in container volumes)
        return {
            "recent_commits": [],
            "working_tree": [],
        }
    
    log_result = await _run_in_executor(
        _run_git,
        repo_path,
        ["log", "-5", "--pretty=format:%h|%an|%ar|%s"],
    )
    status_result = await _run_in_executor(
        _run_git,
        repo_path,
        ["status", "--short"],
    )

    data: Dict[str, Any] = {"recent_commits": [], "working_tree": []}

    if log_result.get("ok"):
        lines = log_result.get("output", "").splitlines()
        for line in lines:
            parts = line.split("|", 3)
            if len(parts) == 4:
                data["recent_commits"].append(
                    {"hash": parts[0], "author": parts[1], "when": parts[2], "message": parts[3]}
                )

    if status_result.get("ok"):
        data["working_tree"] = status_result.get("output", "").splitlines()

    return data


def _ensure_log_dir():
    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)


def _log_overconsumption(event: str, payload: Dict[str, Any]) -> None:
    _ensure_log_dir()
    logger.setLevel(logging.INFO)
    if not logger.handlers:
        handler = logging.FileHandler(LOG_PATH)
        fmt = logging.Formatter("%(asctime)s %(message)s")
        handler.setFormatter(fmt)
        logger.addHandler(handler)
    logger.info("%s | %s", event, payload)


async def check_thresholds_and_log(db_stats: Dict[str, Any], sys_metrics: Dict[str, Any]) -> None:
    """Log overconsumption events when thresholds are exceeded."""
    if db_stats.get("connections_total", 0) > CONN_THRESHOLD:
        _log_overconsumption(
            "db_connections_high",
            {
                "connections_total": db_stats.get("connections_total"),
                "threshold": CONN_THRESHOLD,
            },
        )
    if sys_metrics.get("cpu_percent", 0) > CPU_THRESHOLD:
        _log_overconsumption(
            "cpu_high",
            {
                "cpu_percent": sys_metrics.get("cpu_percent"),
                "threshold": CPU_THRESHOLD,
            },
        )
    if sys_metrics.get("mem_percent", 0) > MEM_THRESHOLD:
        _log_overconsumption(
            "memory_high",
            {
                "mem_percent": sys_metrics.get("mem_percent"),
                "mem_used": sys_metrics.get("mem_used"),
                "mem_total": sys_metrics.get("mem_total"),
                "threshold": MEM_THRESHOLD,
            },
        )


async def get_dashboard_snapshot() -> Dict[str, Any]:
    db_health_task = asyncio.create_task(get_db_health())
    db_stats_task = asyncio.create_task(get_db_stats())
    sys_task = asyncio.create_task(get_system_metrics())
    db_activity_task = asyncio.create_task(get_active_queries())
    repo_activity_task = asyncio.create_task(get_repo_activity())

    db_health = await db_health_task
    db_stats = await db_stats_task
    sys_metrics = await sys_task
    db_activity = await db_activity_task
    repo_activity = await repo_activity_task

    await check_thresholds_and_log(db_stats, sys_metrics)

    admin_suggestions = [
        "VACUUM (VERBOSE) -- run during maintenance windows",
        "REINDEX DATABASE current_database() -- if bloat is observed",
        "Terminate long idle connections: SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE state='idle' AND state_change < now()-interval '15 minutes';",
    ]

    return {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "db_health": db_health,
        "db_stats": db_stats,
        "db_activity": db_activity,
        "system": sys_metrics,
        "repo_activity": repo_activity,
        "admin_suggestions": admin_suggestions,
        "thresholds": {
            "cpu_percent": CPU_THRESHOLD,
            "mem_percent": MEM_THRESHOLD,
            "connections": CONN_THRESHOLD,
            "log_file": LOG_PATH,
        },
    }
