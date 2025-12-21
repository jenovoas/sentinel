"""
Bursty Traffic Generator: Synthetic Traffic for Training

Genera patrones de tráfico con bursts predecibles y precursores detectables
para entrenar el modelo de predicción.
"""

import asyncio
import random
import math
from typing import Optional, Callable
from dataclasses import dataclass
import time


@dataclass
class TrafficPattern:
    """Configuración de un patrón de tráfico"""
    base_rate: float  # packets/sec baseline
    burst_rate: float  # packets/sec during burst
    burst_duration: float  # seconds
    burst_interval: float  # seconds between bursts
    precursor_enabled: bool = True
    precursor_duration: float = 5.0  # seconds of ramp-up


class BurstyTrafficGenerator:
    """
    Generador de tráfico con bursts predecibles.
    
    Soporta múltiples patrones:
    - Bursts periódicos (predecibles)
    - Bursts con precursores (ramp-up gradual)
    - Bursts aleatorios (impredecibles)
    """
    
    def __init__(self, packet_callback: Callable):
        """
        Args:
            packet_callback: Función a llamar por cada paquete generado
                            Signature: async def callback(size_bytes, latency_ms)
        """
        self.packet_callback = packet_callback
        self.running = False
        
    async def generate_periodic_burst(self, pattern: TrafficPattern, duration: float):
        """
        Genera tráfico con bursts periódicos predecibles.
        
        Args:
            pattern: Configuración del patrón de tráfico
            duration: Duración total de la generación (segundos)
        """
        self.running = True
        start_time = time.time()
        next_burst_time = start_time + pattern.burst_interval
        
        print(f"🚀 Starting periodic burst generation:")
        print(f"   Base rate: {pattern.base_rate} pps")
        print(f"   Burst rate: {pattern.burst_rate} pps")
        print(f"   Burst interval: {pattern.burst_interval}s")
        print(f"   Precursors: {'enabled' if pattern.precursor_enabled else 'disabled'}")
        
        while self.running and (time.time() - start_time) < duration:
            current_time = time.time()
            
            # Determinar tasa actual
            if current_time >= next_burst_time:
                # Estamos en un burst
                time_in_burst = current_time - next_burst_time
                
                if time_in_burst < pattern.burst_duration:
                    # Durante el burst
                    current_rate = pattern.burst_rate
                    phase = "BURST"
                else:
                    # Burst terminado, volver a baseline
                    current_rate = pattern.base_rate
                    next_burst_time = current_time + pattern.burst_interval
                    phase = "baseline"
            
            elif pattern.precursor_enabled and \
                 (next_burst_time - current_time) <= pattern.precursor_duration:
                # Fase de precursor (ramp-up)
                time_to_burst = next_burst_time - current_time
                ramp_progress = 1.0 - (time_to_burst / pattern.precursor_duration)
                current_rate = pattern.base_rate + \
                              (pattern.burst_rate - pattern.base_rate) * ramp_progress
                phase = "precursor"
            else:
                # Baseline normal
                current_rate = pattern.base_rate
                phase = "baseline"
            
            # Generar paquetes según la tasa actual
            packets_this_tick = int(current_rate * 0.01)  # 10ms tick
            
            for _ in range(packets_this_tick):
                # Tamaño de paquete variable (1000-1500 bytes)
                packet_size = random.randint(1000, 1500)
                
                # Latencia base + jitter
                base_latency = 5.0
                jitter = random.gauss(0, 1.0)
                
                # Latencia aumenta durante bursts
                if phase == "BURST":
                    latency = base_latency + 10.0 + jitter
                elif phase == "precursor":
                    latency = base_latency + 2.0 + jitter
                else:
                    latency = base_latency + jitter
                
                await self.packet_callback(packet_size, max(0.1, latency))
            
            # Log de estado
            if random.random() < 0.1:  # 10% de las veces
                print(f"[{phase:10s}] Rate: {current_rate:8.0f} pps | "
                      f"Next burst in: {max(0, next_burst_time - current_time):.1f}s")
            
            await asyncio.sleep(0.01)  # 10ms tick
    
    async def generate_random_burst(self, 
                                   base_rate: float,
                                   max_burst_rate: float,
                                   duration: float):
        """
        Genera tráfico con bursts aleatorios (impredecibles).
        
        Útil para validar que el modelo no genera falsos positivos.
        """
        self.running = True
        start_time = time.time()
        
        print(f"🎲 Starting random burst generation:")
        print(f"   Base rate: {base_rate} pps")
        print(f"   Max burst rate: {max_burst_rate} pps")
        
        while self.running and (time.time() - start_time) < duration:
            # Tasa aleatoria con distribución exponencial
            if random.random() < 0.05:  # 5% chance de burst
                current_rate = random.uniform(base_rate, max_burst_rate)
                phase = "RANDOM BURST"
            else:
                current_rate = base_rate
                phase = "baseline"
            
            packets_this_tick = int(current_rate * 0.01)
            
            for _ in range(packets_this_tick):
                packet_size = random.randint(1000, 1500)
                latency = random.gauss(5.0, 1.0)
                await self.packet_callback(packet_size, max(0.1, latency))
            
            if random.random() < 0.1:
                print(f"[{phase:15s}] Rate: {current_rate:8.0f} pps")
            
            await asyncio.sleep(0.01)
    
    async def generate_realistic_web_traffic(self, duration: float):
        """
        Genera tráfico realista tipo web con patrones diurnos.
        
        Simula:
        - Tráfico bajo durante la noche
        - Ramp-up en la mañana
        - Picos durante horas laborales
        - Bursts ocasionales (eventos especiales)
        """
        self.running = True
        start_time = time.time()
        
        print(f"🌐 Starting realistic web traffic generation")
        
        while self.running and (time.time() - start_time) < duration:
            elapsed = time.time() - start_time
            
            # Simular patrón diurno (ciclo de 60 segundos = 1 "día")
            day_progress = (elapsed % 60) / 60.0
            
            # Curva sinusoidal para simular día/noche
            base_multiplier = 0.3 + 0.7 * math.sin(day_progress * 2 * math.pi)
            
            # Tasa base modulada por hora del día
            base_rate = 1000 * base_multiplier
            
            # Bursts ocasionales (eventos especiales)
            if random.random() < 0.01:  # 1% chance
                current_rate = base_rate * random.uniform(5, 10)
                phase = "EVENT BURST"
            else:
                current_rate = base_rate
                phase = f"day {day_progress:.2f}"
            
            packets_this_tick = int(current_rate * 0.01)
            
            for _ in range(packets_this_tick):
                packet_size = random.randint(500, 2000)
                latency = random.gauss(10.0, 3.0)
                await self.packet_callback(packet_size, max(0.1, latency))
            
            if random.random() < 0.05:
                print(f"[{phase:15s}] Rate: {current_rate:8.0f} pps")
            
            await asyncio.sleep(0.01)
    
    def stop(self):
        """Detiene la generación de tráfico"""
        self.running = False


