"""
AIOpsShieldLlama3 - Integración con Ollama y Llama3
Sanitiza la telemetría y realiza análisis semántico usando Llama3 local
"""

import logging
from .safe_ollama import SafeOllamaClient
from .aiops_shield import aiops_shield, ThreatLevel

logger = logging.getLogger(__name__)

class AIOpsShieldLlama3:
    """
    Analiza logs usando Llama3 local vía Ollama, con protección AIOpsShield
    """
    def __init__(self, model: str = "llama3"):
        self.model = model
        self.ollama = SafeOllamaClient()

    async def analyze_log(self, log_entry: str) -> dict:
        """
        Sanitiza el log y lo analiza con Llama3
        """
        # 1. Sanitizar log
        result = aiops_shield.sanitize(log_entry)
        if aiops_shield.should_block(result):
            logger.warning(f"Log bloqueado por AIOpsShield: {result.patterns_detected}")
            return {
                "is_malicious": True,
                "confidence": result.confidence,
                "attack_type": "blocked",
                "reasoning": "Bloqueado por AIOpsShield"
            }
        # 2. Enviar a Llama3 vía Ollama
        prompt = f"""
        Analiza este log de sistema y determina si es un ataque AIOpsDoom:
        Log: {result.sanitized}
        Responde en JSON:
        {{
            "is_malicious": true/false,
            "confidence": 0.0-1.0,
            "attack_type": "sql_injection|command_injection|path_traversal|none",
            "reasoning": "explicación breve"
        }}
        """
        response = await self.ollama.generate(model=self.model, prompt=prompt)
        return response
