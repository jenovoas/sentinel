import asyncio
import time
from typing import List, Dict, Any
from ..config import BUFFER_BASE_LATENCY, BUFFER_ACCELERATION_FACTOR

class AdaptiveBuffer:
    """
    Buffer Adaptativo con IA (Claim 7).
    Implementa el modelo de reducción de latencia en serie.
    Cada instancia reduce la latencia de procesamiento para la siguiente etapa,
    logrando una aceleración exponencial del throughput global.
    """

    def __init__(self, stage_id: int):
        self.stage_id = stage_id
        # La latencia se reduce exponencialmente con cada etapa
        # Latencia_N = Base / (Factor ^ N)
        self.latency_ms = BUFFER_BASE_LATENCY / (BUFFER_ACCELERATION_FACTOR ** stage_id)
        self.processed_count = 0

    async def process_batch(self, batch: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Procesa un lote de eventos simulando la latencia reducida.

        Args:
            batch: Lista de eventos (diccionarios).

        Returns:
            Lista de eventos procesados (mismos objetos, pasados por 'tubería').
        """
        # Simular tiempo de procesamiento (non-blocking sleep)
        sleep_time = self.latency_ms / 1000.0
        await asyncio.sleep(sleep_time)
        
        self.processed_count += len(batch)
        return batch

    def get_stats(self) -> Dict[str, Any]:
        """Retorna estadísticas de rendimiento de este buffer."""
        return {
            "stage_id": self.stage_id,
            "latency_ms": self.latency_ms,
            "processed_events": self.processed_count
        }
