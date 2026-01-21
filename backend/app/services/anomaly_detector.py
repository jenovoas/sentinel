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


class AnomalyDetector:
    """
    Detects anomalies in system metrics using multiple statistical methods.
    Baseline is learned during first N samples.
    """

    def __init__(self, baseline_samples: int = 100, z_score_threshold: float = 3.0):
        """
        Args:
            baseline_samples: Number of samples to learn baseline behavior
            z_score_threshold: Number of standard deviations for anomaly (default 3.0 = 99.7% confidence)
        """
        self.baseline_samples = baseline_samples
        self.z_score_threshold = z_score_threshold

        # Baseline statistics (learned over time)
        self.baseline_stats = {
            'cpu': {'mean': 50.0, 'std': 15.0, 'min': 10.0, 'max': 90.0},
            'memory': {'mean': 50.0, 'std': 10.0, 'min': 20.0, 'max': 90.0},
            'network': {'mean': 1000000, 'std': 500000},
            'gpu': {'mean': 30.0, 'std': 20.0, 'max': 95.0},
        }

        # Running windows for detection
        self.cpu_window = deque(maxlen=60)          # Last 60 samples (~15 minutes)
        self.memory_window = deque(maxlen=60)
        self.network_window = deque(maxlen=60)
        self.gpu_window = deque(maxlen=60)

        # State tracking
        self.samples_processed = 0
        self.learning_phase = True


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
        """
        Analyze current metrics against baseline and return detected anomalies.

        Args:
            cpu: CPU usage percentage (0-100)
            memory: Memory usage percentage (0-100)
            network_bytes: Total network bytes (bytes/sec)
            gpu: GPU usage percentage (0-100) or None
            db_connections: Active database connections
            db_locks: Number of database locks

        Returns:
            List of Anomaly objects detected (may be empty)
        """
        anomalies = []

        # Update learning windows
        self.cpu_window.append(cpu)
        self.memory_window.append(memory)
        self.network_window.append(network_bytes)
        if gpu is not None:
            self.gpu_window.append(gpu)

        self.samples_processed += 1

        # After baseline_samples, stop learning and start detecting
        if self.samples_processed == self.baseline_samples:
            self.learning_phase = False
            self._update_baseline_stats()
            logger.info(f"✅ Anomaly detector baseline learned from {self.baseline_samples} samples")

        # Skip detection during learning phase
        if self.learning_phase:
            return anomalies

        # ============ CPU ANALYSIS ============
        cpu_anomalies = self._detect_cpu_anomalies(cpu)
        anomalies.extend(cpu_anomalies)

        # ============ MEMORY ANALYSIS ============
        memory_anomalies = self._detect_memory_anomalies(memory, memory_used_mb, memory_total_mb)
        anomalies.extend(memory_anomalies)

        # ============ NETWORK ANALYSIS ============
        network_anomalies = self._detect_network_anomalies(network_bytes)
        anomalies.extend(network_anomalies)

        # ============ GPU ANALYSIS ============
        if gpu is not None:
            gpu_anomalies = self._detect_gpu_anomalies(gpu)
            anomalies.extend(gpu_anomalies)

        # ============ DATABASE ANALYSIS ============
        db_anomalies = self._detect_database_anomalies(db_connections, db_locks)
        anomalies.extend(db_anomalies)

        return anomalies


    def _detect_cpu_anomalies(self, cpu: float) -> List[Anomaly]:
        """Detect CPU-related anomalies"""
        anomalies = []

        # Method 1: Z-Score
        z_score = self._calculate_zscore(cpu, self.baseline_stats['cpu'])
        if abs(z_score) > self.z_score_threshold:
            anomalies.append(Anomaly(
                anomaly_type=AnomalyType.CPU_SPIKE,
                severity=SeverityLevel.CRITICAL if cpu > 90 else SeverityLevel.WARNING,
                title=f"CPU Spike Detected: {cpu:.1f}%",
                description=f"CPU usage at {cpu:.1f}% (z-score: {z_score:.2f})",
                metric_value=cpu,
                threshold_value=self.baseline_stats['cpu']['mean'] + (self.z_score_threshold * self.baseline_stats['cpu']['std']),
                context_data={
                    'method': DetectionMethod.ZSCORE,
                    'z_score': z_score,
                    'baseline_mean': self.baseline_stats['cpu']['mean'],
                    'baseline_std': self.baseline_stats['cpu']['std'],
                }
            ))

        # Method 2: Trend - sustained high CPU
        if len(self.cpu_window) >= 10:
            recent_cpu = list(self.cpu_window)[-10:]
            if all(c > 80 for c in recent_cpu):
                anomalies.append(Anomaly(
                    anomaly_type=AnomalyType.CPU_SPIKE,
                    severity=SeverityLevel.CRITICAL,
                    title=f"Sustained High CPU: {cpu:.1f}%",
                    description=f"CPU sustained above 80% for last 10 samples (~2.5 minutes)",
                    metric_value=cpu,
                    threshold_value=80.0,
                    context_data={
                        'method': DetectionMethod.TREND,
                        'sustained_duration': '2.5 minutes',
                        'samples': len(recent_cpu),
                    }
                ))

        return anomalies


    def _detect_memory_anomalies(self, memory: float, used_mb: float, total_mb: float) -> List[Anomaly]:
        """Detect memory-related anomalies"""
        anomalies = []

        # Method 1: Absolute threshold
        if memory > 90:
            anomalies.append(Anomaly(
                anomaly_type=AnomalyType.MEMORY_SPIKE,
                severity=SeverityLevel.CRITICAL,
                title=f"Critical Memory Usage: {memory:.1f}%",
                description=f"Memory at {memory:.1f}% ({used_mb:.0f} MB / {total_mb:.0f} MB)",
                metric_value=memory,
                threshold_value=90.0,
                context_data={
                    'method': DetectionMethod.THRESHOLD,
                    'used_mb': used_mb,
                    'total_mb': total_mb,
                }
            ))

        # Method 2: Z-Score
        elif memory > self.baseline_stats['memory']['mean']:
            z_score = self._calculate_zscore(memory, self.baseline_stats['memory'])
            if abs(z_score) > self.z_score_threshold:
                anomalies.append(Anomaly(
                    anomaly_type=AnomalyType.MEMORY_SPIKE,
                    severity=SeverityLevel.WARNING,
                    title=f"Memory Spike: {memory:.1f}%",
                    description=f"Memory usage at {memory:.1f}% (z-score: {z_score:.2f})",
                    metric_value=memory,
                    threshold_value=self.baseline_stats['memory']['mean'] + (self.z_score_threshold * self.baseline_stats['memory']['std']),
                    context_data={
                        'method': DetectionMethod.ZSCORE,
                        'z_score': z_score,
                    }
                ))

        return anomalies


    def _detect_network_anomalies(self, network_bytes: int) -> List[Anomaly]:
        """Detect network traffic anomalies"""
        anomalies = []

        # Method 1: Rate of change - sudden spike
        if len(self.network_window) >= 2:
            prev_bytes = list(self.network_window)[-2]
            if prev_bytes > 0:
                rate_change = (network_bytes - prev_bytes) / prev_bytes
                if rate_change > 5.0:  # 500% increase
                    anomalies.append(Anomaly(
                        anomaly_type=AnomalyType.NETWORK_SPIKE,
                        severity=SeverityLevel.WARNING,
                        title=f"Network Spike Detected",
                        description=f"Network traffic increased by {rate_change*100:.0f}% in one sample",
                        metric_value=float(network_bytes),
                        threshold_value=float(prev_bytes * 5),
                        context_data={
                            'method': DetectionMethod.RATE_OF_CHANGE,
                            'rate_of_change': rate_change,
                            'previous_bytes': prev_bytes,
                        }
                    ))

        # Method 2: Z-Score sustained high traffic
        if len(self.network_window) >= 10:
            recent_traffic = list(self.network_window)[-10:]
            avg_traffic = np.mean(recent_traffic)
            if avg_traffic > self.baseline_stats['network']['mean'] * 3:
                anomalies.append(Anomaly(
                    anomaly_type=AnomalyType.NETWORK_SPIKE,
                    severity=SeverityLevel.WARNING,
                    title=f"Sustained High Network Traffic",
                    description=f"Average network traffic {avg_traffic:.0f} bytes/s (3x baseline)",
                    metric_value=avg_traffic,
                    threshold_value=self.baseline_stats['network']['mean'] * 3,
                    context_data={
                        'method': DetectionMethod.TREND,
                        'sustained_duration': '2.5 minutes',
                    }
                ))

        return anomalies


    def _detect_gpu_anomalies(self, gpu: float) -> List[Anomaly]:
        """Detect GPU-related anomalies"""
        anomalies = []

        # Absolute threshold
        if gpu > 95:
            anomalies.append(Anomaly(
                anomaly_type=AnomalyType.GPU_OVERHEAT,
                severity=SeverityLevel.CRITICAL,
                title=f"GPU Overload: {gpu:.1f}%",
                description=f"GPU usage at critical level {gpu:.1f}%",
                metric_value=gpu,
                threshold_value=95.0,
                context_data={'method': DetectionMethod.THRESHOLD}
            ))

        return anomalies


    def _detect_database_anomalies(self, db_connections: int, db_locks: int) -> List[Anomaly]:
        """Detect database-related anomalies"""
        anomalies = []

        # Connection surge
        if db_connections > 50:
            anomalies.append(Anomaly(
                anomaly_type=AnomalyType.CONNECTION_SURGE,
                severity=SeverityLevel.WARNING if db_connections < 100 else SeverityLevel.CRITICAL,
                title=f"DB Connection Surge: {db_connections}",
                description=f"Database connections at {db_connections} (threshold: 50)",
                metric_value=float(db_connections),
                threshold_value=50.0,
                context_data={
                    'method': DetectionMethod.THRESHOLD,
                    'active_connections': db_connections,
                }
            ))

        # Lock detected
        if db_locks > 5:
            anomalies.append(Anomaly(
                anomaly_type=AnomalyType.LOCK_DETECTED,
                severity=SeverityLevel.CRITICAL,
                title=f"Database Lock Detected: {db_locks}",
                description=f"Found {db_locks} active database locks",
                metric_value=float(db_locks),
                threshold_value=5.0,
                context_data={
                    'method': DetectionMethod.THRESHOLD,
                    'lock_count': db_locks,
                }
            ))

        return anomalies


    def _calculate_zscore(self, value: float, stats: dict) -> float:
        """Calculate z-score for a value against baseline stats"""
        mean = stats['mean']
        std = stats['std']
        if std == 0:
            return 0.0
        return (value - mean) / std


    def _update_baseline_stats(self):
        """Learn baseline statistics after N samples"""
        try:
            if len(self.cpu_window) > 10:
                cpu_array = np.array(list(self.cpu_window))
                self.baseline_stats['cpu'] = {
                    'mean': float(np.mean(cpu_array)),
                    'std': float(np.std(cpu_array)),
                    'min': float(np.min(cpu_array)),
                    'max': float(np.max(cpu_array)),
                }

            if len(self.memory_window) > 10:
                mem_array = np.array(list(self.memory_window))
                self.baseline_stats['memory'] = {
                    'mean': float(np.mean(mem_array)),
                    'std': float(np.std(mem_array)),
                    'min': float(np.min(mem_array)),
                    'max': float(np.max(mem_array)),
                }

            if len(self.network_window) > 10:
                net_array = np.array(list(self.network_window))
                self.baseline_stats['network'] = {
                    'mean': float(np.mean(net_array)),
                    'std': float(np.std(net_array)),
                }

            if len(self.gpu_window) > 10:
                gpu_array = np.array(list(self.gpu_window))
                self.baseline_stats['gpu'] = {
                    'mean': float(np.mean(gpu_array)),
                    'std': float(np.std(gpu_array)),
                    'max': float(np.max(gpu_array)),
                }

            logger.info(f"📊 Baseline stats updated: {self.baseline_stats}")

        except Exception as e:
            logger.error(f"❌ Error updating baseline stats: {e}")


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
