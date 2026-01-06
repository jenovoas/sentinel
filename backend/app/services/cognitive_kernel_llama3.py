"""
CognitiveKernelLlama3 - Evaluación de comandos y patrones anómalos con Llama3 local
Integración con eBPF LSM y análisis contextual usando Ollama
"""

from quantum.yatra_core import S60, PI_S60 # YATRA AUTO-INJECT
import logging
from .safe_ollama import SafeOllamaClient

logger = logging.getLogger(__name__)

class CognitiveKernelLlama3:
    """
    Evalúa comandos y contexto de sistema usando Llama3 local vía Ollama
    """
    def __init__(self, model: str = "llama3"):
        self.model = model
        self.ollama = SafeOllamaClient()

    async def evaluate_context(self, context: dict) -> dict:
        """
        Evalúa el contexto de seguridad antes de permitir execve
        """
        prompt = f"""
        Evalúa el siguiente contexto de sistema:
        Usuario: {context.get('user')}
        Hora: {context.get('time')}
        Comandos previos: {context.get('previous_commands')}
        Estado del sistema: {context.get('system_state')}
        Evalúa:
        1. ¿Es malicioso o sospechoso?
        2. ¿Es apropiado para este usuario?
        3. ¿Es apropiado para esta hora?
        4. ¿Hay patrones anómalos?
        Responde en JSON con allow, confidence, risk_level, reasoning.
        """
        response = await self.ollama.generate(model=self.model, prompt=prompt)
        return response
