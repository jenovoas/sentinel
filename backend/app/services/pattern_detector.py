"""
Pattern Detector Service

Detects security patterns in events using configurable pattern definitions.
Supports 5+ security patterns with extensible architecture.
"""

from typing import List, Dict, Any
import logging
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.security_pattern import SecurityPattern

logger = logging.getLogger(__name__)


class PatternDetector:
    """
    Detects security patterns in events
    
    Uses pattern definitions from the database to identify
    potential security threats in system events.
    """
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self._patterns_cache: Dict[str, SecurityPattern] = {}
    
    async def load_patterns(self) -> None:
        """Load active patterns from database into cache"""
        result = await self.db.execute(
            select(SecurityPattern).where(SecurityPattern.enabled == True)
        )
        patterns = result.scalars().all()
        
        self._patterns_cache = {p.name: p for p in patterns}
        logger.info(f"Loaded {len(self._patterns_cache)} active security patterns")
    
    async def detect(self, event: Dict[str, Any]) -> List[str]:
        """
        Detect patterns in an event
        
        Args:
            event: Event data dictionary with fields like:
                - event_type: 'syscall', 'network', 'memory', 'file'
                - syscall: syscall name (if event_type == 'syscall')
                - process_path: path to binary
                - user: username
                - uid: user ID
                - etc.
        
        Returns:
            List of detected pattern names
        """
        if not self._patterns_cache:
            await self.load_patterns()
        
        detected = []
        
        # Check each pattern
        for pattern_name, pattern in self._patterns_cache.items():
            if await self._check_pattern(event, pattern):
                detected.append(pattern_name)
                # Update detection count
                pattern.detection_count += 1
        
        if detected:
            logger.info(f"Detected patterns: {detected} in event type {event.get('event_type')}")
        
        return detected
    
    async def _check_pattern(self, event: Dict[str, Any], pattern: SecurityPattern) -> bool:
        """
        Check if an event matches a specific pattern
        
        Args:
            event: Event data
            pattern: Pattern definition
        
        Returns:
            True if pattern matches
        """
        indicators = pattern.indicators
        
        # Dispatch to specific pattern checkers
        if pattern.name == "privilege_escalation":
            return self._check_privilege_escalation(event, indicators)
        elif pattern.name == "malicious_binary":
            return self._check_malicious_binary(event, indicators)
        elif pattern.name == "suspicious_network":
            return self._check_suspicious_network(event, indicators)
        elif pattern.name == "data_exfiltration":
            return self._check_data_exfiltration(event, indicators)
        elif pattern.name == "lateral_movement":
            return self._check_lateral_movement(event, indicators)
        else:
            logger.warning(f"Unknown pattern: {pattern.name}")
            return False
    
    def _check_privilege_escalation(self, event: Dict[str, Any], indicators: Dict) -> bool:
        """
        Detect privilege escalation attempts
        
        Indicators:
            - syscalls: setuid, setgid, setreuid, setregid
            - target_uid: 0 (root)
        """
        if event.get("event_type") != "syscall":
            return False
        
        syscall = event.get("syscall", "")
        target_uid = event.get("target_uid")
        current_uid = event.get("uid")
        
        # Check if it's a privilege-related syscall
        if syscall not in indicators.get("syscalls", []):
            return False
        
        # Check if trying to become root
        if target_uid != indicators.get("target_uid", 0):
            return False
        
        # Check if not already root (escalation, not just using root)
        if current_uid == 0:
            return False
        
        logger.warning(
            f"🚨 Privilege escalation detected: {syscall} "
            f"from uid={current_uid} to uid={target_uid}"
        )
        return True
    
    def _check_malicious_binary(self, event: Dict[str, Any], indicators: Dict) -> bool:
        """
        Detect execution of binaries from suspicious locations
        
        Indicators:
            - paths: /tmp/, /dev/shm/, /var/tmp/
            - syscalls: execve
        """
        if event.get("event_type") != "syscall":
            return False
        
        syscall = event.get("syscall", "")
        process_path = event.get("process_path", "")
        
        # Check if it's an exec syscall
        if syscall not in indicators.get("syscalls", []):
            return False
        
        # Check if binary is in suspicious location
        suspicious_paths = indicators.get("paths", [])
        is_suspicious = any(process_path.startswith(path) for path in suspicious_paths)
        
        if is_suspicious:
            logger.warning(
                f"🚨 Malicious binary detected: {process_path} "
                f"executed via {syscall}"
            )
            return True
        
        return False
    
    def _check_suspicious_network(self, event: Dict[str, Any], indicators: Dict) -> bool:
        """
        Detect suspicious network activity
        
        Indicators:
            - ports: 4444, 1337, 31337 (common backdoor ports)
            - protocols: raw
        """
        if event.get("event_type") != "network":
            return False
        
        dest_port = event.get("dest_port")
        protocol = event.get("protocol", "")
        
        # Check for suspicious ports
        suspicious_ports = indicators.get("ports", [])
        if dest_port in suspicious_ports:
            logger.warning(
                f"🚨 Suspicious network activity: connection to port {dest_port}"
            )
            return True
        
        # Check for raw sockets (often used for packet crafting)
        if protocol in indicators.get("protocols", []):
            logger.warning(
                f"🚨 Suspicious network activity: {protocol} protocol usage"
            )
            return True
        
        return False
    
    def _check_data_exfiltration(self, event: Dict[str, Any], indicators: Dict) -> bool:
        """
        Detect potential data exfiltration
        
        Indicators:
            - min_bytes: 10485760 (10MB)
            - external_only: true
        """
        if event.get("event_type") != "network":
            return False
        
        bytes_sent = event.get("bytes_sent", 0)
        is_external = event.get("is_external", False)
        
        min_bytes = indicators.get("min_bytes", 10485760)
        external_only = indicators.get("external_only", True)
        
        # Check if large data transfer
        if bytes_sent < min_bytes:
            return False
        
        # Check if to external destination (if required)
        if external_only and not is_external:
            return False
        
        logger.warning(
            f"🚨 Data exfiltration detected: {bytes_sent} bytes sent "
            f"to {'external' if is_external else 'internal'} destination"
        )
        return True
    
    def _check_lateral_movement(self, event: Dict[str, Any], indicators: Dict) -> bool:
        """
        Detect lateral movement attempts
        
        Indicators:
            - syscalls: connect
            - internal_network: true
            - ssh_like: true (port 22 or similar)
        """
        if event.get("event_type") not in ["syscall", "network"]:
            return False
        
        # For syscall events
        if event.get("event_type") == "syscall":
            syscall = event.get("syscall", "")
            if syscall not in indicators.get("syscalls", []):
                return False
        
        # Check if internal network
        is_internal = event.get("is_internal", False)
        if indicators.get("internal_network", True) and not is_internal:
            return False
        
        # Check if SSH-like (port 22, 2222, etc.)
        dest_port = event.get("dest_port", 0)
        ssh_ports = [22, 2222, 2200]
        is_ssh_like = dest_port in ssh_ports
        
        if indicators.get("ssh_like", True) and is_ssh_like:
            logger.warning(
                f"🚨 Lateral movement detected: SSH-like connection "
                f"to internal host on port {dest_port}"
            )
            return True
        
        return False
