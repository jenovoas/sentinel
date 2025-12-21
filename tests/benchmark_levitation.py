#!/usr/bin/env python3
"""
Levitation Benchmark: Reactive vs Predictive Buffer Management

Este benchmark demuestra la diferencia crítica entre:
- Sistema REACTIVO: Ajusta buffers DESPUÉS de que llega el tráfico → PACKET DROPS
- Sistema PREDICTIVO (Sentinel): Pre-expande buffers ANTES del burst → ZERO DROPS

El resultado es la "levitación": el tráfico fluye sin tocar los límites.
"""

import asyncio
import sys
import os
import time
from dataclasses import dataclass, field
from typing import List
import json

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from telemetry.traffic_monitor import TrafficMonitor, TrafficMetrics

# Import traffic generator
import importlib.util
spec = importlib.util.spec_from_file_location("traffic_generator", 
                                               os.path.join(os.path.dirname(__file__), "traffic_generator.py"))
traffic_gen_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(traffic_gen_module)
BurstyTrafficGenerator = traffic_gen_module.BurstyTrafficGenerator
TrafficPattern = traffic_gen_module.TrafficPattern


@dataclass
class BufferState:
    """Estado del buffer en un momento dado"""
    timestamp: float
    size_mb: float
    utilization: float  # 0.0 - 1.0
    mode: str  # 'reactive' or 'predictive'


@dataclass
class BenchmarkResults:
    """Resultados del benchmark"""
    mode: str
    total_packets: int = 0
    dropped_packets: int = 0
    avg_latency_ms: float = 0.0
    max_latency_ms: float = 0.0
    avg_throughput_mbps: float = 0.0
    max_throughput_mbps: float = 0.0
    
    # Time series data para visualización
    timestamps: List[float] = field(default_factory=list)
    throughputs: List[float] = field(default_factory=list)
    buffer_sizes: List[float] = field(default_factory=list)
    packet_drops: List[int] = field(default_factory=list)
    latencies: List[float] = field(default_factory=list)


class ReactiveBufferManager:
    """
    Gestor de buffer REACTIVO (tradicional).
    
    Ajusta el tamaño del buffer DESPUÉS de detectar congestión.
    Resultado: Packet drops durante el inicio del burst.
    """
    
    def __init__(self, initial_size_mb: float = 0.5, max_size_mb: float = 10.0):
        self.current_size_mb = initial_size_mb
        self.max_size_mb = max_size_mb
        self.utilization = 0.0
        
    def update(self, incoming_rate_mbps: float) -> BufferState:
        """
        Actualiza el buffer basado en la tasa actual.
        REACTIVO: Solo crece cuando ya hay congestión.
        """
        # Calcular utilización basada en tasa actual vs capacidad
        # Capacidad más realista: 10 Mbps por MB de buffer
        capacity_mbps = self.current_size_mb * 10
        self.utilization = incoming_rate_mbps / capacity_mbps
        
        # REACTIVO: Solo expande si utilización > 80%
        if self.utilization > 0.8 and self.current_size_mb < self.max_size_mb:
            # Crece lentamente (toma tiempo ajustar)
            self.current_size_mb = min(self.max_size_mb, self.current_size_mb * 1.5)
        
        # Si utilización baja, reduce buffer
        elif self.utilization < 0.3:
            self.current_size_mb = max(1.0, self.current_size_mb * 0.9)
        
        return BufferState(
            timestamp=time.time(),
            size_mb=self.current_size_mb,
            utilization=self.utilization,
            mode='reactive'
        )
    
    def calculate_drops(self, incoming_packets: int) -> int:
        """
        Calcula paquetes perdidos si el buffer está saturado.
        """
        if self.utilization > 1.0:
            # Drops proporcionales al exceso de utilización
            drop_rate = (self.utilization - 1.0) / self.utilization
            return int(incoming_packets * drop_rate)
        return 0


