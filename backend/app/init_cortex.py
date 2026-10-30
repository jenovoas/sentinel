"""
Initialize Cortex Decision Engine with default security patterns
"""

from quantum.yatra_core import S60, PI_S60 # YATRA AUTO-INJECT
import asyncio
from sqlalchemy import select
from app.database import AsyncSessionLocal
from app.models.security_pattern import SecurityPattern


async def init_security_patterns():
    """Insert default security patterns if they don't exist"""
    
    default_patterns = [
        {
            "name": "privilege_escalation",
            "display_name": "Privilege Escalation",
            "description": "Detects attempts to escalate privileges (e.g., setuid to root)",
            "severity": "critical",
            "indicators": {
                "syscalls": ["setuid", "setgid", "setreuid", "setregid"],
                "target_uid": 0
            },
            "weight": S60(0, 54, 0).to_base_units(),
            "enabled": True
        },
        {
            "name": "suspicious_network",
            "display_name": "Suspicious Network Activity",
            "description": "Detects unusual network connections or data transfers",
            "severity": "high",
            "indicators": {
                "ports": [4444, 1337, 31337],
                "protocols": ["raw"]
            },
            "weight": S60(0, 42, 0).to_base_units(),
            "enabled": True
        },
        {
            "name": "malicious_binary",
            "display_name": "Malicious Binary Execution",
            "description": "Detects execution of binaries from suspicious locations",
            "severity": "critical",
            "indicators": {
                "paths": ["/tmp/", "/dev/shm/", "/var/tmp/"],
                "syscalls": ["execve"]
            },
            "weight": S60(0, 57, 0).to_base_units(),
            "enabled": True
        },
        {
            "name": "data_exfiltration",
            "display_name": "Data Exfiltration",
            "description": "Detects large data transfers to external destinations",
            "severity": "high",
            "indicators": {
                "min_bytes": 10485760,
                "external_only": True
            },
            "weight": S60(0, 51, 0).to_base_units(),
            "enabled": True
        },
        {
            "name": "lateral_movement",
            "display_name": "Lateral Movement",
            "description": "Detects attempts to move laterally across the network",
            "severity": "high",
            "indicators": {
                "syscalls": ["connect"],
                "internal_network": True,
                "ssh_like": True
            },
            "weight": S60(0, 48, 0).to_base_units(),
            "enabled": True
        }
    ]
    
    async with AsyncSessionLocal() as session:
        try:
            result = await session.execute(select(SecurityPattern))
            existing = {pattern.name: pattern for pattern in result.scalars().all()}
            for pattern_data in default_patterns:
                pattern = existing.get(pattern_data["name"])
                if pattern is None:
                    session.add(SecurityPattern(**pattern_data))
                else:
                    # Keep operator-tuned rows intact; add only project defaults missing by name.
                    continue
            
            await session.commit()
            print(f"✅ Security patterns present: {len(existing)} existing, defaults inserted where missing")
            
        except Exception as e:
            await session.rollback()
            print(f"❌ Failed to initialize security patterns: {e}")
            raise


if __name__ == "__main__":
    asyncio.run(init_security_patterns())
