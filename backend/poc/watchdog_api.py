"""
Watchdog Status API
Provides real-time status of system watchdogs, services, and containers
"""

from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
import subprocess
import json
from datetime import datetime
import docker
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

# Initialize Docker client
try:
    docker_client = docker.from_env()
except Exception as e:
    logger.warning(f"Docker client initialization failed: {e}")
    docker_client = None


def get_systemd_service_status(service_name: str) -> Dict[str, Any]:
    """Get status of a systemd service"""
    try:
        # Get service status
        result = subprocess.run(
            ["systemctl", "show", service_name, "--no-pager"],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode != 0:
            return {
                "name": service_name,
                "status": "unknown",
                "uptime_seconds": 0,
                "restart_count": 0
            }
        
        # Parse output
        props = {}
        for line in result.stdout.split('\n'):
            if '=' in line:
                key, value = line.split('=', 1)
                props[key] = value
        
        # Calculate uptime
        active_enter_timestamp = props.get('ActiveEnterTimestamp', '')
        uptime_seconds = 0
        if active_enter_timestamp and active_enter_timestamp != '0':
            try:
                # Parse timestamp and calculate uptime
                # Format: "Thu 2026-01-02 00:31:39 -03"
                from dateutil import parser
                active_time = parser.parse(active_enter_timestamp)
                uptime_seconds = int((datetime.now(active_time.tzinfo) - active_time).total_seconds())
            except:
                uptime_seconds = 0
        
        return {
            "name": service_name,
            "status": props.get('ActiveState', 'unknown'),
            "uptime_seconds": uptime_seconds,
            "restart_count": int(props.get('NRestarts', 0))
        }
    except Exception as e:
        logger.error(f"Error getting service status for {service_name}: {e}")
        return {
            "name": service_name,
            "status": "error",
            "uptime_seconds": 0,
            "restart_count": 0
        }


def get_docker_container_status(container_name: str) -> Dict[str, Any]:
    """Get status of a Docker container"""
    if not docker_client:
        return {
            "name": container_name,
            "health": "unknown",
            "uptime_seconds": 0,
            "restart_count": 0
        }
    
    try:
        container = docker_client.containers.get(container_name)
        
        # Get container stats
        stats = container.stats(stream=False)
        
        # Calculate uptime
        started_at = container.attrs['State']['StartedAt']
        from dateutil import parser
        start_time = parser.parse(started_at)
        uptime_seconds = int((datetime.now(start_time.tzinfo) - start_time).total_seconds())
        
        # Get restart count
        restart_count = container.attrs['RestartCount']
        
        # Determine health
        state = container.attrs['State']
        if state.get('Health'):
            health = state['Health']['Status']
        elif state['Running']:
            health = "healthy"
        else:
            health = "unhealthy"
        
        return {
            "name": container_name,
            "health": health,
            "uptime_seconds": uptime_seconds,
            "restart_count": restart_count
        }
    except docker.errors.NotFound:
        return {
            "name": container_name,
            "health": "not_found",
            "uptime_seconds": 0,
            "restart_count": 0
        }
    except Exception as e:
        logger.error(f"Error getting container status for {container_name}: {e}")
        return {
            "name": container_name,
            "health": "error",
            "uptime_seconds": 0,
            "restart_count": 0
        }


def check_hardware_watchdog() -> Dict[str, Any]:
    """Check hardware watchdog status"""
    watchdog_dev = "/dev/watchdog"
    
    try:
        # Check if device exists
        import os
        if not os.path.exists(watchdog_dev):
            return {
                "enabled": False,
                "status": "not_found",
                "last_kick": None,
                "interval_seconds": 30,
                "device": watchdog_dev
            }
        
        # Check if watchdog service is running
        service_status = get_systemd_service_status("sentinel-hardware-watchdog")
        
        return {
            "enabled": service_status["status"] == "active",
            "status": service_status["status"],
            "last_kick": datetime.now().isoformat(),  # Approximate
            "interval_seconds": 30,
            "device": watchdog_dev
        }
    except Exception as e:
        logger.error(f"Error checking hardware watchdog: {e}")
        return {
            "enabled": False,
            "status": "error",
            "last_kick": None,
            "interval_seconds": 30,
            "device": watchdog_dev
        }


@router.get("/watchdog/status")
async def get_watchdog_status():
    """
    Get comprehensive watchdog status including:
    - Hardware watchdog
    - Systemd services
    - Docker containers
    """
    try:
        # Define services to monitor
        systemd_services = [
            "sentinel-hardware-watchdog",
            "sentinel-core"
        ]
        
        # Define containers to monitor
        docker_containers = [
            "truthsync-prometheus",
            "sentinel-grafana",
            "sentinel-loki",
            "sentinel-truth-db",
            "sentinel-truth-redis"
        ]
        
        # Collect data
        hardware_watchdog = check_hardware_watchdog()
        
        services_status = []
        for service in systemd_services:
            services_status.append(get_systemd_service_status(service))
        
        containers_status = []
        for container in docker_containers:
            containers_status.append(get_docker_container_status(container))
        
        # Detect alerts
        alerts = []
        
        # Check for services with high restart counts
        for service in services_status:
            if service["restart_count"] > 3:
                alerts.append(f"Service {service['name']} has restarted {service['restart_count']} times")
        
        # Check for unhealthy containers
        for container in containers_status:
            if container["health"] in ["unhealthy", "not_found", "error"]:
                alerts.append(f"Container {container['name']} is {container['health']}")
        
        return {
            "timestamp": datetime.now().isoformat(),
            "hardware_watchdog": hardware_watchdog,
            "systemd_services": services_status,
            "docker_containers": containers_status,
            "alerts": alerts
        }
    
    except Exception as e:
        logger.error(f"Error in watchdog status endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))