class PredictiveBufferManager:
    """
    Gestor de buffer PREDICTIVO (Sentinel).
    
    Pre-expande el buffer ANTES de que llegue el burst.
    Resultado: Zero packet drops.
    """
    
    def __init__(self, initial_size_mb: float = 0.5, max_size_mb: float = 10.0):
        self.current_size_mb = initial_size_mb
        self.max_size_mb = max_size_mb
        self.utilization = 0.0
        self.prediction_active = False
        
    def predict_and_prepare(self, predicted_burst_mbps: float, confidence: float):
        """
        PRE-EXPANDE el buffer basado en predicción.
        
        Args:
            predicted_burst_mbps: Magnitud predicha del burst
            confidence: Confianza de la predicción (0.0 - 1.0)
        """
        if confidence > 0.3:  # Actuar con confianza moderada (30%)
            # Calcular tamaño necesario para el burst predicho (más agresivo)
            required_size = min(self.max_size_mb, predicted_burst_mbps / 5)
            
            # PRE-EXPANDIR instantáneamente (eBPF es nanosegundos)
            self.current_size_mb = required_size
            self.prediction_active = True
            
            print(f"🔮 PREDICCIÓN: Burst de {predicted_burst_mbps:.1f} Mbps detectado!")
            print(f"   → Buffer pre-expandido: {self.current_size_mb:.2f} MB")
    
    def update(self, incoming_rate_mbps: float) -> BufferState:
        """
        Actualiza el buffer (ya está pre-expandido si hubo predicción).
        """
        capacity_mbps = self.current_size_mb * 10
        self.utilization = incoming_rate_mbps / capacity_mbps
        
        # Si el burst terminó, reducir buffer gradualmente
        if self.prediction_active and self.utilization < 0.3:
            self.current_size_mb = max(1.0, self.current_size_mb * 0.95)
            if self.current_size_mb <= 1.1:
                self.prediction_active = False
        
        return BufferState(
            timestamp=time.time(),
            size_mb=self.current_size_mb,
            utilization=self.utilization,
            mode='predictive'
        )
    
    def calculate_drops(self, incoming_packets: int) -> int:
        """
        Calcula drops (debería ser CERO si la predicción fue correcta).
        """
        if self.utilization > 1.0:
            drop_rate = (self.utilization - 1.0) / self.utilization
            return int(incoming_packets * drop_rate)
        return 0


async def run_benchmark(mode: str, duration: float = 30) -> BenchmarkResults:
    """
    Ejecuta benchmark en modo reactivo o predictivo.
    
    Args:
        mode: 'reactive' or 'predictive'
        duration: Duración del test en segundos
    """
    print(f"\n{'='*70}")
    print(f"BENCHMARK: {mode.upper()} MODE")
    print(f"{'='*70}\n")
    
    # Crear monitor
    monitor = TrafficMonitor(window_size=60, sample_interval=0.5)
    
    # Crear buffer manager - PARÁMETROS CALIBRADOS
    if mode == 'reactive':
        buffer_mgr = ReactiveBufferManager(initial_size_mb=0.5, max_size_mb=10.0)
    else:
        buffer_mgr = PredictiveBufferManager(initial_size_mb=0.5, max_size_mb=10.0)
    
    # Resultados
    results = BenchmarkResults(mode=mode)
    
    # Callback para registrar paquetes
    packet_count = 0
    async def packet_handler(size_bytes: int, latency_ms: float):
        nonlocal packet_count
        packet_count += 1
        monitor.record_packet(size_bytes, latency_ms)
    
    # Crear generador
    generator = BurstyTrafficGenerator(packet_callback=packet_handler)
    
    # Patrón de tráfico - CARGA MASIVA
    pattern = TrafficPattern(
        base_rate=1000,
        burst_rate=50000,  # 50x más agresivo
        burst_duration=2,   # Bursts más cortos y violentos
        burst_interval=15,
        precursor_enabled=True,
        precursor_duration=5
    )
    
    # Callback para monitoreo y control de buffer
    async def metrics_callback(metrics: TrafficMetrics):
        throughput_mbps = metrics.throughput_bps / 1_000_000
        
        # PREDICTIVE: Detectar precursores y pre-expandir
        if mode == 'predictive':
            precursors = monitor.detect_precursors()
            
            # DEBUG: Ver qué está pasando
            if precursors.get('severity', 0) > 0.2:
                print(f"🔍 DEBUG: Severity={precursors['severity']:.2f}, Detected={precursors['precursors_detected']}, Active={buffer_mgr.prediction_active}")
            
            if precursors['precursors_detected'] and not buffer_mgr.prediction_active:
                # Predecir magnitud del burst (10x el throughput actual)
                predicted_burst = throughput_mbps * 10
                print(f"🎯 CALLING predict_and_prepare: burst={predicted_burst:.1f} Mbps, severity={precursors['severity']:.2f}")
                buffer_mgr.predict_and_prepare(predicted_burst, precursors['severity'])
        
        # Actualizar buffer (reactivo o predictivo)
        buffer_state = buffer_mgr.update(throughput_mbps)
        
        # Calcular drops
        packets_this_sample = int(metrics.packet_rate * 0.5)  # 0.5s interval
        drops = buffer_mgr.calculate_drops(packets_this_sample)
        
        # Registrar métricas
        results.timestamps.append(metrics.timestamp)
        results.throughputs.append(throughput_mbps)
        results.buffer_sizes.append(buffer_state.size_mb)
        results.packet_drops.append(drops)
        results.latencies.append(metrics.latency_p95)
        
        results.dropped_packets += drops
        
        # Log
        drop_indicator = "🔴" if drops > 0 else "✅"
        print(f"{drop_indicator} Throughput: {throughput_mbps:6.2f} Mbps | "
              f"Buffer: {buffer_state.size_mb:5.2f} MB | "
              f"Util: {buffer_state.utilization*100:5.1f}% | "
              f"Drops: {drops:4d} | "
              f"Total Drops: {results.dropped_packets:6d}")
    
    # Ejecutar
    try:
        await asyncio.wait_for(
            asyncio.gather(
                generator.generate_periodic_burst(pattern, duration=duration),
                monitor.monitoring_loop(callback=metrics_callback)
            ),
            timeout=duration + 5
        )
    except asyncio.TimeoutError:
        generator.stop()
    
    # Calcular estadísticas finales
    stats = monitor.get_summary_stats()
    results.total_packets = packet_count
    results.avg_latency_ms = stats.get('avg_latency_ms', 0)
    results.max_latency_ms = stats.get('max_latency_ms', 0)
    results.avg_throughput_mbps = stats.get('avg_throughput_mbps', 0)
    results.max_throughput_mbps = stats.get('max_throughput_mbps', 0)
    
    return results


