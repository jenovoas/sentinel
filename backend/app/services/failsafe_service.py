import uuid
from datetime import datetime, timedelta, UTC
from typing import Dict, Any, Optional
from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession
from ..models.failsafe import FailSafeExecution, FailSafeStatus


class FailSafeService:
    @staticmethod
    async def create_execution(
        db: AsyncSession,
        playbook: str,
        triggered_by: str,
        severity: str,
        context_data: Optional[Dict[str, Any]] = None,
    ) -> FailSafeExecution:
        execution = FailSafeExecution(
            playbook=playbook,
            triggered_by=triggered_by,
            severity=severity,
            status=FailSafeStatus.TRIGGERED,
            context_data=context_data,
            started_at=datetime.now(UTC),
        )
        db.add(execution)
        await db.commit()
        await db.refresh(execution)
        return execution

    @staticmethod
    async def update_execution_status(
        db: AsyncSession,
        execution_id: uuid.UUID,
        status: FailSafeStatus,
        outcome: Optional[str] = None,
    ) -> Optional[FailSafeExecution]:
        result = await db.execute(
            select(FailSafeExecution).where(FailSafeExecution.id == execution_id)
        )
        execution = result.scalar_one_or_none()
        if execution:
            execution.status = status
            execution.outcome = outcome
            execution.finished_at = datetime.now(UTC)
            await db.commit()
            await db.refresh(execution)
        return execution

    @staticmethod
    async def get_failsafe_status(db: AsyncSession) -> Dict[str, Any]:
        # Defined playbooks (matches failsafe.py)
        PLAYBOOKS = [
            {"name": "backup_recovery", "display_name": "Backup Recovery"},
            {"name": "intrusion_lockdown", "display_name": "Intrusion Lockdown"},
            {"name": "health_failsafe", "display_name": "Health Failsafe"},
            {"name": "integrity_check", "display_name": "Backup Integrity Check"},
            {"name": "offboarding", "display_name": "Secure Offboarding"},
            {"name": "auto_remediation", "display_name": "Anomaly Auto-Remediation"},
        ]

        # Total executions
        total_exec_result = await db.execute(select(func.count(FailSafeExecution.id)))
        total_executions = total_exec_result.scalar() or 0

        # Success rate (last 30 days)
        thirty_days_ago = datetime.now(UTC) - timedelta(days=30)
        recent_stats_result = await db.execute(
            select(
                func.count(FailSafeExecution.id).label("total"),
                func.count(FailSafeExecution.id)
                .filter(FailSafeExecution.status == FailSafeStatus.SUCCESS)
                .label("success"),
            ).where(FailSafeExecution.started_at >= thirty_days_ago)
        )
        recent_stats = recent_stats_result.mappings().first()
        success_rate_30d = 0.0
        if recent_stats and recent_stats["total"] > 0:
            success_rate_30d = (recent_stats["success"] / recent_stats["total"]) * 100

        # Last auto-remediation
        last_remediation_result = await db.execute(
            select(FailSafeExecution.started_at)
            .order_by(desc(FailSafeExecution.started_at))
            .limit(1)
        )
        last_remediation_dt = last_remediation_result.scalar()
        last_remediation_str = "Never"
        if last_remediation_dt:
            # Simple relative time for now, or just ISO string
            diff = datetime.now(UTC) - last_remediation_dt
            if diff.days > 0:
                last_remediation_str = f"{diff.days} days ago"
            elif diff.seconds // 3600 > 0:
                last_remediation_str = f"{diff.seconds // 3600} hours ago"
            elif diff.seconds // 60 > 0:
                last_remediation_str = f"{diff.seconds // 60} minutes ago"
            else:
                last_remediation_str = "just now"

        # Per-playbook stats
        playbook_stats = []
        for pb in PLAYBOOKS:
            pb_result = await db.execute(
                select(
                    func.count(FailSafeExecution.id).label("count"),
                    func.count(FailSafeExecution.id)
                    .filter(FailSafeExecution.status == FailSafeStatus.SUCCESS)
                    .label("success"),
                    func.max(FailSafeExecution.started_at).label("last_run"),
                    # Get the outcome of the last run
                ).where(FailSafeExecution.playbook == pb["name"])
            )
            stats = pb_result.mappings().first()

            last_outcome = None
            if stats["last_run"]:
                outcome_result = await db.execute(
                    select(FailSafeExecution.outcome, FailSafeExecution.status)
                    .where(
                        FailSafeExecution.playbook == pb["name"],
                        FailSafeExecution.started_at == stats["last_run"],
                    )
                    .limit(1)
                )
                last_run_data = outcome_result.mappings().first()
                if last_run_data:
                    last_outcome = last_run_data["outcome"] or last_run_data["status"]

            last_run_str = "Never"
            if stats["last_run"]:
                diff = datetime.now(UTC) - stats["last_run"]
                if diff.days > 0:
                    last_run_str = f"{diff.days} days ago"
                elif diff.seconds // 3600 > 0:
                    last_run_str = f"{diff.seconds // 3600} hours ago"
                elif diff.seconds // 60 > 0:
                    last_run_str = f"{diff.seconds // 60} minutes ago"
                else:
                    last_run_str = "just now"

            pb_success_rate = 0.0
            if stats["count"] > 0:
                pb_success_rate = (stats["success"] / stats["count"]) * 100

            playbook_stats.append(
                {
                    "name": pb["name"],
                    "display_name": pb["display_name"],
                    "status": "idle",  # Could be dynamic if we check active ones
                    "last_run": last_run_str,
                    "last_outcome": last_outcome,
                    "execution_count": stats["count"],
                    "success_rate": pb_success_rate,
                }
            )

        return {
            "status": "active",
            "last_auto_remediation": last_remediation_str,
            "active_playbooks": len(PLAYBOOKS),
            "success_rate_30d": round(success_rate_30d, 1),
            "total_executions": total_executions,
            "playbooks": playbook_stats,
        }
