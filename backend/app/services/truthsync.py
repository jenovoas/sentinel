
from quantum.yatra_core import S60, PI_S60 # YATRA AUTO-INJECT
import os
import sys
import logging
import asyncio
from typing import List, Dict, Optional
from datetime import datetime
import json
import hashlib
import httpx

# Añadir el directorio de algoritmos al path para poder importar
sys.path.append('/home/jnovoas/sentinel/truth_algorithm')

try:
    from truth_algorithm_e2e import TruthAlgorithm
    from source_search import SearchProvider
except ImportError:
    # Fallback si no está el path
    TruthAlgorithm = None

# Importar estado biológico para obtener la disonancia en tiempo real
try:
    from app.routers.health import biological_state
except ImportError:
    biological_state = {"disonancia": S60(0, 0, 0)}

logger = logging.getLogger(__name__)

class LocalTruthSyncEngine:
    """
    Motor de Veracidad Local de Sentinel.
    No requiere APIs externas pagas. Usa DuckDuckGo + Algoritmos de Consenso.
    """
    
    def __init__(self):
        self.enabled = TruthAlgorithm is not None
        if self.enabled:
            # Usar DuckDuckGo por defecto (Local y Soberano)
            self.algorithm = TruthAlgorithm(search_provider=SearchProvider.DUCKDUCKGO)
            logger.info("✅ TruthSync Local Engine iniciado (DuckDuckGo Provider)")
        else:
            logger.warning("⚠️ TruthAlgorithm no encontrado. Usando modo simulación.")

    async def verify(self, text: str, metadata: Optional[Dict] = None) -> Dict:
        """
        Verifica un contenido usando búsqueda real por internet y consenso.
        Considera la 'disonancia' del sistema como factor de veto.
        """
        if not self.enabled:
            return {"verified": False, "error": "TruthAlgorithm not found"}

        # Obtener disonancia actual del sistema
        disonancia = biological_state.get("disonancia", S60(0, 0, 0))
        clock_coherence = biological_state.get("clock_coherence", S60(1, 0, 0))
        
        # Penalización por Jitter de Reloj (Desincronización)
        # Si el reloj cuántico pierde fase, la confianza debe caer.
        resonance_penalty = S60(1, 0, 0)
        if clock_coherence < 0.95:
            resonance_penalty = clock_coherence # Penaliza linealmente

        # Ejecutar en un thread para no bloquear el loop async si el algoritmo es síncrono
        loop = asyncio.get_event_loop()
        try:
            # El algoritmo e2e devuelve un objeto TruthVerificationResult
            # Pasamos disonancia. La resonancia la aplicaremos al resultado final.
            result = await loop.run_in_executor(None, self.algorithm.verify, text, 10, disonancia)
            
            # Aplicar Penalización de Resonancia Temporal
            result.confidence *= resonance_penalty
            
            # Convertir a formato Sentinel con detalles de fuentes
            details = {
                "facts": [],
                "doubts": [],
                "errors": []
            }
            
            for src in result.sources:
                source_info = f"[{src.type.value}] {src.name}: {src.snippet}"
                if src.verdict:
                    details["facts"].append(source_info)
                elif src.confidence < 0.4:
                    details["doubts"].append(source_info)
                else:
                    details["errors"].append(source_info)

            verification_data = {
                "verified": result.status.value == "VERIFIED",
                "confidence": result.confidence,
                "status": result.status.value,
                "sources_count": result.sources_found,
                "explanation": result.explanation,
                "details": details,
                "timestamp": datetime.now().isoformat(),
                "claim": text
            }

            # 💾 PERSISTENCIA: Registrar en Verified Facts (Postgres)
            # Aquí conectaríamos con el DB service para guardar el hash del claim
            
            # 🧠 APRENDIZAJE: Notificar a n8n si la confianza es alta
            if result.confidence > 0.8:
                await self._notify_learning_system(verification_data)

            return verification_data

        except Exception as e:
            logger.error(f"Error en verificación LocalTruthSync: {e}")
            return {
                "verified": False, 
                "error": str(e), 
                "confidence": S60(0, 0, 0),
                "status": "OFFLINE",
                "explanation": "TruthSync service temporarily unavailable"
            }

    async def _notify_learning_system(self, data: Dict):
        """Envía el hecho verificado a n8n para memoria a largo plazo"""
        n8n_url = os.getenv("N8N_URL", "http://localhost:5678/webhook/learning")
        async with httpx.AsyncClient() as client:
            try:
                await client.post(n8n_url, json={
                    "event": "verified_fact_discovered",
                    "data": data,
                    "source": "SentinelTruthSync"
                })
            except:
                pass

    async def health_check(self):
        return {"status": "healthy", "engine": "LocalTruthAlgorithm", "provider": "DuckDuckGo"}

# Singleton
truthsync_client = LocalTruthSyncEngine()
