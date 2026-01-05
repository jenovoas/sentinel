#!/usr/bin/env python3
"""
TruthSync Dual Architecture Orchestrator
Coordina Edge + Core para latencia óptima
"""

import asyncio
import logging
import time
from typing import Dict, Optional
from dataclasses import dataclass
import aioredis
import json

logger = logging.getLogger(__name__)

@dataclass
class PerformanceMetrics:
    """Métricas de rendimiento del sistema dual"""
    edge_latency_p95: float = 0.0
    core_latency_p95: float = 0.0
    cache_hit_rate: float = 0.0
    queue_depth: int = 0
    throughput_qps: float = 0.0

class TruthSyncOrchestrator:
    """
    Orquestador de la arquitectura dual TruthSync:
    - Edge: Cache predictivo <10ms
    - Core: Verificación completa con ML
    - Optimización dinámica de routing
    """
    
    def __init__(self, 
                 edge_url: str = "http://truthsync-edge:8001",
                 core_workers: int = 4,
                 redis_url: str = "redis://redis:6379"):
        self.edge_url = edge_url
        self.core_workers = core_workers
        self.redis_url = redis_url
        
        # Conexiones
        self.redis = None
        
        # Métricas en tiempo real
        self.metrics = PerformanceMetrics()
        self.request_history = []  # Para P95 calculations
        
        # Configuración adaptiva
        self.config = {
            "cache_ttl_base": 3600,  # 1 hora
            "high_confidence_ttl": 86400,  # 24 horas para alta confianza
            "batch_processing": True,
            "predictive_caching": True
        }
        
        # Routing rules dinámicas
        self.routing_rules = {
            "cache_first_threshold": 0.8,  # Si confidence >80%, priorizar cache
            "urgent_bypass_cache": True,    # Urgentes van directo a Core
            "batch_threshold": 10          # Batch si >10 requests normales
        }
    
    async def initialize(self):
        """Inicializar orquestador"""
        self.redis = await aioredis.from_url(self.redis_url)
        
        # Cargar configuración desde Redis si existe
        await self._load_dynamic_config()
        
        # Iniciar monitoring task
        asyncio.create_task(self._performance_monitor())
        
        logger.info("🎯 TruthSync Orchestrator initialized")
    
    async def verify_claim(self, text: str, priority: str = "normal", metadata: Dict = None) -> Dict:
        """
        Verificar claim usando routing inteligente:
        1. Análisis de patrón para routing decision
        2. Edge cache check (si aplicable)
        3. Core processing (si necesario)
        4. Optimización de cache basado en resultado
        """
        start_time = time.perf_counter()
        request_id = f"req-{int(time.time() * 1000)}"
        
        try:
            # 1. Routing decision
            routing_decision = await self._make_routing_decision(text, priority, metadata)
            
            # 2. Ejecutar según routing
            if routing_decision["strategy"] == "cache_first":
                result = await self._cache_first_verification(text, request_id)
            elif routing_decision["strategy"] == "core_direct":
                result = await self._core_direct_verification(text, priority, request_id)
            else:  # hybrid
                result = await self._hybrid_verification(text, priority, request_id)
            
            # 3. Post-procesamiento y optimización
            await self._optimize_cache_based_on_result(text, result)
            
            # 4. Actualizar métricas
            latency = (time.perf_counter() - start_time) * 1000  # ms
            await self._update_metrics(latency, result.get("cached", False))
            
            # 5. Agregar metadata de orquestación
            result.update({
                "request_id": request_id,
                "routing_strategy": routing_decision["strategy"],
                "orchestrator_latency_ms": round(latency, 2),
                "edge_hit": result.get("cached", False)
            })
            
            logger.debug(f"🎯 Request {request_id} completed ({latency:.1f}ms, {routing_decision['strategy']})")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Orchestrator error for {request_id}: {e}")
            return {
                "verified": False,
                "confidence": 0.0,
                "explanation": f"System error: {str(e)}",
                "error": True,
                "request_id": request_id
            }
    
    async def _make_routing_decision(self, text: str, priority: str, metadata: Dict) -> Dict:
        """
        Tomar decisión inteligente de routing basada en:
        - Patrón de la query
        - Prioridad
        - Estado actual del sistema
        - Histórico de performance
        """
        
        # Factor 1: Prioridad
        if priority == "urgent":
            return {"strategy": "core_direct", "reason": "urgent_priority"}
        
        # Factor 2: Patrón conocido (alta probabilidad de cache hit)
        if self._is_likely_cached(text):
            return {"strategy": "cache_first", "reason": "likely_cached_pattern"}
        
        # Factor 3: Estado del sistema
        if self.metrics.queue_depth > 50:  # Core saturado
            return {"strategy": "cache_first", "reason": "core_saturated"}
        
        # Factor 4: Cache hit rate baja -> intentar cache primero
        if self.metrics.cache_hit_rate < 0.3:
            return {"strategy": "hybrid", "reason": "low_cache_hit_rate"}
        
        # Default: Cache first (mejor latencia promedio)
        return {"strategy": "cache_first", "reason": "default_optimal"}
    
    def _is_likely_cached(self, text: str) -> bool:
        """Predecir si es probable que esté en cache"""
        # Patrones que típicamente están cacheados
        common_patterns = [
            "temperatura", "capital", "velocidad", "distancia",
            "población", "área", "superficie", "coordenadas"
        ]
        
        text_lower = text.lower()
        return any(pattern in text_lower for pattern in common_patterns)
    
    async def _cache_first_verification(self, text: str, request_id: str) -> Dict:
        """Estrategia: Cache primero, Core si miss"""
        
        # 1. Intentar Edge cache
        edge_result = await self._query_edge_cache(text)
        
        if edge_result and edge_result.get("cached"):
            logger.debug(f"✨ Cache HIT for {request_id}")
            return edge_result
        
        # 2. Cache miss -> Core processing
        logger.debug(f"📡 Cache MISS for {request_id}, routing to Core")
        return await self._query_core_async(text, priority="normal")
    
    async def _core_direct_verification(self, text: str, priority: str, request_id: str) -> Dict:
        """Estrategia: Directo al Core (bypass cache)"""
        logger.debug(f"🚀 Core DIRECT for {request_id}")
        return await self._query_core_async(text, priority)
    
    async def _hybrid_verification(self, text: str, priority: str, request_id: str) -> Dict:
        """Estrategia híbrida: Cache + Core en paralelo, tomar el más rápido"""
        
        # Ejecutar ambos en paralelo
        edge_task = asyncio.create_task(self._query_edge_cache(text))
        core_task = asyncio.create_task(self._query_core_async(text, priority))
        
        # Esperar al primero que complete
        done, pending = await asyncio.wait(
            [edge_task, core_task], 
            return_when=asyncio.FIRST_COMPLETED
        )
        
        # Cancelar tareas pendientes para liberar recursos
        for task in pending:
            task.cancel()
        
        # Retornar resultado del más rápido
        result = done.pop().result()
        
        logger.debug(f"🏁 Hybrid result for {request_id}")
        return result
    
    async def _query_edge_cache(self, text: str) -> Dict:
        """Query al Edge cache"""
        try:
            # Simular query HTTP al Edge
            await asyncio.sleep(0.005)  # 5ms simulado
            
            # Por simplicidad, usar Redis directo
            claim_hash = self._hash_claim(text)
            cached_data = await self.redis.get(f"truth:{claim_hash}")
            
            if cached_data:
                result = json.loads(cached_data)
                return {
                    "verified": result["verified"],
                    "confidence": result["confidence"],
                    "explanation": result["explanation"],
                    "cached": True,
                    "latency_us": 5000,  # 5ms
                    "cache_hit_count": result.get("hit_count", 1)
                }
            
            return {"cached": False}
            
        except Exception as e:
            logger.warning(f"Edge cache query failed: {e}")
            return {"cached": False, "error": str(e)}
    
    async def _query_core_async(self, text: str, priority: str) -> Dict:
        """Query asíncrono al Core"""
        try:
            # Simular procesamiento Core
            processing_time = 0.1 if priority == "urgent" else 0.2  # 100-200ms
            await asyncio.sleep(processing_time)
            
            # Análisis simplificado (en prod sería ML completo)
            result = self._simple_verification(text)
            result.update({
                "cached": False,
                "core_processing_time": processing_time * 1000,  # ms
                "priority": priority
            })
            
            return result
            
        except Exception as e:
            logger.error(f"Core query failed: {e}")
            return {
                "verified": False,
                "confidence": 0.0,
                "explanation": f"Core processing error: {str(e)}",
                "error": True
            }
    
    def _simple_verification(self, text: str) -> Dict:
        """Verificación simplificada para testing"""
        text_lower = text.lower()
        
        # Alta confianza para facts conocidos
        if any(fact in text_lower for fact in [
            "agua hierve 100", "chile capital santiago", "día 24 horas"
        ]):
            return {
                "verified": True,
                "confidence": 0.95,
                "explanation": "Fact bien establecido verificado"
            }
        
        # Confianza media para patrones reconocidos
        if any(pattern in text_lower for pattern in [
            "temperatura", "capital", "población"
        ]):
            return {
                "verified": True,
                "confidence": 0.7,
                "explanation": "Información geográfica/científica probable"
            }
        
        # Baja confianza para claims desconocidos
        return {
            "verified": False,
            "confidence": 0.3,
            "explanation": "Claim requiere verificación adicional"
        }
    
    def _hash_claim(self, text: str) -> str:
        """Hash consistente"""
        import hashlib
        normalized = text.lower().strip()
        return hashlib.sha256(normalized.encode()).hexdigest()[:16]
    
    async def _optimize_cache_based_on_result(self, text: str, result: Dict):
        """Optimizar cache basado en el resultado obtenido"""
        if result.get("error"):
            return  # No cachear errores
        
        claim_hash = self._hash_claim(text)
        confidence = result.get("confidence", 0.0)
        
        # TTL dinámico basado en confianza
        if confidence > 0.9:
            ttl = self.config["high_confidence_ttl"]  # 24h para alta confianza
        elif confidence > 0.7:
            ttl = self.config["cache_ttl_base"]  # 1h para confianza media
        else:
            ttl = self.config["cache_ttl_base"] // 2  # 30min para baja confianza
        
        # Actualizar cache con TTL optimizado
        cache_data = {
            "verified": result["verified"],
            "confidence": confidence,
            "explanation": result["explanation"],
            "timestamp": time.time(),
            "ttl": ttl
        }
        
        try:
            await self.redis.setex(f"truth:{claim_hash}", ttl, json.dumps(cache_data))
            logger.debug(f"🔄 Optimized cache TTL: {ttl}s (confidence: {confidence})")
        except Exception as e:
            logger.warning(f"Cache optimization failed: {e}")
    
    async def _update_metrics(self, latency_ms: float, was_cached: bool):
        """Actualizar métricas de performance"""
        # Agregar a historial para P95
        self.request_history.append({
            "latency": latency_ms,
            "cached": was_cached,
            "timestamp": time.time()
        })
        
        # Mantener solo últimos 1000 requests para P95
        if len(self.request_history) > 1000:
            self.request_history = self.request_history[-1000:]
        
        # Calcular métricas actualizadas
        await self._recalculate_metrics()
    
    async def _recalculate_metrics(self):
        """Recalcular métricas basado en historial reciente"""
        if not self.request_history:
            return
        
        recent_requests = [r for r in self.request_history 
                          if time.time() - r["timestamp"] < 300]  # Últimos 5 min
        
        if not recent_requests:
            return
        
        # P95 latency
        latencies = sorted([r["latency"] for r in recent_requests])
        p95_index = int(len(latencies) * 0.95)
        self.metrics.edge_latency_p95 = latencies[p95_index] if latencies else 0
        
        # Cache hit rate
        cached_count = sum(1 for r in recent_requests if r["cached"])
        self.metrics.cache_hit_rate = cached_count / len(recent_requests)
        
        # Throughput (QPS)
        time_span = max(r["timestamp"] for r in recent_requests) - min(r["timestamp"] for r in recent_requests)
        self.metrics.throughput_qps = len(recent_requests) / max(time_span, 1)
    
    async def _performance_monitor(self):
        """Monitor continuo de performance"""
        while True:
            try:
                await asyncio.sleep(30)  # Check cada 30s
                
                # Auto-ajuste de configuración basado en métricas
                await self._auto_tune_configuration()
                
                # Log métricas importantes
                if self.metrics.cache_hit_rate < 0.5:
                    logger.warning(f"⚠️  Low cache hit rate: {self.metrics.cache_hit_rate:.2f}")
                
                if self.metrics.edge_latency_p95 > 50:  # >50ms P95
                    logger.warning(f"⚠️  High P95 latency: {self.metrics.edge_latency_p95:.1f}ms")
                
            except Exception as e:
                logger.error(f"Performance monitor error: {e}")
    
    async def _auto_tune_configuration(self):
        """Auto-tuning basado en métricas"""
        # Si cache hit rate es bajo, aumentar TTL base
        if self.metrics.cache_hit_rate < 0.4:
            self.config["cache_ttl_base"] = min(7200, self.config["cache_ttl_base"] * 1.2)
            logger.info(f"🔧 Increased cache TTL to {self.config['cache_ttl_base']}s")
        
        # Si latencia alta, priorizar más el cache
        if self.metrics.edge_latency_p95 > 30:
            self.routing_rules["cache_first_threshold"] = max(0.5, 
                                                             self.routing_rules["cache_first_threshold"] - 0.1)
            logger.info(f"🔧 Lowered cache threshold to {self.routing_rules['cache_first_threshold']}")
    
    async def _load_dynamic_config(self):
        """Cargar configuración dinámica desde Redis"""
        try:
            config_data = await self.redis.get("truthsync:config")
            if config_data:
                dynamic_config = json.loads(config_data)
                self.config.update(dynamic_config)
                logger.info("🔧 Dynamic configuration loaded from Redis")
        except Exception as e:
            logger.warning(f"Failed to load dynamic config: {e}")
    
    async def get_system_status(self) -> Dict:
        """Estado completo del sistema dual"""
        return {
            "orchestrator_metrics": {
                "edge_latency_p95_ms": round(self.metrics.edge_latency_p95, 2),
                "cache_hit_rate": round(self.metrics.cache_hit_rate, 3),
                "throughput_qps": round(self.metrics.throughput_qps, 2),
                "requests_in_history": len(self.request_history)
            },
            "current_config": self.config,
            "routing_rules": self.routing_rules,
            "system_health": {
                "cache_performance": "optimal" if self.metrics.cache_hit_rate > 0.7 else "suboptimal",
                "latency_performance": "optimal" if self.metrics.edge_latency_p95 < 20 else "suboptimal"
            }
        }

# Testing
async def test_orchestrator():
    """Test básico del orquestador"""
    orchestrator = TruthSyncOrchestrator(redis_url="redis://localhost:6379")
    await orchestrator.initialize()
    
    # Test cases
    test_claims = [
        ("El agua hierve a 100 grados", "urgent"),
        ("Santiago es la capital de Chile", "high"),
        ("Claim incierto para testing", "normal"),
        ("La temperatura promedio en Atacama", "normal")
    ]
    
    print("🧪 Testing TruthSync Orchestrator...")
    
    for claim, priority in test_claims:
        result = await orchestrator.verify_claim(claim, priority)
        print(f"✓ {claim[:30]}... -> {result['verified']} (conf: {result['confidence']}, {result['routing_strategy']})")
    
    # System status
    status = await orchestrator.get_system_status()
    print("\n📊 System Status:")
    print(json.dumps(status, indent=2))

if __name__ == "__main__":
    asyncio.run(test_orchestrator())