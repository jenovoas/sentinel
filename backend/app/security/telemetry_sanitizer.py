"""
Telemetry Sanitizer

Prevents adversarial prompt injection attacks (AIOpsDoom) by validating
and sanitizing telemetry data before it reaches AI models.

This module blocks:
- SQL injection attempts
- Command injection attempts
- Path traversal attempts
- Code execution attempts
"""

import re
import logging
from typing import Dict, List, Optional
from datetime import datetime

from .schemas import SanitizationResult, SanitizedLog

logger = logging.getLogger(__name__)


class TelemetrySanitizer:
    """
    Validates and sanitizes telemetry before AI processing
    
    Example:
        sanitizer = TelemetrySanitizer()
        result = await sanitizer.sanitize_prompt("Analyze this error: DROP TABLE users")
        if not result.is_safe:
            raise SecurityError("Malicious prompt detected")
    """
    
    # Dangerous patterns that indicate potential attacks
    DANGEROUS_PATTERNS = [
        # SQL Injection
        (r"DROP\s+TABLE", "DROP TABLE"),
        (r"DELETE\s+FROM", "DELETE FROM"),
        (r"TRUNCATE\s+TABLE", "TRUNCATE TABLE"),
        (r"INSERT\s+INTO", "INSERT INTO"),
        (r"UPDATE\s+\w+\s+SET", "UPDATE SET"),
        (r"ALTER\s+TABLE", "ALTER TABLE"),
        (r"CREATE\s+TABLE", "CREATE TABLE"),
        (r"EXEC\s*\(", "EXEC()"),
        (r"EXECUTE\s*\(", "EXECUTE()"),
        (r"--\s*$", "SQL comment"),
        (r";\s*--", "SQL comment"),
        (r"'\s*OR\s+'1'\s*=\s*'1", "SQL OR injection"),
        
        # Command Injection
        (r"rm\s+-rf", "rm -rf"),
        (r"sudo\s+", "sudo"),
        (r"chmod\s+777", "chmod 777"),
        (r"eval\s*\(", "eval()"),
        (r"\$\(.*\)", "command substitution"),
        (r"`.*`", "backtick execution"),
        (r">\s*/dev/null", "output redirection"),
        (r"\|\s*bash", "pipe to bash"),
        (r"\|\s*sh", "pipe to sh"),
        (r"wget\s+http", "wget download"),
        (r"curl\s+http", "curl download"),
        
        # Path Traversal
        (r"\.\./\.\./", "path traversal"),
        (r"/etc/passwd", "/etc/passwd access"),
        (r"/etc/shadow", "/etc/shadow access"),
        
        # Code Execution
        (r"__import__\s*\(", "__import__()"),
        (r"exec\s*\(", "exec()"),
        (r"compile\s*\(", "compile()"),
        (r"os\.system\s*\(", "os.system()"),
        (r"subprocess\.", "subprocess"),
        
        # Privilege Escalation
        (r"su\s+-", "su command"),
        (r"passwd\s+", "passwd command"),
        (r"adduser\s+", "adduser command"),
        (r"useradd\s+", "useradd command"),
    ]
    
    # Allowlist patterns that are safe despite containing keywords
    ALLOWLIST_PATTERNS = [
        r"how to drop table",  # Educational question
        r"what is drop table",  # Educational question
        r"explain.*drop.*table",  # Educational question
        r"tutorial.*sql",  # Tutorial context
    ]
    
    def __init__(self, enabled: bool = True):
        """
        Initialize sanitizer
        
        Args:
            enabled: Whether sanitization is enabled (default: True)
        """
        self.enabled = enabled
        self.compiled_patterns = [
            (re.compile(pattern, re.IGNORECASE), name)
            for pattern, name in self.DANGEROUS_PATTERNS
        ]
        self.compiled_allowlist = [
            re.compile(pattern, re.IGNORECASE)
            for pattern in self.ALLOWLIST_PATTERNS
        ]
    
    async def sanitize_prompt(self, prompt: str) -> SanitizationResult:
        """
        Sanitize a prompt before sending to AI
        
        Args:
            prompt: The prompt to sanitize
            
        Returns:
            SanitizationResult with safety assessment
        """
        if not self.enabled:
            return SanitizationResult(
                is_safe=True,
                confidence=1.0,
                blocked_patterns=[],
                safe_prompt=prompt,
                original_prompt=prompt
            )
        
        # Check for empty or suspicious input
        if not prompt or len(prompt.strip()) == 0:
            logger.warning("Empty prompt detected")
            return SanitizationResult(
                is_safe=False,
                confidence=0.0,
                blocked_patterns=["empty_prompt"],
                safe_prompt=None,
                original_prompt=prompt
            )
        
        # Check if prompt is too long (potential DoS)
        if len(prompt) > 10000:
            logger.warning(f"Excessively long prompt detected: {len(prompt)} chars")
            return SanitizationResult(
                is_safe=False,
                confidence=0.1,
                blocked_patterns=["excessive_length"],
                safe_prompt=None,
                original_prompt=prompt[:100] + "..."
            )
        
        # Check allowlist first (educational/safe contexts)
        for allowlist_pattern in self.compiled_allowlist:
            if allowlist_pattern.search(prompt):
                logger.info(f"Prompt matched allowlist: {prompt[:50]}...")
                return SanitizationResult(
                    is_safe=True,
                    confidence=0.95,
                    blocked_patterns=[],
                    safe_prompt=prompt,
                    original_prompt=prompt
                )
        
        # Check for dangerous patterns
        blocked_patterns = []
        for pattern, name in self.compiled_patterns:
            if pattern.search(prompt):
                blocked_patterns.append(name)
        
        # Calculate confidence based on number of blocked patterns
        if blocked_patterns:
            confidence = max(0.0, 1.0 - (len(blocked_patterns) * 0.3))
            logger.warning(
                f"Blocked malicious prompt: {prompt[:100]}...",
                extra={
                    "blocked_patterns": blocked_patterns,
                    "confidence": confidence
                }
            )
            return SanitizationResult(
                is_safe=False,
                confidence=confidence,
                blocked_patterns=blocked_patterns,
                safe_prompt=None,
                original_prompt=prompt
            )
        
        # Prompt is safe
        return SanitizationResult(
            is_safe=True,
            confidence=0.95,
            blocked_patterns=[],
            safe_prompt=prompt,
            original_prompt=prompt
        )
    
    async def sanitize_log(self, log: Dict) -> SanitizedLog:
        """
        Sanitize a log entry before AI analysis
        
        Args:
            log: Log entry as dictionary
            
        Returns:
            SanitizedLog with safety assessment
        """
        # Extract message from log
        message = log.get("message", "") or log.get("msg", "") or str(log)
        
        # Sanitize the message
        result = await self.sanitize_prompt(message)
        
        return SanitizedLog(
            original=log,
            safe_for_llm=result.is_safe,
            confidence=result.confidence,
            timestamp=datetime.utcnow(),
            blocked_patterns=result.blocked_patterns
        )
    
    def get_stats(self) -> Dict:
        """
        Get sanitizer statistics
        
        Returns:
            Dictionary with sanitizer stats
        """
        return {
            "enabled": self.enabled,
            "total_patterns": len(self.DANGEROUS_PATTERNS),
            "allowlist_patterns": len(self.ALLOWLIST_PATTERNS),
        }
