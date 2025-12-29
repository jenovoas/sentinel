import time
from ..config import AI_MODEL_NAME, AI_LATENCY_SIMULATION

class SentinelBrain:
    """
    Cerebro de Sentinel Cortex.
    Responsable de tomar decisiones de seguridad basadas en contexto.
    Actualmente usa una simulación (Mock), pero está diseñado para
    conectarse a Ollama/Llama3 en el futuro.
    """

    def __init__(self):
        print(f"🧠 [SentinelBrain] Inicializando modelo: {AI_MODEL_NAME}")

    def analyze_threat(self, filename: str) -> bool:
        """
        Analiza un nombre de archivo/comando para determinar si es malicioso.

        Args:
            filename (str): El nombre del binario o comando bloqueado.

        Returns:
            bool: True si debe ser PERMITIDO (Whitelist), False si debe seguir BLOQUEADO.
        """
        # Simular latencia de inferencia (pensamiento de la IA)
        time.sleep(AI_LATENCY_SIMULATION)

        # Lógica de Detección (Mock para PoC)
        # En el futuro, esto será una llamada a: ollama.generate(prompt=...)
        
        if "safe" in filename or "deploy" in filename:
            # Contexto: Nombres que implican operaciones seguras o despliegues
            return True
            
        if "malware" in filename or "attack" in filename:
            # Contexto: Amenazas obvias
            return False
            
        # Por defecto: Ante la duda, mantener el bloqueo (Zero Trust)
        return False
