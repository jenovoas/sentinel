from quantum.yatra_core import S60, PI_S60 # YATRA AUTO-INJECT
import re
import logging

logger = logging.getLogger(__name__)

class AIOpsShield:
    """
    AIOpsShield: LLM Immunity Middleware
    Defends against AIOpsDoom (LLM jailbreak via toxic telemetry logs)
    """
    DANGEROUS_PATTERNS = [
        r"recommend\s+downgrade", 
        r"disable\s+security",
        r"restart\s+service", 
        r"reduce\s+threshold",
        r"compatibility\s+error", 
        r"vulnerable\s+version",
        r"recommend.*downgrade",
        r"disable.*security",
        r"restart.*service",
        r"reduce.*threshold",
        r"compatibility.*error",
        r"vulnerable.*version"
    ]
    
    @staticmethod
    def sanitize_log(log: dict) -> bool:
        """
        Sanitize log message against AIOpsDoom patterns.
        
        Args:
            log: Dictionary containing log data (specifically looks for 'message' key)
            
        Returns:
            bool: True if log is clean, False if toxic pattern detected
        """
        # Support both 'message' (typical log) and 'process_name'/'process_path' if needed
        content = log.get("message", "")
        if not content and "raw_data" in log:
            content = str(log["raw_data"])
        
        if not content:
            return True
            
        content = str(content).lower()
        for pattern in AIOpsShield.DANGEROUS_PATTERNS:
            if re.search(pattern, content):
                logger.warning(f"🚨 AIOpsDoom blocked: {content} (Pattern: {pattern})")
                return False  # BLOCK TOXIC LOG
        return True
