import asyncio
import unittest
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, String, DateTime, JSON, func
import sys
import os

# Mock the Base to avoid full app dependency if needed, but we can try to use the real one
# For simplicity and isolation, we'll use a local setup for this logic test

sys.path.append(os.path.join(os.getcwd(), "backend"))

from app.database import Base
from app.models.failsafe import FailSafeExecution
from app.services.failsafe_service import track_execution, update_execution, get_failsafe_stats

class TestFailSafeService(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.engine = create_async_engine("sqlite+aiosqlite:///:memory:")
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        self.AsyncSessionLocal = async_sessionmaker(
            self.engine, class_=AsyncSession, expire_on_commit=False
        )
        self.session = self.AsyncSessionLocal()

    async def asyncTearDown(self):
        await self.session.close()
        await self.engine.dispose()

    async def test_track_and_update_execution(self):
        # Test tracking
        execution = await track_execution(
            self.session,
            playbook="backup_recovery",
            triggered_by="test_trigger",
            severity="high",
            context_data={"test": "data"}
        )

        self.assertEqual(execution.playbook, "backup_recovery")
        self.assertEqual(execution.status, "triggered")

        # Test update
        updated = await update_execution(
            self.session,
            execution.id,
            status="success",
            outcome="Everything worked"
        )

        self.assertEqual(updated.status, "success")
        self.assertEqual(updated.outcome, "Everything worked")
        self.assertIsNotNone(updated.completed_at)

    async def test_get_stats(self):
        # Insert some data
        await track_execution(self.session, "auto_remediation", "sys", "low")
        exec2 = await track_execution(self.session, "backup_recovery", "sys", "high")
        await update_execution(self.session, exec2.id, "success", "fixed")

        stats = await get_failsafe_stats(self.session)

        self.assertEqual(stats["total_executions"], 2)
        self.assertEqual(stats["success_rate_30d"], 50.0)
        self.assertTrue(any(p["name"] == "backup_recovery" and p["execution_count"] == 1 for p in stats["playbooks"]))
        self.assertTrue(any(p["name"] == "auto_remediation" and p["status"] == "triggered" for p in stats["playbooks"]))

if __name__ == "__main__":
    # We need aiosqlite for this test
    import subprocess
    subprocess.run(["pip", "install", "aiosqlite"], capture_output=True)
    unittest.main()
