"""
TruthSync Observability & Integrity Metrics
Integration with Prometheus, Grafana, and Loki for complete system monitoring
"""

import time
import json
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
from prometheus_client import Counter, Histogram, Gauge, Summary, Info
import logging


# Configure Loki-compatible logging
class LokiFormatter(logging.Formatter):
    """Format logs for Loki ingestion"""
    
    def format(self, record):
        log_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': record.levelname,
            'component': 'truthsync',
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
        }
        
        # Add extra fields if present
        if hasattr(record, 'claim_key'):
            log_data['claim_key'] = record.claim_key
        if hasattr(record, 'confidence'):
            log_data['confidence'] = record.confidence
        if hasattr(record, 'verification_result'):
            log_data['verification_result'] = record.verification_result
            
        return json.dumps(log_data)


# Prometheus Metrics
class TruthSyncMetrics:
    """Prometheus metrics for TruthSync"""
    
    # Counters
    claims_processed_total = Counter(
        'truthsync_claims_processed_total',
        'Total number of claims processed',
        ['result']  # cache_hit, cache_miss, verified, rejected
    )
    
    predictions_total = Counter(
        'truthsync_predictions_total',
        'Total number of predictions made',
        ['outcome']  # correct, incorrect
    )
    
    cache_operations_total = Counter(
        'truthsync_cache_operations_total',
        'Total cache operations',
        ['operation', 'result']  # get/put, hit/miss
    )
    
    ml_updates_total = Counter(
        'truthsync_ml_updates_total',
        'Total ML model updates sent to Sentinel'
    )
    
    anomalies_detected_total = Counter(
        'truthsync_anomalies_detected_total',
        'Total anomalies detected',
        ['anomaly_type']
    )
    
    # Histograms
    processing_duration_seconds = Histogram(
        'truthsync_processing_duration_seconds',
        'Time spent processing claims',
        ['stage'],  # extraction, verification, caching
        buckets=[0.00001, 0.00005, 0.0001, 0.0005, 0.001, 0.005, 0.01, 0.05, 0.1]
    )
    
    buffer_write_duration_seconds = Histogram(
        'truthsync_buffer_write_duration_seconds',
        'Time spent writing to shared buffers',
        buckets=[0.000001, 0.000005, 0.00001, 0.00005, 0.0001, 0.0005, 0.001]
    )
    
    buffer_read_duration_seconds = Histogram(
        'truthsync_buffer_read_duration_seconds',
        'Time spent reading from shared buffers',
        buckets=[0.000001, 0.000005, 0.00001, 0.00005, 0.0001, 0.0005, 0.001]
    )
    
    claim_confidence_score = Histogram(
        'truthsync_claim_confidence_score',
        'Distribution of claim confidence scores',
        buckets=[0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
    )
    
    # Gauges
    cache_size = Gauge(
        'truthsync_cache_size',
        'Current number of entries in cache'
    )
    
    cache_hit_rate = Gauge(
        'truthsync_cache_hit_rate',
        'Current cache hit rate (0-1)'
    )
    
    prediction_accuracy = Gauge(
        'truthsync_prediction_accuracy',
        'Current prediction accuracy (0-1)'
    )
    
    active_buffers = Gauge(
        'truthsync_active_buffers',
        'Number of active shared memory buffers',
        ['buffer_type']  # input, output
    )
    
    confidence_threshold = Gauge(
        'truthsync_confidence_threshold',
        'Current adaptive confidence threshold'
    )
    
    # Summary
    end_to_end_latency = Summary(
        'truthsync_end_to_end_latency_seconds',
        'End-to-end latency from input to verified output'
    )
    
    # Info
    system_info = Info(
        'truthsync_system',
        'TruthSync system information'
    )


class IntegrityMonitor:
    """
    Monitors system integrity and exports metrics to Prometheus/Grafana
    """
    
    def __init__(self):
        self.metrics = TruthSyncMetrics()
        self.logger = self._setup_loki_logger()
        
        # Set system info
        self.metrics.system_info.info({
            'version': '1.0.0-poc',
            'architecture': 'hybrid_rust_python',
            'cache_type': 'predictive_lru',
            'verification': 'self_verifying',
            'ml_integration': 'sentinel_ml'
        })
    
    def _setup_loki_logger(self) -> logging.Logger:
        """Setup logger for Loki integration"""
        logger = logging.getLogger('truthsync')
        logger.setLevel(logging.INFO)
        
        # Console handler with Loki format
        handler = logging.StreamHandler()
        handler.setFormatter(LokiFormatter())
        logger.addHandler(handler)
        
        return logger
    
    def record_claim_processing(self, result: str, duration: float, confidence: float):
        """Record claim processing metrics"""
        self.metrics.claims_processed_total.labels(result=result).inc()
        self.metrics.processing_duration_seconds.labels(stage='extraction').observe(duration)
        self.metrics.claim_confidence_score.observe(confidence)
        
        self.logger.info(
            f"Claim processed: result={result}, duration={duration:.6f}s, confidence={confidence:.2f}",
            extra={'confidence': confidence, 'result': result}
        )
    
    def record_prediction(self, was_correct: bool, likelihood: float):
        """Record prediction outcome"""
        outcome = 'correct' if was_correct else 'incorrect'
        self.metrics.predictions_total.labels(outcome=outcome).inc()
        
        self.logger.info(
            f"Prediction: outcome={outcome}, likelihood={likelihood:.2f}",
            extra={'verification_result': was_correct, 'confidence': likelihood}
        )
    
    def record_cache_operation(self, operation: str, result: str):
        """Record cache operation"""
        self.metrics.cache_operations_total.labels(
            operation=operation,
            result=result
        ).inc()
    
    def record_buffer_operation(self, operation: str, duration: float):
        """Record buffer read/write operation"""
        if operation == 'write':
            self.metrics.buffer_write_duration_seconds.observe(duration)
        else:
            self.metrics.buffer_read_duration_seconds.observe(duration)
    
    def update_cache_stats(self, size: int, hit_rate: float):
        """Update cache statistics"""
        self.metrics.cache_size.set(size)
        self.metrics.cache_hit_rate.set(hit_rate)
    
    def update_prediction_accuracy(self, accuracy: float):
        """Update prediction accuracy"""
        self.metrics.prediction_accuracy.set(accuracy)
    
    def update_confidence_threshold(self, threshold: float):
        """Update adaptive confidence threshold"""
        self.metrics.confidence_threshold.set(threshold)
    
    def record_anomaly(self, anomaly_type: str):
        """Record detected anomaly"""
        self.metrics.anomalies_detected_total.labels(anomaly_type=anomaly_type).inc()
        
        self.logger.warning(
            f"Anomaly detected: type={anomaly_type}",
            extra={'anomaly_type': anomaly_type}
        )
    
    def record_ml_update(self):
        """Record ML model update"""
        self.metrics.ml_updates_total.inc()
        self.logger.info("ML model update sent to Sentinel")
    
    def record_end_to_end_latency(self, duration: float):
        """Record end-to-end processing latency"""
        self.metrics.end_to_end_latency.observe(duration)
    
    def update_active_buffers(self, input_count: int, output_count: int):
        """Update active buffer counts"""
        self.metrics.active_buffers.labels(buffer_type='input').set(input_count)
        self.metrics.active_buffers.labels(buffer_type='output').set(output_count)


# Grafana Dashboard JSON (for import)
GRAFANA_DASHBOARD = {
    "dashboard": {
        "title": "TruthSync - Integrity & Performance",
        "panels": [
            {
                "title": "Claims Processing Rate",
                "targets": [{
                    "expr": "rate(truthsync_claims_processed_total[5m])"
                }],
                "type": "graph"
            },
            {
                "title": "Prediction Accuracy",
                "targets": [{
                    "expr": "truthsync_prediction_accuracy"
                }],
                "type": "gauge"
            },
            {
                "title": "Cache Hit Rate",
                "targets": [{
                    "expr": "truthsync_cache_hit_rate"
                }],
                "type": "gauge"
            },
            {
                "title": "Processing Latency (p50, p95, p99)",
                "targets": [
                    {"expr": "histogram_quantile(0.50, truthsync_processing_duration_seconds)"},
                    {"expr": "histogram_quantile(0.95, truthsync_processing_duration_seconds)"},
                    {"expr": "histogram_quantile(0.99, truthsync_processing_duration_seconds)"}
                ],
                "type": "graph"
            },
            {
                "title": "Buffer Operations Latency",
                "targets": [
                    {"expr": "truthsync_buffer_write_duration_seconds"},
                    {"expr": "truthsync_buffer_read_duration_seconds"}
                ],
                "type": "graph"
            },
            {
                "title": "Anomalies Detected",
                "targets": [{
                    "expr": "rate(truthsync_anomalies_detected_total[5m])"
                }],
                "type": "graph"
            },
            {
                "title": "Confidence Score Distribution",
                "targets": [{
                    "expr": "truthsync_claim_confidence_score"
                }],
                "type": "heatmap"
            },
            {
                "title": "Adaptive Threshold",
                "targets": [{
                    "expr": "truthsync_confidence_threshold"
                }],
                "type": "graph"
            }
        ]
    }
}


# Prometheus scrape config
PROMETHEUS_CONFIG = """
# Add to prometheus.yml
scrape_configs:
  - job_name: 'truthsync'
    scrape_interval: 5s
    static_configs:
      - targets: ['localhost:9090']
        labels:
          service: 'truthsync'
          environment: 'production'
"""


# Example usage
if __name__ == '__main__':
    monitor = IntegrityMonitor()
    
    print("="*60)
    print("TRUTHSYNC INTEGRITY MONITORING DEMO")
    print("="*60)
    
    # Simulate operations
    monitor.record_claim_processing('verified', 0.000015, 0.92)
    monitor.record_prediction(True, 0.88)
    monitor.record_cache_operation('get', 'hit')
    monitor.record_buffer_operation('write', 0.000002)
    monitor.update_cache_stats(1500, 0.85)
    monitor.update_prediction_accuracy(0.91)
    monitor.update_confidence_threshold(0.72)
    
    print("\n✅ Metrics recorded successfully")
    print("📊 Metrics available at: http://localhost:9090/metrics")
    print("📈 Grafana dashboard ready for import")
