"""
Sentinel Optimized - ML Buffer System
Adaptado para GTX 1050 (3GB VRAM) con métricas reales medibles

OBJETIVO: Demostrar mejoras reales en latencia y throughput
Hardware: GTX 1050, 3GB VRAM, CPU disponible
"""

import asyncio
import time
from typing import AsyncGenerator, Dict, List, Optional
from dataclasses import dataclass
from statistics import mean, quantiles
import httpx
import logging

# Importar componentes Sentinel existentes
from .aiops_shield import aiops_shield, SanitizationResult
from .truthsync import truthsync_client

logger = logging.getLogger(__name__)


@dataclass
class LatencyMetrics:
    """Métricas de latencia para documentación de patente"""
    ttfb_ms: float
    token_rate_ms: float
    total_time_ms: float
    tokens_generated: int
    cache_hit: bool
    sanitized: bool
    
    def is_human_like(self) -> bool:
        """Valida si cumple estándares humanos"""
        return self.ttfb_ms < 200 and self.token_rate_ms < 250


class HierarchicalBuffers:
    """
    Buffers jerárquicos optimizados para latencia mínima
    
    - Episódico: Últimos N mensajes (memoria corto plazo)
    - Patrones: Frecuencias y patterns (memoria largo plazo)
    - Predictivo: ML predictions (anticipación)
    """
    
    def __init__(self, max_episodic: int = 100):
        self.episodico: List[str] = []
        self.patrones: Dict[str, int] = {}
        self.predictivo: List[str] = []
        self.max_episodic = max_episodic
    
    def update_episodic(self, text: str):
        """O(1) append con límite"""
        self.episodico.append(text)
        if len(self.episodico) > self.max_episodic:
            self.episodico.pop(0)
    
    def update_patterns(self, text: str):
        """O(1) update de frecuencias"""
        # Usar primeros 10 chars como key (simplificado)
        key = text[:10] if len(text) >= 10 else text
        self.patrones[key] = self.patrones.get(key, 0) + 1
    
    def get_context(self, limit: int = 3) -> str:
        """Obtiene contexto relevante para prompt"""
        recent = self.episodico[-limit:] if self.episodico else []
        return " ".join(recent)


