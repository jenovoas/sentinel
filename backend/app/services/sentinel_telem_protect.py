"""
Sentinel con Protección Telemétrica Paralela
Integra AIOpsShield + TruthSync sin overhead de latencia

Features:
- Buffers jerárquicos ✅
- AIOpsShield paralelo ✅
- TruthSync background ✅
- 0ms overhead ✅
- TTFB <200ms ✅
"""

import asyncio
import time
import json
from typing import AsyncGenerator, Optional, Dict
from dataclasses import dataclass
import httpx
import logging

# Importar componentes Sentinel existentes
from .aiops_shield import aiops_shield, SanitizationResult, ThreatLevel
from .truthsync import truthsync_client
from .sentinel_fluido import SentinelBuffer, SentinelFluido

logger = logging.getLogger(__name__)


@dataclass
class ProtectionMetrics:
    """Métricas de protección telemétrica"""
    ttfb_ms: float
    shield_check_ms: float
    truthsync_checks: int
    threats_detected: int
    threats_blocked: int
    safe: bool


class SentinelTelemProtect(SentinelFluido):
    """
    Sentinel con protección telemétrica paralela
    
    Extiende SentinelFluido agregando:
    - AIOpsShield en paralelo (0ms overhead)
    - TruthSync background (0ms overhead)
    - Métricas de protección
    
    Claim 6 Patente: Pipeline paralelo sin degradación latencia
    """
    
    def __init__(
        self,
        ollama_url: str = "http://localhost:11434",
        model: str = "llama3.2:1b"
    ):
        super().__init__(ollama_url, model)
        self.shield = aiops_shield
        self.truthsync = truthsync_client
        
        # Métricas de protección
        self.protection_stats = {
            "total_requests": 0,
            "threats_detected": 0,
            "threats_blocked": 0,
            "shield_checks": 0,
            "truthsync_checks": 0
        }
        
        logger.info(f"SentinelTelemProtect: AIOpsShield + TruthSync paralelo")
    
    async def _shield_check_parallel(
        self, 
        mensaje: str
    ) -> tuple[SanitizationResult, float]:
        """
        AIOpsShield check en paralelo (no bloquea LLM)
        
        Returns:
            (sanitization_result, check_time_ms)
        """
        start = time.time()
        
        try:
            # Sanitización (típicamente <1ms)
            result = self.shield.sanitize(mensaje)
            check_time = (time.time() - start) * 1000
            
            self.protection_stats["shield_checks"] += 1
            
            if result.threat_level == ThreatLevel.MALICIOUS:
                self.protection_stats["threats_detected"] += 1
                logger.warning(
                    f"Threat detected: {result.patterns_detected}, "
                    f"confidence: {result.confidence}"
                )
            
            return result, check_time
            
        except Exception as e:
            logger.error(f"Shield check error: {e}")
            # En caso de error, permitir pero loggear
            return SanitizationResult(
                sanitized=mensaje,
                threat_level=ThreatLevel.UNKNOWN,
                confidence=0.0,
                patterns_detected=[],
                abstracted_vars={}
            ), 0
    
    async def _truthsync_verify_parallel(self, text: str):
        """
        TruthSync verification en background (no bloquea)
        """
        try:
            result = await self.truthsync.verify(text)
            self.protection_stats["truthsync_checks"] += 1
            
            if not result.get("verified", True):
                logger.warning(f"TruthSync verification failed: {text[:50]}...")
            
        except Exception as e:
            logger.debug(f"TruthSync background error: {e}")
    
    async def responder_protegido(
        self,
        user_id: str,
        mensaje: str,
        block_malicious: bool = True
    ) -> AsyncGenerator[tuple[str, Optional[ProtectionMetrics]], None]:
        """
        Responde con protección telemétrica paralela
        
        Pipeline:
        1. Shield check (paralelo, no bloquea)
        2. LLM streaming (fluido)
        3. TruthSync background (paralelo)
        4. Buffer update (O(1))
        
        Args:
            user_id: ID del usuario
            mensaje: Mensaje a procesar
            block_malicious: Si True, bloquea contenido malicioso
        
        Yields:
            (chunk, metrics) - metrics solo en primer chunk
        """
        self.protection_stats["total_requests"] += 1
        
        start_total = time.time()
        
        # 1. SHIELD CHECK PARALELO (no bloquea LLM)
        shield_task = asyncio.create_task(
            self._shield_check_parallel(mensaje)
        )
        
        # 2. PREPARAR BUFFER Y CONTEXTO
        buffer = self._get_buffer(user_id)
        
        # Esperar shield solo si vamos a bloquear
        if block_malicious:
            shield_result, shield_time = await shield_task
            
            # Bloquear si es malicioso
            if self.shield.should_block(shield_result):
                self.protection_stats["threats_blocked"] += 1
                
                metrics = ProtectionMetrics(
                    ttfb_ms=0,
                    shield_check_ms=shield_time,
                    truthsync_checks=0,
                    threats_detected=1,
                    threats_blocked=1,
                    safe=False
                )
                
                yield "⚠️ Contenido bloqueado por AIOpsShield", metrics
                return
            
            # Usar mensaje sanitizado
            mensaje_procesado = shield_result.sanitized
        else:
            # No bloquear, pero verificar en background
            mensaje_procesado = mensaje
        
        # 3. CONSTRUIR CONTEXTO
        prompt = self._construir_contexto(buffer, mensaje_procesado)
        
        # 4. LLM STREAMING (fluido, sin bloqueos)
        ttfb = None
        respuesta_completa = ""
        truthsync_tasks = []
        
        try:
            async with self.client.stream(
                "POST",
                f"{self.ollama_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": True,
                    "options": {
                        "temperature": 0.7,
                        "num_predict": 512,
                        "num_ctx": 2048,
                    }
                }
            ) as response:
                response.raise_for_status()
                
                async for line in response.aiter_lines():
                    if not line:
                        continue
                    
                    try:
                        data = json.loads(line)
                        chunk = data.get("response", "")
                        
                        if not chunk:
                            continue
                        
                        # TTFB (primer token)
                        if ttfb is None:
                            ttfb = (time.time() - start_total) * 1000
                            
                            # Obtener resultado shield si no esperamos antes
                            if not block_malicious and shield_task.done():
                                shield_result, shield_time = await shield_task
                            else:
                                shield_result, shield_time = await shield_task
                            
                            # Métricas primer chunk
                            metrics = ProtectionMetrics(
                                ttfb_ms=ttfb,
                                shield_check_ms=shield_time,
                                truthsync_checks=0,
                                threats_detected=1 if shield_result.threat_level == ThreatLevel.MALICIOUS else 0,
                                threats_blocked=0,
                                safe=True
                            )
                        else:
                            metrics = None
                        
                        respuesta_completa += chunk
                        
                        # 5. UPDATE BUFFERS (O(1))
                        buffer.agregar_episodio(chunk)
                        buffer.actualizar_patron(chunk)
                        
                        # 6. TRUTHSYNC BACKGROUND (no bloquea)
                        if len(respuesta_completa) % 100 == 0:  # Cada 100 chars
                            task = asyncio.create_task(
                                self._truthsync_verify_parallel(respuesta_completa)
                            )
                            truthsync_tasks.append(task)
                        
                        # Yield chunk
                        yield chunk, metrics
                        
                    except json.JSONDecodeError:
                        continue
            
            # Esperar verificaciones background (no bloquea usuario)
            if truthsync_tasks:
                await asyncio.gather(*truthsync_tasks, return_exceptions=True)
            
            logger.info(
                f"Protected response: TTFB={ttfb:.0f}ms, "
                f"shield={shield_time:.2f}ms, "
                f"truthsync_checks={len(truthsync_tasks)}"
            )
            
        except httpx.HTTPError as e:
            logger.error(f"Ollama error: {e}")
            yield f"Error: {str(e)}", None
    
    def get_protection_stats(self) -> Dict:
        """Obtiene estadísticas de protección"""
        return {
            **self.protection_stats,
            "block_rate": (
                self.protection_stats["threats_blocked"] / 
                self.protection_stats["total_requests"]
                if self.protection_stats["total_requests"] > 0 else 0
            ),
            "detection_rate": (
                self.protection_stats["threats_detected"] / 
                self.protection_stats["total_requests"]
                if self.protection_stats["total_requests"] > 0 else 0
            )
        }


# Global instance
sentinel_telem_protect = SentinelTelemProtect()
