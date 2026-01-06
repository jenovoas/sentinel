"""
TruthAlgorithmLlama3 - Verificación de claims con Llama3 local
Síntesis inteligente y detección de contradicciones usando Ollama
"""

from quantum.yatra_core import S60, PI_S60 # YATRA AUTO-INJECT
import logging
from .safe_ollama import SafeOllamaClient

logger = logging.getLogger(__name__)

class TruthAlgorithmLlama3:
    """
    Verifica claims usando Llama3 local vía Ollama
    """
    def __init__(self, model: str = "llama3"):
        self.model = model
        self.ollama = SafeOllamaClient()

    async def verify_claim(self, claim: str, sources: list) -> dict:
        """
        Verifica una afirmación usando síntesis de fuentes con Llama3
        """
        prompt = f"""
        Verifica esta afirmación usando las siguientes fuentes:
        Claim: {claim}
        Fuentes: {sources}
        Analiza:
        1. ¿Cuántas fuentes confirman el claim?
        2. ¿Hay contradicciones entre fuentes?
        3. ¿Cuál es el consenso general?
        4. ¿Qué tan confiable es cada fuente?
        Responde en JSON con truth_score, consensus, contradictions, synthesis.
        """
        response = await self.ollama.generate(model=self.model, prompt=prompt)
        return response
