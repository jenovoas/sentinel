#!/usr/bin/env python3
"""
Quick Demo: Burst Precursor Detection

Ejecuta una demostración rápida (30 segundos) del sistema de detección
de precursores de bursts.
"""

import asyncio
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from telemetry.traffic_monitor import TrafficMonitor, TrafficMetrics

# Import traffic generator from same directory
import importlib.util
spec = importlib.util.spec_from_file_location("traffic_generator", 
                                               os.path.join(os.path.dirname(__file__), "traffic_generator.py"))
traffic_gen_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(traffic_gen_module)
BurstyTrafficGenerator = traffic_gen_module.BurstyTrafficGenerator
TrafficPattern = traffic_gen_module.TrafficPattern


async def quick_demo():
    """Demo rápido de 30 segundos"""
    
    print("=" * 70)
    print("SENTINEL BURST PREDICTION DEMO")
    print("=" * 70)
    print()
    print("Este demo muestra cómo Sentinel detecta PRECURSORES de bursts")
    print("antes de que ocurran, permitiendo preparación pre-emptiva.")
    print()
    print("Patrón de tráfico:")
    print("  - Baseline: 1,000 packets/sec")
    print("  - Burst: 10,000 packets/sec (10x)")
    print("  - Precursor: 5 segundos de ramp-up antes del burst")
    print("  - Intervalo: Burst cada 15 segundos")
    print()
    print("=" * 70)
    print()
    
    # Crear monitor
    monitor = TrafficMonitor(window_size=60, sample_interval=0.5)
    
    # Callback para registrar paquetes
    packet_count = 0
    async def packet_handler(size_bytes: int, latency_ms: float):
        nonlocal packet_count
        packet_count += 1
        monitor.record_packet(size_bytes, latency_ms)
        
        # Simular queue depth basado en tasa de paquetes
        if packet_count % 100 == 0:
            queue_depth = min(100, packet_count % 1000)
            monitor.update_queue_depth(queue_depth)
    
    # Crear generador
    generator = BurstyTrafficGenerator(packet_callback=packet_handler)
    
    # Patrón de tráfico con bursts predecibles
    pattern = TrafficPattern(
        base_rate=1000,      # 1K pps baseline
        burst_rate=10000,    # 10K pps durante burst
        burst_duration=3,    # 3 segundos de burst
        burst_interval=15,   # cada 15 segundos
        precursor_enabled=True,
        precursor_duration=5  # 5 segundos de ramp-up
    )
    
    # Callback para imprimir métricas
    burst_predictions = []
    
    async def metrics_callback(metrics: TrafficMetrics):
        precursors = monitor.detect_precursors()
        
        throughput_mbps = metrics.throughput_bps / 1_000_000
        
        # Determinar fase
        if precursors['precursors_detected']:
            phase = "⚠️  PRECURSOR"
            burst_predictions.append({
                'timestamp': metrics.timestamp,
                'severity': precursors['severity'],
                'throughput': throughput_mbps
            })
        elif throughput_mbps > 10:  # Durante burst
            phase = "🔥 BURST    "
        else:
            phase = "✓  Baseline "
        
        print(f"{phase} | "
              f"Throughput: {throughput_mbps:6.2f} Mbps | "
              f"Latency P95: {metrics.latency_p95:5.2f} ms | "
              f"Queue: {metrics.queue_depth:3d} | "
              f"Packets: {packet_count:8d}")
        
        if precursors['precursors_detected']:
            print(f"           └─> Severity: {precursors['severity']:.2f} | "
                  f"Throughput↑: {precursors['throughput_increasing']} | "
                  f"Latency↑: {precursors['latency_increasing']} | "
                  f"Queue↑: {precursors['queue_filling']}")
    
    # Ejecutar generación y monitoreo en paralelo
    try:
        await asyncio.wait_for(
            asyncio.gather(
                generator.generate_periodic_burst(pattern, duration=30),
                monitor.monitoring_loop(callback=metrics_callback)
            ),
            timeout=35
        )
    except asyncio.TimeoutError:
        generator.stop()
    
    # Mostrar estadísticas finales
    print()
    print("=" * 70)
    print("RESULTADOS")
    print("=" * 70)
    
    stats = monitor.get_summary_stats()
    print(f"\nEstadísticas de tráfico:")
    print(f"  Throughput promedio: {stats.get('avg_throughput_mbps', 0):.2f} Mbps")
    print(f"  Throughput máximo:   {stats.get('max_throughput_mbps', 0):.2f} Mbps")
    print(f"  Latencia promedio:   {stats.get('avg_latency_ms', 0):.2f} ms")
    print(f"  Latencia máxima:     {stats.get('max_latency_ms', 0):.2f} ms")
    print(f"  Total de muestras:   {stats.get('total_samples', 0)}")
    print(f"  Total de paquetes:   {packet_count:,}")
    
    print(f"\nPrecursores detectados: {len(burst_predictions)}")
    if burst_predictions:
        print("\nDetecciones de precursores:")
        for i, pred in enumerate(burst_predictions, 1):
            print(f"  {i}. Timestamp: {pred['timestamp']:.2f}s | "
                  f"Severity: {pred['severity']:.2f} | "
                  f"Throughput: {pred['throughput']:.2f} Mbps")
    
    print()
    print("=" * 70)
    print("CONCLUSIÓN")
    print("=" * 70)
    print()
    
    if burst_predictions:
        print("✅ El sistema detectó precursores ANTES de los bursts!")
        print("   Esto permite pre-expandir buffers y evitar packet drops.")
        print()
        print("   Próximo paso: Entrenar modelo LSTM para predicción automática.")
    else:
        print("⚠️  No se detectaron precursores suficientes.")
        print("   Ajustar umbrales de detección o duración del test.")
    
    print()
    print("=" * 70)


if __name__ == "__main__":
    try:
        asyncio.run(quick_demo())
    except KeyboardInterrupt:
        print("\n\nDemo interrumpido por el usuario.")
        sys.exit(0)
