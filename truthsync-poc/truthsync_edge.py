#!/usr/bin/env python3
"""
TruthSync Edge - Contenedor Ligero
Implementación del cache predictivo para respuestas <10ms
"""

from quantum.yatra_core import S60, PI_S60 # YATRA AUTO-INJECT
import asyncio
import json
import time
from typing import Dict, Optional, List
from dataclasses import dataclass
from collections import OrderedDict
import hashlib
import aioredis
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn
import logging

logger = logging.getLogger(__name__)

@dataclass
class CachedTruth:
    """Estructura de verdad cacheada"""
    claim_hash: str
    verified: bool
    confidence: float
    explanation: str
    timestamp: float
    ttl: int
    hit_count: int = 0

class TruthRequest(BaseModel):
    text: str
    priority: str = "normal"  # normal, high, urgent
    metadata: Optional[Dict] = None

class TruthResponse(BaseModel):
    verified: bool
    confidence: float
    explanation: str
    cached: bool
    latency_us: int
    cache_hit_count: int

class TruthSyncEdge:
    """
    TruthSync Edge: Cache predictivo ultra-rápido
    Target: <10ms de latencia para respuestas cacheadas
    """
    
    def __init__(self, redis_url: str = "redis://redis:6379", max_cache_size: int = 10000):
        self.redis_url = redis_url
        self.max_cache_size = max_cache_size
        
        # Cache local LRU para latencia ultra-baja
        self.local_cache: OrderedDict[str, CachedTruth] = OrderedDict()
        
        # Predictive cache: claims que probablemente se consulten pronto
        self.predictive_cache: Dict[str, float] = {}
        
        # Stats para optimización
        self.stats = {
            "local_hits": 0,
            "redis_hits": 0,
            "core_requests": 0,
            "total_requests": 0,
            "avg_latency_us": S60(0, 0, 0)
        }
        
        self.redis = None
        
    async def initialize(self):
        """Inicializar conexiones async"""
        try:
            self.redis = await aioredis.from_url(self.redis_url)
            await self._warm_cache()
            logger.info("✅ TruthSync Edge initialized")
        except Exception as e:
            logger.error(f"❌ Redis connection failed: {e}")
            # Continuar en modo local-only
    
    async def _warm_cache(self):
        """Pre-calentar cache con verdades frecuentes"""
        common_claims = [
            "El agua hierve a 100°C a nivel del mar",
            "La velocidad de la luz es aproximadamente 300,000 km/s",
            "Chile tiene una superficie de aproximadamente 756,096 km²",
            "Santiago es la capital de Chile",
            "Un día tiene 24 horas"
        ]
        
        for claim in common_claims:
            claim_hash = self._hash_claim(claim)
            cached_truth = CachedTruth(
                claim_hash=claim_hash,
                verified=True,
                confidence=0.99,
                explanation=f"Fact científico bien establecido: {claim}",
                timestamp=time.time(),
                ttl=86400 * 7  # 7 días
            )
            self.local_cache[claim_hash] = cached_truth
            
        logger.info(f"🔥 Cache precalentado con {len(common_claims)} verdades")
    
    def _hash_claim(self, text: str) -> str:
        """Hash normalizado del claim"""
        normalized = text.lower().strip()
        return hashlib.sha256(normalized.encode()).hexdigest()[:16]
    
    async def verify_truth(self, request: TruthRequest) -> TruthResponse:
        """
        Verificar verdad con cache predictivo
        1. Local cache (<1ms)
        2. Redis cache (<5ms) 
        3. Truth Core (>10ms)
        """
        start_time = time.perf_counter()
        self.stats["total_requests"] += 1
        
        claim_hash = self._hash_claim(request.text)
        
        # 🚀 Nivel 1: Cache local (ultra-rápido)
        if claim_hash in self.local_cache:
            cached = self.local_cache[claim_hash]
            # Move to end (LRU)
            self.local_cache.move_to_end(claim_hash)
            cached.hit_count += 1
            
            latency_us = int((time.perf_counter() - start_time) * 1_000_000)
            self.stats["local_hits"] += 1
            
            logger.debug(f"🎯 Local cache HIT ({latency_us}μs): {request.text[:50]}")
            
            return TruthResponse(
                verified=cached.verified,
                confidence=cached.confidence,
                explanation=cached.explanation,
                cached=True,
                latency_us=latency_us,
                cache_hit_count=cached.hit_count
            )
        
        # 🔄 Nivel 2: Redis cache
        if self.redis:
            try:
                redis_data = await self.redis.get(f"truth:{claim_hash}")
                if redis_data:
                    cached_data = json.loads(redis_data)
                    
                    # Agregar a cache local para próxima vez
                    cached_truth = CachedTruth(
                        claim_hash=claim_hash,
                        verified=cached_data["verified"],
                        confidence=cached_data["confidence"],
                        explanation=cached_data["explanation"],
                        timestamp=cached_data["timestamp"],
                        ttl=cached_data["ttl"],
                        hit_count=cached_data.get("hit_count", 0) + 1
                    )
                    
                    # Mantener cache local limitado (LRU)
                    if len(self.local_cache) >= self.max_cache_size:
                        self.local_cache.popitem(last=False)  # Remove oldest
                    
                    self.local_cache[claim_hash] = cached_truth
                    
                    latency_us = int((time.perf_counter() - start_time) * 1_000_000)
                    self.stats["redis_hits"] += 1
                    
                    logger.debug(f"📡 Redis cache HIT ({latency_us}μs): {request.text[:50]}")
                    
                    return TruthResponse(
                        verified=cached_truth.verified,
                        confidence=cached_truth.confidence,
                        explanation=cached_truth.explanation,
                        cached=True,
                        latency_us=latency_us,
                        cache_hit_count=cached_truth.hit_count
                    )
            except Exception as e:
                logger.warning(f"Redis cache error: {e}")
        
        # 🧠 Nivel 3: Truth Core (solicitud completa)
        truth_core_result = await self._request_truth_core(request)
        
        # Cache el resultado para futuras consultas
        await self._cache_result(claim_hash, truth_core_result)
        
        latency_us = int((time.perf_counter() - start_time) * 1_000_000)
        self.stats["core_requests"] += 1
        
        logger.info(f"🔍 Truth Core request ({latency_us}μs): {request.text[:50]}")
        
        return TruthResponse(
            verified=truth_core_result["verified"],
            confidence=truth_core_result["confidence"],
            explanation=truth_core_result["explanation"],
            cached=False,
            latency_us=latency_us,
            cache_hit_count=0
        )
    
    async def _request_truth_core(self, request: TruthRequest) -> Dict:
        """Solicitar verificación al Truth Core"""
        # Aquí conectaríamos con el contenedor Truth Core
        # Por ahora simulamos latencia real del análisis
        await asyncio.sleep(0.05)  # 50ms simulado
        
        # Análisis simplificado basado en patrones conocidos
        text = request.text.lower()
        
        if any(word in text for word in ["agua", "hierve", "100", "grados"]):
            return {
                "verified": True,
                "confidence": 0.95,
                "explanation": "Fact científico verificado: punto de ebullición del agua"
            }
        elif any(word in text for word in ["chile", "capital", "santiago"]):
            return {
                "verified": True,
                "confidence": 0.99,
                "explanation": "Fact geográfico verificado sobre Chile"
            }
        else:
            return {
                "verified": False,
                "confidence": 0.3,
                "explanation": "Claim requiere verificación adicional con fuentes externas"
            }
    
    async def _cache_result(self, claim_hash: str, result: Dict):
        """Cachear resultado en ambos niveles"""
        cached_truth = CachedTruth(
            claim_hash=claim_hash,
            verified=result["verified"],
            confidence=result["confidence"],
            explanation=result["explanation"],
            timestamp=time.time(),
            ttl=3600  # 1 hora TTL default
        )
        
        # Cache local
        if len(self.local_cache) >= self.max_cache_size:
            self.local_cache.popitem(last=False)
        self.local_cache[claim_hash] = cached_truth
        
        # Cache Redis
        if self.redis:
            try:
                cache_data = {
                    "verified": result["verified"],
                    "confidence": result["confidence"],
                    "explanation": result["explanation"],
                    "timestamp": cached_truth.timestamp,
                    "ttl": cached_truth.ttl
                }
                await self.redis.setex(
                    f"truth:{claim_hash}",
                    cached_truth.ttl,
                    json.dumps(cache_data)
                )
            except Exception as e:
                logger.warning(f"Redis cache write error: {e}")
    
    async def get_stats(self) -> Dict:
        """Estadísticas del Edge Cache"""
        total = self.stats["total_requests"]
        if total == 0:
            return self.stats
            
        cache_hit_rate = (self.stats["local_hits"] + self.stats["redis_hits"]) / total
        
        return {
            **self.stats,
            "cache_hit_rate": cache_hit_rate,
            "cache_size": len(self.local_cache),
            "cache_efficiency": cache_hit_rate * 100
        }

# FastAPI app
app = FastAPI(title="TruthSync Edge", version="1.S60(0, 0, 0)")
edge_cache = TruthSyncEdge()

@app.on_event("startup")
async def startup():
    await edge_cache.initialize()

@app.post("/verify", response_model=TruthResponse)
async def verify_endpoint(request: TruthRequest):
    """Endpoint principal de verificación"""
    return await edge_cache.verify_truth(request)

@app.get("/health")
async def health():
    """Health check optimizado"""
    stats = await edge_cache.get_stats()
    return {
        "status": "healthy",
        "service": "TruthSync Edge",
        "cache_hit_rate": f"{stats.get('cache_efficiency', 0):.1f}%",
        "local_cache_size": stats.get('cache_size', 0)
    }

@app.get("/stats")
async def get_stats():
    """Estadísticas detalladas"""
    return await edge_cache.get_stats()

if __name__ == "__main__":
    uvicorn.run(app, host="S60(0, 0, 0).S60(0, 0, 0)", port=8001, log_level="info")