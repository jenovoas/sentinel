# Autor: Jaime Novoa Sepúlveda — Todos los derechos reservados.
# Licencia: Apache 2.0 + Cláusula No Comercial (ver LICENSE).
# Colaboración abierta con atribución. Uso comercial PROHIBIDO sin autorización.
"""
Anomaly Detection Service for Phase 2
Implements baseline statistical detection for pre-AI analysis
"""

import logging
from datetime import datetime, timedelta
from enum import Enum
from typing import List, Optional, Dict, Any
from sqlalchemy import and_, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.monitoring import Anomaly, AnomalyType, SeverityLevel, MetricSample

logger = logging.getLogger(__name__)


class DetectionMethod(str, Enum):
    """Statistical anomaly detection methods"""
    ZSCORE = "zscore"                  # Z-score deviation
    PERCENTILE = "percentile"          # Percentile thresholds
    THRESHOLD = "threshold"            # Fixed thresholds
    TREND = "trend"                    # Trend-based (slope)
    RATE_OF_CHANGE = "rate_of_change"  # Sudden spikes


import sys
from pathlib import Path

# Try to import me60os_core with multiple fallback paths to resolve import errors
try:
    import me60os_core
except ImportError:
    # Try parent directory (app/)
    sys.path.append(str(Path(__file__).parent.parent))
    # Try project root (backend/)
    sys.path.append(str(Path(__file__).parent.parent.parent))
    # Try specific build directory if exists
    sys.path.append(str(Path(__file__).parent.parent.parent / "build"))
    
    try:
        import me60os_core
    except ImportError:
        logger.error("❌ me60os_core (SOMA Rust) not found in search paths. Anomaly detection will be limited.")
        # Define a mock or handle missing core to prevent crash
        me60os_core = None


class AnomalyDetector:
    """
    Detects anomalies in system metrics using multiple statistical methods.
    (Implementación nativa en SOMA Rust Core)
    """

    def __init__(self, baseline_samples: int = 100, z_score_threshold: float = 3.0):
        if me60os_core is None:
            self._core = None
            logger.warning("AnomalyDetector initialized without Rust Core backend")
            return
        self._core = me60os_core.AnomalyDetectorCore(baseline_samples, z_score_threshold)
        self._learning_notified = False

    async def analyze_metrics(
        self,
        cpu: float,
        memory: float,
        network_bytes: int,
        gpu: Optional[float] = None,
        db_connections: int = 0,
        db_locks: int = 0,
        memory_used_mb: float = 0,
        memory_total_mb: float = 0,
    ) -> List[Anomaly]:
        
        if self._core is None:
            return []

        raw_anomalies = self._core.analyze_metrics(
            float(cpu), float(memory), float(network_bytes),
            float(gpu) if gpu is not None else None,
            int(db_connections), int(db_locks),
            float(memory_used_mb), float(memory_total_mb)
        )

        if not self._core.is_learning and not self._learning_notified:
            logger.info("✅ Anomaly detector baseline learned (SOMA Rust)")
            self._learning_notified = True

        anomalies = []
        for a in raw_anomalies:
            severity_mapped = SeverityLevel.CRITICAL if a["severity"] == 3 else SeverityLevel.WARNING
            try:
                atype = AnomalyType(a["anomaly_type"])
            except ValueError:
                # Fallback genérico si el enum no está mapeado
                atype = AnomalyType.CPU_SPIKE 
                
            anomalies.append(Anomaly(
                anomaly_type=atype,
                severity=severity_mapped,
                title=a["title"],
                description=a["description"],
                metric_value=a["metric_value"],
                threshold_value=a["threshold_value"],
                context_data={"source": "me60os_core"}
            ))

        return anomalies



# Singleton instance per app
_detector: Optional[AnomalyDetector] = None


async def get_anomaly_detector() -> AnomalyDetector:
    """Get or create the anomaly detector singleton"""
    global _detector
    if _detector is None:
        _detector = AnomalyDetector(baseline_samples=100)
    return _detector


async def save_anomalies(session: AsyncSession, anomalies: List[Anomaly]):
    """Batch save detected anomalies to database"""
    if not anomalies:
        return

    try:
        session.add_all(anomalies)
        await session.flush()
        logger.info(f"💾 Saved {len(anomalies)} anomalies to database")
    except Exception as e:
        logger.error(f"❌ Error saving anomalies: {e}")
        raise