async def main():
    """Ejecuta benchmark completo: Reactive vs Predictive"""
    
    print("\n" + "="*70)
    print("SENTINEL LEVITATION BENCHMARK")
    print("="*70)
    print("\nEste benchmark compara:")
    print("  🔴 REACTIVE: Buffer crece DESPUÉS del burst → Packet Drops")
    print("  🟢 PREDICTIVE: Buffer crece ANTES del burst → Zero Drops")
    print("\n" + "="*70)
    
    # Test duration
    duration = 30
    
    # Run reactive benchmark
    reactive_results = await run_benchmark('reactive', duration)
    
    # Wait a bit between tests
    await asyncio.sleep(2)
    
    # Run predictive benchmark
    predictive_results = await run_benchmark('predictive', duration)
    
    # Compare results
    print("\n" + "="*70)
    print("RESULTADOS COMPARATIVOS")
    print("="*70)
    
    print(f"\n{'Métrica':<30} {'Reactive':>15} {'Predictive':>15} {'Mejora':>15}")
    print("-" * 70)
    
    print(f"{'Total Packets':<30} {reactive_results.total_packets:>15,} {predictive_results.total_packets:>15,} {'-':>15}")
    
    print(f"{'Dropped Packets':<30} {reactive_results.dropped_packets:>15,} {predictive_results.dropped_packets:>15,} ", end="")
    if reactive_results.dropped_packets > 0:
        improvement = (1 - predictive_results.dropped_packets / reactive_results.dropped_packets) * 100
        print(f"{improvement:>14.1f}%")
    else:
        print(f"{'N/A':>15}")
    
    print(f"{'Avg Latency (ms)':<30} {reactive_results.avg_latency_ms:>15.2f} {predictive_results.avg_latency_ms:>15.2f} ", end="")
    if reactive_results.avg_latency_ms > 0:
        improvement = (1 - predictive_results.avg_latency_ms / reactive_results.avg_latency_ms) * 100
        print(f"{improvement:>14.1f}%")
    else:
        print(f"{'N/A':>15}")
    
    print(f"{'Max Latency (ms)':<30} {reactive_results.max_latency_ms:>15.2f} {predictive_results.max_latency_ms:>15.2f} {'-':>15}")
    
    print(f"{'Avg Throughput (Mbps)':<30} {reactive_results.avg_throughput_mbps:>15.2f} {predictive_results.avg_throughput_mbps:>15.2f} {'-':>15}")
    
    # Export data for visualization
    export_data = {
        'reactive': {
            'timestamps': reactive_results.timestamps,
            'throughputs': reactive_results.throughputs,
            'buffer_sizes': reactive_results.buffer_sizes,
            'packet_drops': reactive_results.packet_drops,
            'latencies': reactive_results.latencies,
            'total_drops': reactive_results.dropped_packets
        },
        'predictive': {
            'timestamps': predictive_results.timestamps,
            'throughputs': predictive_results.throughputs,
            'buffer_sizes': predictive_results.buffer_sizes,
            'packet_drops': predictive_results.packet_drops,
            'latencies': predictive_results.latencies,
            'total_drops': predictive_results.dropped_packets
        }
    }
    
    output_file = '/tmp/levitation_benchmark_data.json'
    with open(output_file, 'w') as f:
        json.dump(export_data, f, indent=2)
    
    print(f"\n📊 Datos exportados a: {output_file}")
    print("    Usa visualize_levitation.py para generar gráficas")
    
    # Conclusión
    print("\n" + "="*70)
    print("CONCLUSIÓN")
    print("="*70)
    
    if predictive_results.dropped_packets == 0 and reactive_results.dropped_packets > 0:
        print("\n🎉 ¡LEVITACIÓN LOGRADA!")
        print("   El sistema predictivo logró ZERO DROPS mientras el reactivo perdió")
        print(f"   {reactive_results.dropped_packets:,} paquetes.")
        print("\n   El tráfico 'levitó' sobre la infraestructura sin tocar los límites.")
    elif predictive_results.dropped_packets < reactive_results.dropped_packets:
        print(f"\n✅ Mejora significativa: {((1 - predictive_results.dropped_packets / reactive_results.dropped_packets) * 100):.1f}% menos drops")
    else:
        print("\n⚠️  Ajustar parámetros de predicción")
    
    print("\n" + "="*70)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nBenchmark interrumpido por el usuario.")
        sys.exit(0)
