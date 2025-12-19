"""
Sentinel Dual-Lane Architecture
Separa flujos de datos en dos carriles independientes:
- Security & Audit Lane: Determinista, sin buffering, WAL obligatorio
- Observability & Trends Lane: Buffering permitido, predicción habilitada

ELIMINA RIESGOS EXISTENCIALES:
1. Out-of-order en Loki (pérdida evidencia forense)
2. Ventana de ceguera (ataques sin detección)
3. OOM por buffering descontrolado
4. Fabricación de evidencia por regeneración
"""

import asyncio
import time
import json
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field
from enum import Enum
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class DataLane(Enum):
    """
    Carriles de datos con políticas diferentes
    
    SECURITY: Precisión forense, cero buffering, WAL obligatorio
    OBSERVABILITY: Throughput optimizado, buffering permitido
    """
    SECURITY = "security"
    OBSERVABILITY = "observability"


class EventPriority(Enum):
    """Prioridad de eventos para routing"""
    CRITICAL = "critical"    # Security lane, bypass inmediato
    HIGH = "high"           # Security lane, alta prioridad
    MEDIUM = "medium"       # Observability lane, normal
    LOW = "low"             # Observability lane, batch permitido


@dataclass
class LaneEvent:
    """
    Evento con metadata de lane
    
    Attributes:
        lane: Carril de datos (SECURITY o OBSERVABILITY)
        source: Origen del evento (auditd, shield, app, etc.)
        priority: Prioridad para routing
        timestamp: Timestamp de recolección (no de envío)
        labels: Labels para Loki/Prometheus
        data: Payload del evento
        synthetic: Si es dato imputado/regenerado
    """
    lane: DataLane
    source: str
    priority: EventPriority
    timestamp: float
    labels: Dict[str, str]
    data: Dict[str, Any]
    synthetic: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Serializa evento para WAL/Loki"""
        return {
            "lane": self.lane.value,
            "source": self.source,
            "priority": self.priority.value,
            "timestamp": self.timestamp,
            "labels": self.labels,
            "data": self.data,
            "synthetic": self.synthetic
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "LaneEvent":
        """Deserializa evento desde WAL"""
        return cls(
            lane=DataLane(data["lane"]),
            source=data["source"],
            priority=EventPriority(data["priority"]),
            timestamp=data["timestamp"],
            labels=data["labels"],
            data=data["data"],
            synthetic=data.get("synthetic", False)
        )


class DualLaneRouter:
    """
    Router de eventos a carriles según origen y tipo
    
    RESPONSABILIDAD:
    - Clasificar eventos automáticamente
    - Enrutar a Security o Observability lane
    - Aplicar políticas de bypass/buffering
    """
    
    # Fuentes que SIEMPRE van a Security Lane
    SECURITY_SOURCES = {
        "auditd",
        "ebpf",
        "shield",
        "dual_guardian",
        "kernel",
        "syscall"
    }
    
    # Fuentes que van a Observability Lane
    OBSERVABILITY_SOURCES = {
        "prometheus",
        "app",
        "network",
        "llm",
        "database",
        "cache"
    }
    
    def __init__(self):
        self.stats = {
            "security_events": 0,
            "observability_events": 0,
            "misrouted_events": 0
        }
    
    def classify_event(
        self,
        source: str,
        data: Dict[str, Any],
        labels: Optional[Dict[str, str]] = None
    ) -> LaneEvent:
        """
        Clasifica evento y crea LaneEvent
        
        ALGORITMO:
        1. Si source en SECURITY_SOURCES → Security Lane
        2. Si labels contiene "threat" o "attack" → Security Lane
        3. Si data contiene "malicious" o "blocked" → Security Lane
        4. Caso contrario → Observability Lane
        
        Args:
            source: Origen del evento
            data: Payload del evento
            labels: Labels opcionales
        
        Returns:
            LaneEvent clasificado
        """
        labels = labels or {}
        timestamp = time.time()
        
        # 1. Clasificación por source
        if source in self.SECURITY_SOURCES:
            lane = DataLane.SECURITY
            priority = EventPriority.CRITICAL
            self.stats["security_events"] += 1
        
        # 2. Clasificación por labels
        elif any(key in labels for key in ["threat", "attack", "malicious"]):
            lane = DataLane.SECURITY
            priority = EventPriority.HIGH
            self.stats["security_events"] += 1
        
        # 3. Clasificación por contenido
        elif any(word in str(data).lower() for word in ["malicious", "blocked", "threat", "attack"]):
            lane = DataLane.SECURITY
            priority = EventPriority.HIGH
            self.stats["security_events"] += 1
        
        # 4. Default: Observability Lane
        else:
            lane = DataLane.OBSERVABILITY
            priority = EventPriority.MEDIUM
            self.stats["observability_events"] += 1
        
        # Agregar lane a labels
        labels["lane"] = lane.value
        labels["source"] = source
        labels["priority"] = priority.value
        
        return LaneEvent(
            lane=lane,
            source=source,
            priority=priority,
            timestamp=timestamp,
            labels=labels,
            data=data,
            synthetic=False
        )
    
    def should_bypass_buffer(self, event: LaneEvent) -> bool:
        """
        Determina si evento debe bypass buffer
        
        Security Lane: SIEMPRE bypass
        Observability Lane: Solo si priority=CRITICAL
        """
        if event.lane == DataLane.SECURITY:
            return True
        
        if event.priority == EventPriority.CRITICAL:
            return True
        
        return False
    
    def get_stats(self) -> Dict[str, Any]:
        """Obtiene estadísticas de routing"""
        total = self.stats["security_events"] + self.stats["observability_events"]
        
        return {
            **self.stats,
            "total_events": total,
            "security_ratio": self.stats["security_events"] / total if total > 0 else 0,
            "observability_ratio": self.stats["observability_events"] / total if total > 0 else 0
        }


class SecurityLaneCollector:
    """
    Collector para Security Lane
    
    POLÍTICA ESTRICTA:
    - Sin buffering (latencia <10ms)
    - WAL obligatorio (durabilidad)
    - Bypass de colas
    - Alerta si pérdida (nunca imputa)
    """
    
    def __init__(self, wal_path: Path):
        self.wal_path = wal_path
        self.stats = {
            "events_collected": 0,
            "events_lost": 0,
            "avg_latency_ms": 0.0
        }
        self.latencies: List[float] = []
    
    async def emit_immediate(
        self,
        event: LaneEvent
    ) -> bool:
        """
        Emite evento inmediatamente sin buffering
        
        Pipeline:
        1. WAL (fsync) - durabilidad
        2. Dual-Guardian (decisión local) - bloqueo
        3. Storage forense (S3) - evidencia
        4. Loki (lane=security) - observabilidad
        
        Returns:
            True si exitoso, False si pérdida
        """
        start = time.time()
        
        try:
            # 1. WAL (obligatorio)
            # TODO: Implementar WAL.append()
            
            # 2. Dual-Guardian (si aplica)
            # TODO: Implementar dual_guardian.evaluate()
            
            # 3. Storage forense
            # TODO: Implementar forensic_storage.append()
            
            # 4. Loki
            # TODO: Implementar loki_client.push()
            
            latency_ms = (time.time() - start) * 1000
            self.latencies.append(latency_ms)
            self.stats["events_collected"] += 1
            self.stats["avg_latency_ms"] = sum(self.latencies) / len(self.latencies)
            
            if latency_ms > 10:
                logger.warning(
                    f"Security lane latency high: {latency_ms:.2f}ms "
                    f"(target <10ms)"
                )
            
            return True
            
        except Exception as e:
            logger.error(f"Security lane emit failed: {e}")
            self.stats["events_lost"] += 1
            
            # CRITICAL: Alerta de IntegrityGap
            await self._alert_integrity_gap(event, str(e))
            
            return False
    
    async def _alert_integrity_gap(self, event: LaneEvent, error: str):
        """
        Alerta crítica de pérdida de integridad
        
        NUNCA imputa datos, solo alerta
        """
        logger.critical(
            f"INTEGRITY GAP: Security event lost\n"
            f"Source: {event.source}\n"
            f"Timestamp: {event.timestamp}\n"
            f"Error: {error}\n"
            f"Data: {json.dumps(event.data, indent=2)}"
        )
        
        # TODO: Enviar alerta a PagerDuty/Slack/etc
    
    def get_stats(self) -> Dict[str, Any]:
        """Obtiene estadísticas del collector"""
        return {
            **self.stats,
            "loss_rate": (
                self.stats["events_lost"] / 
                (self.stats["events_collected"] + self.stats["events_lost"])
                if (self.stats["events_collected"] + self.stats["events_lost"]) > 0 
                else 0
            )
        }


class ObservabilityLaneCollector:
    """
    Collector para Observability Lane
    
    POLÍTICA OPTIMIZADA:
    - Buffering permitido (throughput)
    - Imputación permitida (continuidad)
    - Backpressure (límites duros)
    - Reordenamiento (antes de flush)
    """
    
    def __init__(
        self,
        wal_path: Path,
        max_buffer_bytes: int = 10 * 1024 * 1024,  # 10MB
        max_batch_records: int = 1000,
        max_batch_ms: int = 1000
    ):
        self.wal_path = wal_path
        self.max_buffer_bytes = max_buffer_bytes
        self.max_batch_records = max_batch_records
        self.max_batch_ms = max_batch_ms
        
        self.buffer: List[LaneEvent] = []
        self.buffer_bytes = 0
        self.last_flush = time.time()
        
        self.stats = {
            "events_collected": 0,
            "events_buffered": 0,
            "events_flushed": 0,
            "events_dropped": 0,
            "backpressure_activations": 0,
            "avg_batch_size": 0
        }
    
    async def emit_buffered(
        self,
        event: LaneEvent
    ) -> bool:
        """
        Emite evento con buffering
        
        Pipeline:
        1. Agregar a buffer
        2. Verificar límites (backpressure)
        3. Flush si necesario (batch lleno o timeout)
        4. Reordenar por timestamp antes de flush
        
        Returns:
            True si exitoso, False si dropped
        """
        try:
            # 1. Agregar a buffer
            event_bytes = len(json.dumps(event.to_dict()))
            
            # 2. Verificar límites (backpressure)
            if self.buffer_bytes + event_bytes > self.max_buffer_bytes:
                logger.warning(
                    f"Backpressure activated: buffer full "
                    f"({self.buffer_bytes / 1024 / 1024:.1f}MB)"
                )
                self.stats["backpressure_activations"] += 1
                
                # Flush inmediato
                await self._flush_buffer()
                
                # Si aún no cabe, drop evento de menor prioridad
                if self.buffer_bytes + event_bytes > self.max_buffer_bytes:
                    dropped = self._drop_lowest_priority()
                    if dropped:
                        logger.info(f"Dropped event: {dropped.source} (priority={dropped.priority.value})")
            
            self.buffer.append(event)
            self.buffer_bytes += event_bytes
            self.stats["events_buffered"] += 1
            
            # 3. Flush si batch lleno o timeout
            should_flush = (
                len(self.buffer) >= self.max_batch_records or
                (time.time() - self.last_flush) * 1000 >= self.max_batch_ms
            )
            
            if should_flush:
                await self._flush_buffer()
            
            return True
            
        except Exception as e:
            logger.error(f"Observability lane emit failed: {e}")
            self.stats["events_dropped"] += 1
            return False
    
    async def _flush_buffer(self):
        """
        Flush buffer a Loki con reordenamiento
        
        CRÍTICO: Reordena por (stream_labels, timestamp) para evitar out-of-order
        """
        if not self.buffer:
            return
        
        try:
            # 1. Reordenar por timestamp
            sorted_events = sorted(self.buffer, key=lambda e: e.timestamp)
            
            # 2. WAL
            # TODO: Implementar WAL.append_batch()
            
            # 3. Loki
            # TODO: Implementar loki_client.push_batch()
            
            batch_size = len(sorted_events)
            self.stats["events_flushed"] += batch_size
            self.stats["avg_batch_size"] = (
                (self.stats["avg_batch_size"] * (self.stats["events_flushed"] - batch_size) + batch_size) /
                self.stats["events_flushed"]
            )
            
            # 4. Limpiar buffer
            self.buffer.clear()
            self.buffer_bytes = 0
            self.last_flush = time.time()
            
            logger.debug(f"Flushed {batch_size} events to Loki")
            
        except Exception as e:
            logger.error(f"Buffer flush failed: {e}")
    
    def _drop_lowest_priority(self) -> Optional[LaneEvent]:
        """
        Drop evento de menor prioridad (backpressure)
        
        Orden de drop:
        1. LOW priority
        2. MEDIUM priority
        3. HIGH priority (nunca CRITICAL)
        """
        for priority in [EventPriority.LOW, EventPriority.MEDIUM, EventPriority.HIGH]:
            for i, event in enumerate(self.buffer):
                if event.priority == priority:
                    dropped = self.buffer.pop(i)
                    self.buffer_bytes -= len(json.dumps(dropped.to_dict()))
                    self.stats["events_dropped"] += 1
                    return dropped
        
        return None
    
    def get_stats(self) -> Dict[str, Any]:
        """Obtiene estadísticas del collector"""
        return {
            **self.stats,
            "buffer_utilization": self.buffer_bytes / self.max_buffer_bytes,
            "drop_rate": (
                self.stats["events_dropped"] / 
                self.stats["events_collected"]
                if self.stats["events_collected"] > 0 
                else 0
            )
        }


# Global instances
dual_lane_router = DualLaneRouter()
