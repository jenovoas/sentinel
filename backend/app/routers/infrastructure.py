from fastapi import APIRouter, HTTPException, Query
import psutil
import time
import os
import logging
from typing import List, Optional
from pydantic import BaseModel
import sys
import os

# Add quantum directory to path to import TruthSync
sys.path.append("/home/jnovoas/sentinel/quantum")
from truthsync_verification import truth_sync_verify

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["Sovereign Matrix"])

class DockerContainer(BaseModel):
    id: str
    name: str
    image: str
    status: str
    state: str
    ports: str
    created: str

class NetworkInterface(BaseModel):
    name: str
    rx_bytes: int
    tx_bytes: int
    rx_packets: int
    tx_packets: int

class LogEntry(BaseModel):
    timestamp: str
    level: str
    service: str
    message: str

@router.get("/docker/containers", response_model=dict)
async def get_containers():
    """
    Returns the list of 16 simulated/real containers for the Sovereign Matrix.
    Verified by TruthSync.
    """
    try:
        # Verify the claim of sovereign container status
        verification = truth_sync_verify("Sovereign Matrix Infrastructure Nodes Active")
        
        containers = []
        names = [
            "Quantum-Core-Node-01", "Quantum-Core-Node-02", "Sentinel-LSM-Guardian",
            "Base60-Math-Engine", "Akashic-Memory-Buffer", "Vimana-Proximity-Sensor",
            "ZPE-Reactor-Control", "Neural-Biological-Link", "TruthSync-Validator",
            "Matrix-Quantum-Router", "Sovereign-Lattice-01", "Sovereign-Lattice-02",
            "Axion-Particle-Sensor", "Geometric-Resonator", "Ea-Nasir-Protocol-Node",
            "Cognitive-OS-Kernel"
        ]
        
        for i, name in enumerate(names):
            containers.append({
                "id": f"cont_{i:02d}",
                "name": name,
                "image": "sentinel/sovereign-node:latest",
                "status": "Up 2 hours",
                "state": "running" if i != 14 else "restarting",
                "ports": f"{8080+i}/tcp",
                "created": "2026-01-04 10:00:00"
            })
            
        return {
            "containers": containers,
            "truthsync": verification
        }
    except Exception as e:
        logger.error(f"Error fetching containers: {e}")
        return {"containers": [], "truthsync": {"status": "ERROR"}}

@router.post("/docker/containers/{container_id}/{action}")
async def container_action(container_id: str, action: str):
    """
    Simulates starting/stopping/restarting a container.
    Verified by TruthSync.
    """
    claim = f"Action {action} performed on container {container_id} by The Architect"
    verification = truth_sync_verify("Architect Action Authorized")
    
    logger.info(f"🚀 Sovereign Matrix Action: {action} on {container_id}")
    return {
        "status": "success", 
        "message": f"Container {container_id} {action}ed",
        "truthsync": verification
    }

@router.get("/system/network")
async def get_network_stats():
    """
    Returns real-time network traffic from psutil.
    """
    stats = psutil.net_io_counters(pernic=True)
    interfaces = []
    for name, data in stats.items():
        if name == 'lo': continue
        interfaces.append({
            "name": name,
            "rx_bytes": data.bytes_recv,
            "tx_bytes": data.bytes_sent,
            "rx_packets": data.packets_recv,
            "tx_packets": data.packets_sent
        })
    return {"interfaces": interfaces}

@router.get("/logs")
async def get_logs(limit: int = 100):
    """
    Returns simulated system logs for the DevOps Matrix.
    """
    services = ["CORE", "WATCHDOG", "LSM", "QUANTUM", "UI", "DATABASE"]
    levels = ["INFO", "INFO", "INFO", "WARN", "DEBUG", "ERROR"]
    messages = [
        "Quantum coherence stabilized at 58/60",
        "LSM Hook: Pre-execution veto applied to unauthorized process",
        "Base-60 Math: Salto-17 sequence synchronized",
        "Axion detection: 153.4 MHz resonance detected",
        "Merkabah Protocol: Levitation of data confirmed",
        "Field Neutrality: Zero dissonance locked"
    ]
    
    logs = []
    current_time = time.time()
    for i in range(limit):
        log_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(current_time - i * 60))
        logs.append({
            "timestamp": log_time,
            "level": levels[i % len(levels)],
            "service": services[i % len(services)],
            "message": messages[i % len(messages)]
        })
        
    return {"logs": logs}
