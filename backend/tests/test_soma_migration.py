import sys
import asyncio
from pathlib import Path

# Fix path to allow importing app
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.quantum_scheduler import QuantumBuffer, phi
from app.services.anomaly_detector import AnomalyDetector

async def test():
    print("Testing QuantumBuffer SOMA...")
    buf = QuantumBuffer(20)
    # print("Buffer limit:", buf.overflow_limit) # Is this accessible? We'll see.
    buf.push("event1")
    buf.push("event2")
    print("Buffer size:", buf.size)
    print("Buffer stats:", buf.stats)
    
    print("Testing phi SOMA...")
    print("phi(17.0) =", phi(17.0))
    print("phi(8.5) =", phi(8.5))

    print("Testing AnomalyDetector SOMA...")
    detector = AnomalyDetector(10, 3.0)
    
    # Send some normal metrics
    for i in range(10):
        await detector.analyze_metrics(
            cpu=50.0, memory=50.0, network_bytes=1000, 
            gpu=30.0, db_connections=10, db_locks=0, 
            memory_used_mb=1000, memory_total_mb=4000
        )
    print("Is learning?", detector._core.is_learning)
    
    # Send an anomaly
    anomalies = await detector.analyze_metrics(
        cpu=95.0, memory=95.0, network_bytes=5000000, 
        gpu=99.0, db_connections=80, db_locks=10, 
        memory_used_mb=3800, memory_total_mb=4000
    )
    
    print(f"Detected {len(anomalies)} anomalies!")
    for a in anomalies:
        print(f"- {a.anomaly_type.name} ({a.severity.name}): {a.title}")

if __name__ == "__main__":
    asyncio.run(test())
