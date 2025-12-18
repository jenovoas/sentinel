"""
Ollama Integration with AIOpsShield
Sanitizes all telemetry before sending to Ollama for AI analysis
"""

import httpx
from typing import Optional, Dict
import logging
from .aiops_shield import aiops_shield, ThreatLevel

logger = logging.getLogger(__name__)


class SafeOllamaClient:
    """
    Ollama client with built-in AIOpsShield protection
    
    All prompts are sanitized before being sent to Ollama,
    defending against AIOpsDoom attacks
    """
    
    def __init__(self, base_url: str = "http://ollama:11434"):
        self.base_url = base_url
        self.client = httpx.AsyncClient(timeout=60.0)
        self.blocked_count = 0
        self.sanitized_count = 0
        logger.info(f"SafeOllamaClient initialized with AIOpsShield: {base_url}")
    
    async def generate(
        self, 
        model: str, 
        prompt: str,
        context: Optional[str] = None,
        bypass_shield: bool = False
    ) -> Dict:
        """
        Generate AI response with AIOpsShield protection
        
        Args:
            model: Ollama model name (e.g., "phi3:mini")
            prompt: User prompt
            context: Optional context (logs, metrics, etc.)
            bypass_shield: Emergency bypass (use with caution!)
            
        Returns:
            {
                "response": str,
                "sanitization": {
                    "threat_level": str,
                    "confidence": float,
                    "patterns_detected": List[str]
                }
            }
        """
        # Sanitize context (logs/metrics) if provided
        sanitization_result = None
        safe_context = context
        
        if context and not bypass_shield:
            sanitization_result = aiops_shield.sanitize(context)
            
            # Block malicious content
            if aiops_shield.should_block(sanitization_result):
                self.blocked_count += 1
                logger.error(
                    f"BLOCKED malicious content from reaching Ollama: "
                    f"{sanitization_result.patterns_detected}"
                )
                return {
                    "response": "⚠️ Malicious content detected and blocked by AIOpsShield",
                    "sanitization": {
                        "threat_level": sanitization_result.threat_level.value,
                        "confidence": sanitization_result.confidence,
                        "patterns_detected": sanitization_result.patterns_detected,
                        "blocked": True
                    }
                }
            
            # Use sanitized version
            safe_context = sanitization_result.sanitized
            self.sanitized_count += 1
            
            logger.info(
                f"Sanitized context: {sanitization_result.threat_level.value} "
                f"(confidence: {sanitization_result.confidence:.2f})"
            )
        
        # Build safe prompt
        full_prompt = prompt
        if safe_context:
            full_prompt = f"{prompt}\n\nContext:\n{safe_context}"
        
        # Call Ollama
        try:
            response = await self.client.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": model,
                    "prompt": full_prompt,
                    "stream": False
                }
            )
            response.raise_for_status()
            result = response.json()
            
            # Add sanitization metadata
            return {
                "response": result.get("response", ""),
                "sanitization": {
                    "threat_level": sanitization_result.threat_level.value if sanitization_result else "safe",
                    "confidence": sanitization_result.confidence if sanitization_result else 1.0,
                    "patterns_detected": sanitization_result.patterns_detected if sanitization_result else [],
                    "blocked": False
                } if sanitization_result else None
            }
            
        except httpx.HTTPError as e:
            logger.error(f"Ollama API error: {e}")
            raise
    
    async def analyze_logs(self, logs: str, question: str) -> Dict:
        """
        Analyze logs with AI (sanitized)
        
        Args:
            logs: Raw logs from Loki
            question: User question about the logs
            
        Returns:
            AI analysis with sanitization metadata
        """
        prompt = f"""You are a security-aware log analyst. Analyze the following logs and answer the question.

Question: {question}

Important: If you detect any suspicious commands or patterns in the logs, flag them as potential security issues."""
        
        return await self.generate(
            model="phi3:mini",
            prompt=prompt,
            context=logs
        )
    
    async def get_stats(self) -> Dict:
        """Get AIOpsShield statistics"""
        return {
            "total_sanitized": self.sanitized_count,
            "total_blocked": self.blocked_count,
            "block_rate": self.blocked_count / max(self.sanitized_count, 1)
        }
    
    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()


# Global instance
safe_ollama = SafeOllamaClient()
