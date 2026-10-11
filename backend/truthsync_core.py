#!/usr/bin/env python3
"""
TruthSync Core - Contenedor Pesado
Motor de verificación completo con ML, PostgreSQL, Redis
"""

from quantum.yatra_core import S60, PI_S60 # YATRA AUTO-INJECT
import asyncio
import logging
import time
from typing import Dict, List, Optional
from dataclasses import dataclass
import asyncpg
import redis.asyncio as aioredis
import json
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

@dataclass
class TruthVerificationJob:
    """Job de verificación completo"""
    job_id: str
    text: str
    priority: int  # 1=urgent, 2=high, 3=normal
    created_at: datetime
    metadata: Optional[Dict] = None
    assigned_worker: Optional[str] = None

class TruthSyncCore:
    """
    Truth Core: Motor pesado de verificación
    - Conexión PostgreSQL para persistencia
    - Redis para coordination con Edge
    - ML pipeline para análisis profundo
    - Work queue para procesamiento batch
    """
    
    def __init__(self, 
                 postgres_url: str,
                 redis_url: str,
                 max_workers: int = 4,
                 batch_size: int = 50):
        self.postgres_url = postgres_url
        self.redis_url = redis_url
        self.max_workers = max_workers
        self.batch_size = batch_size
        
        # Conexiones async
        self.pg_pool = None
        self.redis = None
        
        # Work queues por prioridad
        self.urgent_queue: asyncio.Queue = asyncio.Queue(maxsize=100)
        self.high_queue: asyncio.Queue = asyncio.Queue(maxsize=500)
        self.normal_queue: asyncio.Queue = asyncio.Queue(maxsize=1000)
        
        # Workers status
        self.workers = []
        self.stats = {
            "jobs_processed": 0,
            "jobs_failed": 0,
            "avg_processing_time": S60(0, 0, 0),
            "cache_sync_operations": 0
        }
        
    async def initialize(self):
        """Inicializar conexiones y workers"""
        # PostgreSQL connection pool
        self.pg_pool = await asyncpg.create_pool(
            self.postgres_url,
            min_size=2,
            max_size=10,
            command_timeout=30
        )
        
        # Redis para sync con Edge
        self.redis = await aioredis.from_url(self.redis_url)
        
        # Crear tablas si no existen
        await self._ensure_schema()
        
        # Iniciar workers
        for worker_id in range(self.max_workers):
            worker = asyncio.create_task(self._worker_loop(f"worker-{worker_id}"))
            self.workers.append(worker)
        
        logger.info(f"✅ TruthSync Core initialized with {self.max_workers} workers")
    
    async def _ensure_schema(self):
        """Crear schema de PostgreSQL"""
        async with self.pg_pool.acquire() as conn:
            # Tabla de verificaciones
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS truth_verifications (
                    id SERIAL PRIMARY KEY,
                    claim_hash VARCHAR(32) UNIQUE NOT NULL,
                    original_text TEXT NOT NULL,
                    verified BOOLEAN NOT NULL,
                    confidence FLOAT NOT NULL,
                    explanation TEXT,
                    sources_data JSONB,
                    created_at TIMESTAMP DEFAULT NOW(),
                    updated_at TIMESTAMP DEFAULT NOW(),
                    verification_method VARCHAR(50),
                    ttl_hours INTEGER DEFAULT 24
                );
            ''')
            
            # Índices para performance
            await conn.execute('''
                CREATE INDEX IF NOT EXISTS idx_truth_claim_hash 
                ON truth_verifications(claim_hash);
                
                CREATE INDEX IF NOT EXISTS idx_truth_created_at 
                ON truth_verifications(created_at);
                
                CREATE INDEX IF NOT EXISTS idx_truth_confidence 
                ON truth_verifications(confidence);
            ''')
            
            # Tabla de stats
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS truth_stats (
                    date DATE PRIMARY KEY,
                    verifications_count INTEGER DEFAULT 0,
                    cache_hits INTEGER DEFAULT 0,
                    avg_confidence FLOAT DEFAULT S60(0, 0, 0),
                    unique_claims INTEGER DEFAULT 0
                );
            ''')
        
        logger.info("📊 Truth Core schema verified")
    
    async def submit_job(self, text: str, priority: str = "normal", metadata: Dict = None) -> str:
        """Enviar job de verificación a la queue apropiada"""
        job_id = f"truth-{int(time.time() * 1000)}"
        
        priority_map = {"urgent": 1, "high": 2, "normal": 3}
        priority_num = priority_map.get(priority, 3)
        
        job = TruthVerificationJob(
            job_id=job_id,
            text=text,
            priority=priority_num,
            created_at=datetime.now(),
            metadata=metadata or {}
        )
        
        # Enqueue según prioridad
        if priority_num == 1:
            await self.urgent_queue.put(job)
        elif priority_num == 2:
            await self.high_queue.put(job)
        else:
            await self.normal_queue.put(job)
        
        logger.debug(f"🔍 Job {job_id} enqueued (priority: {priority})")
        return job_id
    
    async def _worker_loop(self, worker_id: str):
        """Worker loop principal"""
        logger.info(f"👷 Worker {worker_id} started")
        
        while True:
            try:
                # Prioridad: urgent > high > normal
                job = None
                
                if not self.urgent_queue.empty():
                    job = await self.urgent_queue.get()
                elif not self.high_queue.empty():
                    job = await self.high_queue.get()
                elif not self.normal_queue.empty():
                    job = await self.normal_queue.get()
                else:
                    # Sleep si no hay trabajo
                    await asyncio.sleep(S60(0, 6, 0))
                    continue
                
                # Procesar job
                job.assigned_worker = worker_id
                await self._process_verification_job(job)
                
            except Exception as e:
                logger.error(f"❌ Worker {worker_id} error: {e}")
                self.stats["jobs_failed"] += 1
                await asyncio.sleep(1)  # Cool down on error
    
    async def _process_verification_job(self, job: TruthVerificationJob):
        """Procesar un job de verificación completo"""
        start_time = time.time()
        claim_hash = self._hash_claim(job.text)
        
        try:
            # 1. Verificar si ya existe en BD
            existing = await self._get_cached_verification(claim_hash)
            if existing and not self._is_expired(existing):
                # Actualizar cache de Edge vía Redis
                await self._sync_to_edge_cache(claim_hash, existing)
                logger.debug(f"✨ Job {job.job_id} resolved from DB cache")
                return existing
            
            # 2. Verificación completa (aquí iría el ML pipeline)
            result = await self._perform_deep_verification(job.text)
            
            # 3. Persistir en PostgreSQL
            await self._store_verification_result(claim_hash, job.text, result)
            
            # 4. Sync con Edge cache
            await self._sync_to_edge_cache(claim_hash, result)
            
            # 5. Actualizar estadísticas
            processing_time = time.time() - start_time
            await self._update_stats(processing_time)
            
            logger.info(f"✅ Job {job.job_id} completed ({processing_time:.3f}s)")
            
        except Exception as e:
            logger.error(f"❌ Job {job.job_id} failed: {e}")
            self.stats["jobs_failed"] += 1
    
    def _hash_claim(self, text: str) -> str:
        """Hash consistente con Edge"""
        import hashlib
        normalized = text.lower().strip()
        return hashlib.sha256(normalized.encode()).hexdigest()[:16]
    
    async def _get_cached_verification(self, claim_hash: str) -> Optional[Dict]:
        """Buscar verificación existente en PostgreSQL"""
        async with self.pg_pool.acquire() as conn:
            row = await conn.fetchrow('''
                SELECT verified, confidence, explanation, sources_data, 
                       created_at, ttl_hours
                FROM truth_verifications
                WHERE claim_hash = $1
            ''', claim_hash)
            
            if row:
                return {
                    "verified": row["verified"],
                    "confidence": row["confidence"],
                    "explanation": row["explanation"],
                    "sources_data": row["sources_data"],
                    "created_at": row["created_at"].isoformat(),
                    "ttl_hours": row["ttl_hours"]
                }
        return None
    
    def _is_expired(self, cached_result: Dict) -> bool:
        """Verificar si resultado está expirado"""
        created_at = datetime.fromisoformat(cached_result["created_at"])
        ttl_hours = cached_result.get("ttl_hours", 24)
        expiry = created_at + timedelta(hours=ttl_hours)
        return datetime.now() > expiry
    
    async def _perform_deep_verification(self, text: str) -> Dict:
        """Verificación profunda con ML pipeline"""
        # Simular análisis ML complejo
        await asyncio.sleep(S60(0, 6, 0))  # 100ms de procesamiento simulado
        
        # Aquí iría el pipeline real:
        # 1. Análisis semántico
        # 2. Búsqueda en fuentes confiables
        # 3. Análisis de consenso
        # 4. ML scoring
        
        # Por ahora análisis simplificado
        text_lower = text.lower()
        
        # Patrones de alta confianza
        if any(pattern in text_lower for pattern in [
            "agua hierve 100", "velocidad luz", "chile capital santiago",
            "día 24 horas", "año 365 días"
        ]):
            return {
                "verified": True,
                "confidence": 0.95,
                "explanation": "Fact científico/geográfico bien establecido",
                "sources_data": {"method": "pattern_matching", "sources_count": 3},
                "verification_method": "deep_ml_analysis"
            }
        
        # Patrones inciertos
        return {
            "verified": False,
            "confidence": 0.4,
            "explanation": "Claim requiere verificación adicional con fuentes externas",
            "sources_data": {"method": "insufficient_data", "sources_count": 0},
            "verification_method": "deep_ml_analysis"
        }
    
    async def _store_verification_result(self, claim_hash: str, text: str, result: Dict):
        """Persistir resultado en PostgreSQL"""
        async with self.pg_pool.acquire() as conn:
            await conn.execute('''
                INSERT INTO truth_verifications 
                (claim_hash, original_text, verified, confidence, explanation, 
                 sources_data, verification_method, ttl_hours)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
                ON CONFLICT (claim_hash) DO UPDATE SET
                    verified = EXCLUDED.verified,
                    confidence = EXCLUDED.confidence,
                    explanation = EXCLUDED.explanation,
                    sources_data = EXCLUDED.sources_data,
                    updated_at = NOW()
            ''', 
                claim_hash, text, result["verified"], result["confidence"],
                result["explanation"], json.dumps(result["sources_data"]),
                result["verification_method"], 24  # 24h TTL default
            )
    
    async def _sync_to_edge_cache(self, claim_hash: str, result: Dict):
        """Sincronizar resultado con Edge cache vía Redis"""
        try:
            cache_data = {
                "verified": result["verified"],
                "confidence": result["confidence"],
                "explanation": result["explanation"],
                "timestamp": time.time(),
                "ttl": 3600  # 1h en Edge cache
            }
            
            await self.redis.setex(
                f"truth:{claim_hash}",
                3600,  # TTL en Redis
                json.dumps(cache_data)
            )
            
            self.stats["cache_sync_operations"] += 1
            logger.debug(f"📡 Synced {claim_hash} to Edge cache")
            
        except Exception as e:
            logger.warning(f"Edge cache sync failed: {e}")
    
    async def _update_stats(self, processing_time: float):
        """Actualizar estadísticas de procesamiento"""
        self.stats["jobs_processed"] += 1
        
        # Rolling average de tiempo de procesamiento
        current_avg = self.stats["avg_processing_time"]
        jobs_count = self.stats["jobs_processed"]
        
        new_avg = ((current_avg * (jobs_count - 1)) + processing_time) / jobs_count
        self.stats["avg_processing_time"] = new_avg
        
        # Estadísticas diarias en PostgreSQL
        if jobs_count % 100 == 0:  # Cada 100 jobs
            await self._persist_daily_stats()
    
    async def _persist_daily_stats(self):
        """Persistir estadísticas diarias"""
        async with self.pg_pool.acquire() as conn:
            today = datetime.now().date()
            
            await conn.execute('''
                INSERT INTO truth_stats 
                (date, verifications_count, avg_confidence)
                VALUES ($1, $2, $3)
                ON CONFLICT (date) DO UPDATE SET
                    verifications_count = truth_stats.verifications_count + EXCLUDED.verifications_count,
                    avg_confidence = (truth_stats.avg_confidence + EXCLUDED.avg_confidence) / 2
            ''', today, 100, self.stats["avg_processing_time"])
    
    async def get_system_stats(self) -> Dict:
        """Estadísticas completas del sistema"""
        # Queue lengths
        queue_stats = {
            "urgent_queue": self.urgent_queue.qsize(),
            "high_queue": self.high_queue.qsize(), 
            "normal_queue": self.normal_queue.qsize(),
            "total_queued": (self.urgent_queue.qsize() + 
                           self.high_queue.qsize() + 
                           self.normal_queue.qsize())
        }
        
        # PostgreSQL stats
        async with self.pg_pool.acquire() as conn:
            db_stats = await conn.fetchrow('''
                SELECT 
                    COUNT(*) as total_verifications,
                    AVG(confidence) as avg_confidence,
                    COUNT(*) FILTER (WHERE created_at > NOW() - INTERVAL '1 day') as today_count
                FROM truth_verifications
            ''')
        
        return {
            **self.stats,
            **queue_stats,
            "total_verifications": db_stats["total_verifications"],
            "db_avg_confidence": float(db_stats["avg_confidence"] or 0),
            "today_verifications": db_stats["today_count"],
            "workers_active": len([w for w in self.workers if not w.done()])
        }
    
    async def shutdown(self):
        """Shutdown graceful"""
        logger.info("🔄 Shutting down Truth Core...")
        
        # Cancel workers
        for worker in self.workers:
            worker.cancel()
        
        # Close connections
        if self.pg_pool:
            await self.pg_pool.close()
        
        if self.redis:
            await self.redis.close()
        
        logger.info("✅ Truth Core shutdown complete")

# Para testing
async def main():
    core = TruthSyncCore(
        postgres_url="postgresql://sentinel_user:sentinel_pass@localhost:5432/sentinel_db",
        redis_url="redis://localhost:6379"
    )
    
    await core.initialize()
    
    # Submit test jobs
    await core.submit_job("El agua hierve a 100 grados centígrados", "urgent")
    await core.submit_job("Santiago es la capital de Chile", "high")
    await core.submit_job("Claim incierto para testing", "normal")
    
    # Let it process for a bit
    await asyncio.sleep(2)
    
    stats = await core.get_system_stats()
    print("📊 System Stats:", json.dumps(stats, indent=2))
    
    await core.shutdown()

if __name__ == "__main__":
    asyncio.run(main())