class SentinelOptimized:
    """
    Sentinel Optimizado para GTX 1050 (3GB VRAM)
    
    Estrategia:
    1. Usar Ollama local (ya instalado) en lugar de vLLM (requiere más VRAM)
    2. Implementar buffers jerárquicos
    3. ML predictor simple (heurísticos + patterns)
    4. Medir latencias reales
    
    Target: TTFB <200ms, token-rate <250ms
    """
    
    def __init__(
        self,
        ollama_url: str = "http://localhost:11434",
        model: str = "phi3:mini"  # Optimizado para 3GB VRAM
    ):
        self.ollama_url = ollama_url
        self.model = model
        self.client = httpx.AsyncClient(timeout=60.0)
        
        # Componentes Sentinel
        self.shield = aiops_shield
        self.truthsync = truthsync_client
        
        # Buffers jerárquicos por usuario
        self.buffers: Dict[str, HierarchicalBuffers] = {}
        
        # Métricas para patente
        self.metrics: List[LatencyMetrics] = []
        
        logger.info(f"SentinelOptimized initialized: {ollama_url} / {model}")
    
    def _get_buffer(self, user_id: str) -> HierarchicalBuffers:
        """Obtiene o crea buffer para usuario"""
        if user_id not in self.buffers:
            self.buffers[user_id] = HierarchicalBuffers()
        return self.buffers[user_id]
    
    async def _probe_pruning(
        self, 
        user_id: str, 
        mensaje: str
    ) -> str:
        """
        ML Probe Pruning - Selecciona contexto óptimo
        
        Versión simplificada para hardware limitado:
        - Heurísticos en lugar de modelo ML pesado
        - Lookup en buffers O(1)
        - Target: <10ms latency
        """
        buffer = self._get_buffer(user_id)
        
        # Contexto episódico (últimos 3 mensajes)
        context = buffer.get_context(limit=3)
        
        # Patrones relevantes (simplificado)
        key = mensaje[:10] if len(mensaje) >= 10 else mensaje
        pattern_freq = buffer.patrones.get(key, 0)
        
        # Construir prompt optimizado
        if context:
            return f"Context: {context}\n\nUser: {mensaje}"
        else:
            return f"User: {mensaje}"
    
    async def generate_optimized(
        self,
        user_id: str,
        mensaje: str,
        stream: bool = True
    ) -> AsyncGenerator[tuple[str, Optional[LatencyMetrics]], None]:
        """
        Generación optimizada con métricas reales
        
        Flujo:
        1. AIOpsShield (sanitización <1ms)
        2. Probe Pruning (<10ms)
        3. Ollama streaming (TTFB objetivo <200ms)
        4. Buffer update (<1ms)
        5. TruthSync background (no bloquea)
        
        Yields:
            (chunk, metrics) - metrics solo en primer chunk
        """
        start_total = time.time()
        
        # 1. SANITIZACIÓN (AIOpsShield)
        sanitization = self.shield.sanitize(mensaje)
        if self.shield.should_block(sanitization):
            logger.warning(f"Blocked malicious content: {sanitization.patterns_detected}")
            yield "⚠️ Contenido bloqueado por AIOpsShield", None
            return
        
        mensaje_sanitizado = sanitization.sanitized
        t_sanitize = (time.time() - start_total) * 1000
        logger.debug(f"Sanitization: {t_sanitize:.2f}ms")
        
        # 2. PROBE PRUNING (ML predictor simple)
        start_probe = time.time()
        prompt = await self._probe_pruning(user_id, mensaje_sanitizado)
        t_probe = (time.time() - start_probe) * 1000
        logger.debug(f"Probe pruning: {t_probe:.2f}ms")
        
        # 3. OLLAMA STREAMING (optimizado)
        try:
            response = await self.client.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": stream,
                    "options": {
                        "temperature": 0.7,
                        "num_predict": 512,
                        # Optimizaciones para latencia
                        "num_ctx": 2048,  # Reducir context window
                        "num_batch": 128,  # Batch size optimizado
                    }
                },
                timeout=60.0
            )
            response.raise_for_status()
            
            respuesta_completa = ""
            first_chunk = True
            ttfb = None
            chunk_times = []
            
            # Streaming de respuesta
            async for line in response.aiter_lines():
                if not line:
                    continue
                
                try:
                    import json
                    data = json.loads(line)
                    chunk = data.get("response", "")
                    
                    if not chunk:
                        continue
                    
                    # TTFB (crítico para patente)
                    if first_chunk:
                        ttfb = (time.time() - start_total) * 1000
                        logger.info(f"TTFB: {ttfb:.0f}ms")
                        first_chunk = False
                    
                    chunk_times.append(time.time())
                    respuesta_completa += chunk
                    
                    # 4. UPDATE BUFFERS (O(1))
                    buffer = self._get_buffer(user_id)
                    buffer.update_episodic(chunk)
                    buffer.update_patterns(chunk)
                    
                    # Yield chunk
                    yield chunk, None
                    
                    # 5. TRUTHSYNC BACKGROUND (no bloquea)
                    if len(respuesta_completa) % 50 == 0:  # Cada 50 chars
                        asyncio.create_task(
                            self._verify_background(respuesta_completa)
                        )
                    
                except json.JSONDecodeError:
                    continue
            
            # Calcular métricas finales
            total_time = (time.time() - start_total) * 1000
            
            # Token rate (aproximado)
            if len(chunk_times) > 1:
                token_rate = mean([
                    (chunk_times[i+1] - chunk_times[i]) * 1000
                    for i in range(len(chunk_times) - 1)
                ])
            else:
                token_rate = 0
            
            # Guardar métricas
            metrics = LatencyMetrics(
                ttfb_ms=ttfb or 0,
                token_rate_ms=token_rate,
                total_time_ms=total_time,
                tokens_generated=len(respuesta_completa.split()),
                cache_hit=False,  # Ollama no expone esto
                sanitized=True
            )
            self.metrics.append(metrics)
            
            logger.info(
                f"Completed: TTFB={ttfb:.0f}ms, "
                f"token_rate={token_rate:.0f}ms, "
                f"total={total_time:.0f}ms, "
                f"human_like={metrics.is_human_like()}"
            )
            
        except httpx.HTTPError as e:
            logger.error(f"Ollama error: {e}")
            yield f"Error: {str(e)}", None
    
    async def _verify_background(self, text: str):
        """Verificación TruthSync en background (no bloquea)"""
        try:
            await self.truthsync.verify(text)
        except Exception as e:
            logger.debug(f"Background verification failed: {e}")
    
    def get_patent_metrics(self) -> Dict:
        """
        Exporta métricas para documentación de patente
        
        Returns:
            Dict con p95, mean, y cumplimiento de targets
        """
        if not self.metrics:
            return {"error": "No metrics collected"}
        
        ttfb_values = [m.ttfb_ms for m in self.metrics if m.ttfb_ms > 0]
        token_rate_values = [m.token_rate_ms for m in self.metrics if m.token_rate_ms > 0]
        
        if not ttfb_values:
            return {"error": "No valid TTFB metrics"}
        
        # Calcular p95
        ttfb_p95 = quantiles(ttfb_values, n=20)[-1] if len(ttfb_values) > 20 else max(ttfb_values)
        token_rate_mean = mean(token_rate_values) if token_rate_values else 0
        
        # Contar cuántos cumplen estándar humano
        human_like_count = sum(1 for m in self.metrics if m.is_human_like())
        human_like_pct = (human_like_count / len(self.metrics)) * 100
        
        return {
            "total_requests": len(self.metrics),
            "ttfb_p95_ms": round(ttfb_p95, 2),
            "ttfb_mean_ms": round(mean(ttfb_values), 2),
            "token_rate_mean_ms": round(token_rate_mean, 2),
            "human_like_percentage": round(human_like_pct, 2),
            "target_ttfb_ms": 200,
            "target_token_rate_ms": 250,
            "meets_ttfb_target": ttfb_p95 < 200,
            "meets_token_rate_target": token_rate_mean < 250,
            "meets_human_standard": human_like_pct > 80
        }
    
    def export_metrics_csv(self, filename: str = "sentinel_metrics.csv"):
        """Exporta métricas a CSV para análisis"""
        import csv
        
        with open(filename, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                "ttfb_ms", "token_rate_ms", "total_time_ms",
                "tokens_generated", "human_like"
            ])
            
            for m in self.metrics:
                writer.writerow([
                    m.ttfb_ms,
                    m.token_rate_ms,
                    m.total_time_ms,
                    m.tokens_generated,
                    m.is_human_like()
                ])
        
        logger.info(f"Metrics exported to {filename}")
    
    async def close(self):
        """Cleanup"""
        await self.client.aclose()


# Global instance
sentinel_optimized = SentinelOptimized()
