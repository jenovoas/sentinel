from datetime import datetime, UTC
from typing import List, Dict, Any, Optional
import uuid
from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.failsafe import FailSafeExecution

async def track_execution(
    db: AsyncSession,
    playbook: str,
    triggered_by: str,
    severity: str,
    context_data: Optional[Dict[str, Any]] = None
) -> FailSafeExecution:
    """Record a new fail-safe playbook execution"""
    execution = FailSafeExecution(
        playbook=playbook,
        triggered_by=triggered_by,
        severity=severity,
        status="triggered",
        context_data=context_data,
        triggered_at=datetime.now(UTC)
    )
    db.add(execution)
    await db.commit()
    await db.refresh(execution)
    return execution

async def update_execution(
    db: AsyncSession,
    execution_id: uuid.UUID,
    status: str,
    outcome: Optional[str] = None
) -> Optional[FailSafeExecution]:
    """Update an existing execution status and outcome"""
    result = await db.execute(
        select(FailSafeExecution).where(FailSafeExecution.id == execution_id)
    )
    execution = result.scalar_one_or_none()

    if execution:
        execution.status = status
        execution.outcome = outcome
        if status in ["success", "failed"]:
            execution.completed_at = datetime.now(UTC)
        db.add(execution)
        await db.commit()
        await db.refresh(execution)

    return execution

async def get_failsafe_stats(db: AsyncSession) -> Dict[str, Any]:
    """Get aggregated failsafe statistics and playbook details"""
    # 1. Overall status
    total_executions_query = await db.execute(select(func.count(FailSafeExecution.id)))
    total_executions = total_executions_query.scalar() or 0

    success_executions_query = await db.execute(
        select(func.count(FailSafeExecution.id)).where(FailSafeExecution.status == "success")
    )
    success_executions = success_executions_query.scalar() or 0

    success_rate = (success_executions / total_executions * 100) if total_executions > 0 else 100.0

    # 2. Last auto-remediation
    last_remediation_query = await db.execute(
        select(FailSafeExecution.triggered_at)
        .where(FailSafeExecution.playbook == "auto_remediation")
        .order_by(desc(FailSafeExecution.triggered_at))
        .limit(1)
    )
    last_remediation_time = last_remediation_query.scalar()

    last_remediation_str = "Never"
    if last_remediation_time:
        if last_remediation_time.tzinfo is None:
            last_remediation_time = last_remediation_time.replace(tzinfo=UTC)
        diff = datetime.now(UTC) - last_remediation_time
        if diff.days > 0:
            last_remediation_str = f"{diff.days} days ago"
        elif diff.seconds // 3600 > 0:
            last_remediation_str = f"{diff.seconds // 3600} hours ago"
        else:
            last_remediation_str = f"{diff.seconds // 60} minutes ago"

    # 3. Individual playbook stats
    playbooks_config = [
        {"name": "backup_recovery", "display_name": "Backup Recovery"},
        {"name": "intrusion_lockdown", "display_name": "Intrusion Lockdown"},
        {"name": "health_failsafe", "display_name": "Health Failsafe"},
        {"name": "integrity_check", "display_name": "Backup Integrity Check"},
        {"name": "offboarding", "display_name": "Secure Offboarding"},
        {"name": "auto_remediation", "display_name": "Anomaly Auto-Remediation"},
    ]

    playbook_results = []
    for pb in playbooks_config:
        # Get count and success rate per playbook
        count_q = await db.execute(
            select(func.count(FailSafeExecution.id)).where(FailSafeExecution.playbook == pb["name"])
        )
        count = count_q.scalar() or 0

        succ_q = await db.execute(
            select(func.count(FailSafeExecution.id))
            .where(FailSafeExecution.playbook == pb["name"], FailSafeExecution.status == "success")
        )
        succ = succ_q.scalar() or 0

        last_q = await db.execute(
            select(FailSafeExecution)
            .where(FailSafeExecution.playbook == pb["name"])
            .order_by(desc(FailSafeExecution.triggered_at))
            .limit(1)
        )
        last_exec = last_q.scalar_one_or_none()

        pb_success_rate = (succ / count * 100) if count > 0 else 0.0

        last_run_str = "Never"
        if last_exec:
            last_exec_time = last_exec.triggered_at
            if last_exec_time.tzinfo is None:
                last_exec_time = last_exec_time.replace(tzinfo=UTC)
            diff = datetime.now(UTC) - last_exec_time
            if diff.days > 0:
                last_run_str = f"{diff.days} days ago"
            elif diff.seconds // 3600 > 0:
                last_run_str = f"{diff.seconds // 3600} hours ago"
            else:
                last_run_str = f"{diff.seconds // 60} minutes ago"

        playbook_results.append({
            "name": pb["name"],
            "display_name": pb["display_name"],
            "status": last_exec.status if last_exec else "idle",
            "last_run": last_run_str,
            "last_outcome": last_exec.outcome if last_exec else None,
            "execution_count": count,
            "success_rate": round(pb_success_rate, 1),
        })

    return {
        "status": "active",
        "last_auto_remediation": last_remediation_str,
        "active_playbooks": len(playbooks_config),
        "success_rate_30d": round(success_rate, 1),
        "total_executions": total_executions,
        "playbooks": playbook_results
    }
