"""
Traffic Monitor: Telemetry Collection for Burst Prediction

Captura métricas de tráfico en tiempo real para alimentar el modelo predictivo.
Métricas clave: throughput, packet rate, queue depth, latency, connection rate.
"""

import asyncio
import time
from dataclasses import dataclass, asdict
from typing import List, Dict, Optional
from collections import deque
import statistics
import json


@dataclass
class TrafficMetrics:
    """Snapshot de métricas de tráfico en un momento dado"""
    timestamp: float
    throughput_bps: float  # bytes per second
    packet_rate: float  # packets per second
    queue_depth: int  # current queue size
    latency_p50: float  # median latency (ms)
    latency_p95: float  # 95th percentile latency (ms)
    latency_p99: float  # 99th percentile latency (ms)
    connection_rate: float  # new connections per second
    active_connections: int


class TrafficMonitor:
    """
    Monitor de tráfico en tiempo real con ventana deslizante.
    
    Mantiene un historial de métricas para análisis de time-series.
    """
    
    def __init__(self, window_size: int = 60, sample_interval: float = 0.1):
        """
        Args:
            window_size: Tamaño de la ventana de historial (en segundos)
            sample_interval: Intervalo de muestreo (en segundos)
        """
        self.window_size = window_size
        self.sample_interval = sample_interval
        
        # Ventana deslizante de métricas
        max_samples = int(window_size / sample_interval)
        self.metrics_history: deque[TrafficMetrics] = deque(maxlen=max_samples)
        
        # Contadores para cálculo de rates
        self._last_sample_time = time.time()
        self._bytes_counter = 0
        self._packets_counter = 0
        self._connections_counter = 0
        
        # Latency tracking
        self._latency_samples: deque[float] = deque(maxlen=1000)
        
        # Estado actual
        self._current_queue_depth = 0
        self._active_connections = 0
        
    def record_packet(self, size_bytes: int, latency_ms: Optional[float] = None):
        """Registra un paquete procesado"""
        self._bytes_counter += size_bytes
        self._packets_counter += 1
        
        if latency_ms is not None:
            self._latency_samples.append(latency_ms)
    
    def record_connection(self, new: bool = True):
        """Registra una nueva conexión o cierre"""
        if new:
            self._connections_counter += 1
            self._active_connections += 1
        else:
            self._active_connections = max(0, self._active_connections - 1)
    
    def update_queue_depth(self, depth: int):
        """Actualiza la profundidad actual de la cola"""
        self._current_queue_depth = depth
    
    def _calculate_percentile(self, data: List[float], percentile: float) -> float:
        """Calcula percentil de una lista de valores"""
        if not data:
            return 0.0
        sorted_data = sorted(data)
        index = int(len(sorted_data) * percentile / 100)
        return sorted_data[min(index, len(sorted_data) - 1)]
    
    async def sample_metrics(self) -> TrafficMetrics:
        """
        Toma una muestra de métricas actuales.
        
        Returns:
            TrafficMetrics con los valores actuales
        """
        current_time = time.time()
        elapsed = current_time - self._last_sample_time
        
        # Calcular rates
        throughput_bps = self._bytes_counter / elapsed if elapsed > 0 else 0
        packet_rate = self._packets_counter / elapsed if elapsed > 0 else 0
        connection_rate = self._connections_counter / elapsed if elapsed > 0 else 0
        
        # Calcular latency percentiles
        latency_list = list(self._latency_samples)
        latency_p50 = self._calculate_percentile(latency_list, 50)
        latency_p95 = self._calculate_percentile(latency_list, 95)
        latency_p99 = self._calculate_percentile(latency_list, 99)
        
        # Crear snapshot
        metrics = TrafficMetrics(
            timestamp=current_time,
            throughput_bps=throughput_bps,
            packet_rate=packet_rate,
            queue_depth=self._current_queue_depth,
            latency_p50=latency_p50,
            latency_p95=latency_p95,
            latency_p99=latency_p99,
            connection_rate=connection_rate,
            active_connections=self._active_connections
        )
        
        # Agregar a historial
        self.metrics_history.append(metrics)
        
        # Reset contadores
        self._bytes_counter = 0
        self._packets_counter = 0
        self._connections_counter = 0
        self._last_sample_time = current_time
        
        return metrics
    
    def get_time_series(self, duration_seconds: int = 60) -> List[TrafficMetrics]:
        """
        Obtiene serie temporal de métricas.
        
        Args:
            duration_seconds: Duración de la ventana a retornar
            
        Returns:
            Lista de TrafficMetrics en orden cronológico
        """
        if not self.metrics_history:
            return []
        
        cutoff_time = time.time() - duration_seconds
        return [m for m in self.metrics_history if m.timestamp >= cutoff_time]
    
    def get_feature_matrix(self, duration_seconds: int = 60) -> Dict[str, List[float]]:
        """
        Obtiene matriz de features para el modelo predictivo.
        
        Returns:
            Dict con listas de valores para cada feature
        """
        time_series = self.get_time_series(duration_seconds)
        
        if not time_series:
            return {
                'throughput': [],
                'packet_rate': [],
                'queue_depth': [],
                'latency': [],
                'connection_rate': []
            }
        
        return {
            'throughput': [m.throughput_bps for m in time_series],
            'packet_rate': [m.packet_rate for m in time_series],
            'queue_depth': [float(m.queue_depth) for m in time_series],
            'latency': [m.latency_p95 for m in time_series],
            'connection_rate': [m.connection_rate for m in time_series]
        }
    
    def detect_precursors(self) -> Dict[str, any]:
        """
        Detecta señales precursoras de un burst.
        
        Analiza tendencias en las últimas muestras para identificar
        patrones que típicamente preceden a un burst.
        
        Returns:
            Dict con señales detectadas y su severidad
        """
        if len(self.metrics_history) < 10:
            return {'precursors_detected': False}
        
        recent = list(self.metrics_history)[-10:]
        
        # Analizar tendencias
        throughput_trend = self._calculate_trend([m.throughput_bps for m in recent])
        latency_trend = self._calculate_trend([m.latency_p95 for m in recent])
        queue_trend = self._calculate_trend([float(m.queue_depth) for m in recent])
        
        # Detectar incrementos sostenidos (precursores)
        precursors = {
            'precursors_detected': False,
            'throughput_increasing': throughput_trend > 0.1,
            'latency_increasing': latency_trend > 0.1,
            'queue_filling': queue_trend > 0.1,
            'severity': 0.0
        }
        
        # Calcular severidad combinada
        severity = 0.0
        if precursors['throughput_increasing']:
            severity += 0.3
        if precursors['latency_increasing']:
            severity += 0.4
        if precursors['queue_filling']:
            severity += 0.3
        
        precursors['severity'] = severity
        precursors['precursors_detected'] = severity > 0.5
        
        return precursors
    
    def _calculate_trend(self, values: List[float]) -> float:
        """
        Calcula tendencia (slope) de una serie de valores.
        
        Returns:
            Valor positivo = tendencia creciente
            Valor negativo = tendencia decreciente
        """
        if len(values) < 2:
            return 0.0
        
        # Simple linear regression slope
        n = len(values)
        x = list(range(n))
        
        x_mean = statistics.mean(x)
        y_mean = statistics.mean(values)
        
        numerator = sum((x[i] - x_mean) * (values[i] - y_mean) for i in range(n))
        denominator = sum((x[i] - x_mean) ** 2 for i in range(n))
        
        if denominator == 0:
            return 0.0
        
        slope = numerator / denominator
        
        # Normalizar por el valor medio para obtener tendencia relativa
        if y_mean != 0:
            return slope / y_mean
        return 0.0
    
    async def monitoring_loop(self, callback=None):
        """
        Loop principal de monitoreo.
        
        Args:
            callback: Función opcional a llamar con cada muestra
        """
        while True:
            metrics = await self.sample_metrics()
            
            if callback:
                await callback(metrics)
            
            # Detectar precursores
            precursors = self.detect_precursors()
            if precursors['precursors_detected']:
                print(f"⚠️  Precursors detected! Severity: {precursors['severity']:.2f}")
            
            await asyncio.sleep(self.sample_interval)
    
    def export_to_json(self, filepath: str):
        """Exporta historial de métricas a JSON"""
        data = [asdict(m) for m in self.metrics_history]
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
    
    def get_summary_stats(self) -> Dict[str, float]:
        """Obtiene estadísticas resumidas del período monitoreado"""
        if not self.metrics_history:
            return {}
        
        throughputs = [m.throughput_bps for m in self.metrics_history]
        latencies = [m.latency_p95 for m in self.metrics_history]
        
        return {
            'avg_throughput_mbps': statistics.mean(throughputs) / 1_000_000,
            'max_throughput_mbps': max(throughputs) / 1_000_000,
            'avg_latency_ms': statistics.mean(latencies),
            'max_latency_ms': max(latencies),
            'total_samples': len(self.metrics_history)
        }


# Ejemplo de uso
async def main():
    monitor = TrafficMonitor(window_size=60, sample_interval=0.1)
    
    async def print_metrics(metrics: TrafficMetrics):
        print(f"[{metrics.timestamp:.2f}] "
              f"Throughput: {metrics.throughput_bps/1_000_000:.2f} Mbps | "
              f"Latency P95: {metrics.latency_p95:.2f} ms | "
              f"Queue: {metrics.queue_depth}")
    
    # Simular tráfico
    async def simulate_traffic():
        for i in range(100):
            # Simular paquetes
            for _ in range(100):
                monitor.record_packet(size_bytes=1500, latency_ms=5.0 + (i % 10))
            
            monitor.update_queue_depth(i % 50)
            await asyncio.sleep(0.01)
    
    # Ejecutar monitoreo y simulación en paralelo
    await asyncio.gather(
        monitor.monitoring_loop(callback=print_metrics),
        simulate_traffic()
    )


if __name__ == "__main__":
    asyncio.run(main())
