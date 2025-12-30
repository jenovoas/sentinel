#!/usr/bin/env python3
"""
Sentinel Cortex - Mock Data Population Script
Injects 24 hours of "historical" metrics to validate Analytics API.
"""
import asyncio
import os
import sys
import random
from datetime import datetime, timedelta
import logging

# Ensure we can import from app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import AsyncSessionLocal
from app.models.monitoring import MetricSample, Anomaly, AnomalyType, SeverityLevel

# Configure Logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("sentinel.mock_data")

async def populate_metrics():
    logger.info("🚀 Starting Mock Data Population...")
    
    async with AsyncSessionLocal() as db:
        # 1. Check if data exists
        # (Skipping check to force population in this demo script)
        
        # 2. Generate 24h of metrics (1 sample every 5 minutes = 288 samples)
        now = datetime.utcnow()
        start_time = now - timedelta(hours=24)
        samples = []
        
        current_time = start_time
        logger.info(f"Generating metrics from {start_time} to {now}")
        
        while current_time <= now:
            # Simulate a healthy system with occasional spikes
            is_spike = random.random() > 0.95
            
            cpu = random.uniform(1.5, 4.0) if not is_spike else random.uniform(15.0, 45.0)
            mem = random.uniform(20.0, 25.0)
            net_recv = random.randint(1000, 50000) if not is_spike else random.randint(1000000, 5000000)
            
            sample = MetricSample(
                sampled_at=current_time,
                cpu_percent=cpu,
                memory_percent=mem,
                memory_used_mb=random.uniform(2048, 4096),
                memory_total_mb=16384,
                gpu_percent=random.uniform(0, 5) if not is_spike else random.uniform(50, 80),
                gpu_memory_percent=random.uniform(10, 30),
                gpu_temperature=random.uniform(40, 60),
                network_bytes_sent=random.randint(500, 10000),
                network_bytes_recv=net_recv,
                network_packets_sent=random.randint(10, 100),
                network_packets_recv=random.randint(50, 500) if not is_spike else random.randint(5000, 10000),
                db_connections_total=100,
                db_connections_active=random.randint(2, 10),
                db_locks=0,
                db_size_bytes=104857600  # 100MB
            )
            samples.append(sample)
            current_time += timedelta(minutes=5)
            
        db.add_all(samples)
        logger.info(f"✅ Added {len(samples)} metric samples.")
        
        # 3. Generate Anomalies (The "Story")
        anomalies = [
            Anomaly(
                detected_at=now - timedelta(hours=22),
                anomaly_type=AnomalyType.SYSTEM_RESOURCE,
                severity=SeverityLevel.LOW,
                title="Minor CPU Spike",
                description="CPU usage exceeded 15% during routine maintenance.",
                metric_value=18.5,
                threshold_value=15.0,
                is_resolved=True,
                resolved_at=now - timedelta(hours=21, minutes=50),
                resolution_notes="Auto-resolved: Process finished."
            ),
            Anomaly(
                detected_at=now - timedelta(hours=14),
                anomaly_type=AnomalyType.SECURITY_PATTERN,
                severity=SeverityLevel.CRITICAL,
                title="Pattern match: reverse_shell",
                description="Detected potential reverse shell attempt via PatternDetector.",
                metric_value=0.98, # Confidence
                threshold_value=0.90,
                context_data={"process": "nc", "args": "-e /bin/sh"},
                is_resolved=True,
                resolved_at=now - timedelta(hours=13, minutes=59),
                resolution_notes="Blocked by Cortex: Fail-Closed Policy."
            ),
            Anomaly(
                detected_at=now - timedelta(hours=2),
                anomaly_type=AnomalyType.TRUTH_INTEGRITY,
                severity=SeverityLevel.HIGH,
                title="Truth Skew Detected",
                description="Ring buffer skew exceeded safety margin.",
                metric_value=1.55, # µs
                threshold_value=1.50,
                is_resolved=False # Still active!
            )
        ]
        
        db.add_all(anomalies)
        logger.info(f"✅ Added {len(anomalies)} anomalies.")
        
        await db.commit()
        logger.info("🎉 Mock Data Population Complete!")

if __name__ == "__main__":
    asyncio.run(populate_metrics())