# Ejemplo de uso integrado con TrafficMonitor
async def demo_burst_prediction():
    """Demo completo: Generador + Monitor + Detección de Precursores"""
    import sys
    import os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
    from telemetry.traffic_monitor import TrafficMonitor
    
    # Crear monitor
    monitor = TrafficMonitor(window_size=60, sample_interval=0.1)
    
    # Callback para registrar paquetes
    async def packet_handler(size_bytes: int, latency_ms: float):
        monitor.record_packet(size_bytes, latency_ms)
    
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
    async def metrics_callback(metrics):
        precursors = monitor.detect_precursors()
        
        if precursors['precursors_detected']:
            print(f"⚠️  PRECURSOR ALERT! Severity: {precursors['severity']:.2f}")
            print(f"    Throughput: {metrics.throughput_bps/1_000_000:.2f} Mbps")
            print(f"    Latency P95: {metrics.latency_p95:.2f} ms")
    
    # Ejecutar generación y monitoreo en paralelo
    print("=" * 60)
    print("DEMO: Burst Prediction Training Data Generation")
    print("=" * 60)
    
    await asyncio.gather(
        generator.generate_periodic_burst(pattern, duration=60),
        monitor.monitoring_loop(callback=metrics_callback)
    )
    
    # Exportar datos para entrenamiento
    monitor.export_to_json('/tmp/burst_training_data.json')
    
    # Mostrar estadísticas
    stats = monitor.get_summary_stats()
    print("\n" + "=" * 60)
    print("SUMMARY STATISTICS")
    print("=" * 60)
    for key, value in stats.items():
        print(f"{key:25s}: {value:.2f}")


if __name__ == "__main__":
    asyncio.run(demo_burst_prediction())
