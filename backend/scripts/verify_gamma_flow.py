#!/usr/bin/env python3
"""Read-only Gamma queue inventory; human review belongs to the authenticated UI.

Does not create telemetry, decisions, sessions, or synthetic human approvals.
Use the isolated Gamma tests to exercise state transitions.
"""
import asyncio
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import AsyncSessionLocal
from app.services.guardian_gamma import GuardianGammaService


async def verify_gamma_flow():
    async with AsyncSessionLocal() as db:
        pending = await GuardianGammaService(db).get_pending_decisions()
        print(f"Pending Gamma decisions (up to 50): {len(pending)}")
        for decision in pending:
            print({key: decision[key] for key in (
                "id", "guardian", "type", "confidence_s60_raw", "created_at", "timeout_at"
            )})
        print("Review/approval requires a real platform-superuser session at /security/gamma.")


if __name__ == "__main__":
    asyncio.run(verify_gamma_flow())
