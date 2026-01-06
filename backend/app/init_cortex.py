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
            "weight": 0.9,
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
            "weight": 0.7,
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
            "weight": 0.95,
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
            "weight": 0.85,
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
            "weight": 0.8,
            "enabled": True
        }
    ]
    
    async with AsyncSessionLocal() as session:
        try:
            # Check if patterns already exist
            result = await session.execute(select(SecurityPattern))
            existing = result.scalars().all()
            
            if existing:
                print(f"✅ Security patterns already initialized ({len(existing)} patterns)")
                return
            
            # Insert default patterns
            for pattern_data in default_patterns:
                pattern = SecurityPattern(**pattern_data)
                session.add(pattern)
            
            await session.commit()
            print(f"✅ Initialized {len(default_patterns)} security patterns")
            
        except Exception as e:
            await session.rollback()
            print(f"❌ Failed to initialize security patterns: {e}")
            raise


if __name__ == "__main__":
    asyncio.run(init_security_patterns())
