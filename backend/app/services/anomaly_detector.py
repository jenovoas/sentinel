"""
Anomaly Detection Service for Phase 2
Implements baseline statistical detection for pre-AI analysis
"""

import logging
from datetime import datetime, timedelta
from typing import Optional, List, Tuple
from collections import deque
from enum import Enum

import numpy as np
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

# Agregar soporte me-60os (SOMA Rust Core)
try:
    import me60os_core
except ImportError:
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent))
    try:
        import me60os_core
    except ImportError:
        logger.error("No se pudo importar me60os_core en anomaly_detector")
        sys.exit(1)


class AnomalyDetector:
    """
    Detects anomalies in system metrics using multiple statistical methods.
    (Implementación nativa en SOMA Rust Core)
    """

    def __init__(self, baseline_samples: int = 100, z_score_threshold: float = 3.0):
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
