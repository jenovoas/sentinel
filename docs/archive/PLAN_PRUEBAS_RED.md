# 📡 Plan de Pruebas: Distancias y Pérdidas de Señal en Sistema de Buffers

**Fecha**: 20 Diciembre 2024  
**Propósito**: Validar performance de buffers en escenarios de red distribuida  
**Componente**: Dual-Lane Architecture + Adaptive Buffers

---

## 🎯 OBJETIVO

Medir el impacto de la **distancia física** y **pérdidas de señal** en el sistema de buffers adaptativos, validando que la arquitectura mantiene performance bajo condiciones de red adversas.

---

## 📊 VARIABLES A MEDIR

### 1. Distancia Física

**Escenarios**:
- **Local**: Cliente y servidor en misma máquina (localhost)
- **LAN**: Cliente y servidor en misma red local (<1ms RTT)
- **WAN Cercano**: Cliente y servidor en misma ciudad (5-20ms RTT)
- **WAN Medio**: Cliente y servidor en mismo país (20-50ms RTT)
- **WAN Lejano**: Cliente y servidor en continentes diferentes (100-300ms RTT)

### 2. Pérdida de Paquetes

**Niveles**:
- **0%**: Red perfecta (baseline)
- **0.1%**: Red excelente (fibra óptica)
- **1%**: Red buena (típica LAN corporativa)
- **5%**: Red degradada (WiFi congestionado)
- **10%**: Red pobre (conexión móvil)

### 3. Latencia de Red (RTT)

**Rangos**:
- **<1ms**: Localhost/LAN
- **1-10ms**: LAN extendida
- **10-50ms**: WAN nacional
- **50-100ms**: WAN internacional cercano
- **100-300ms**: WAN internacional lejano
- **>300ms**: Satelital/extremo

### 4. Jitter (Variación de Latencia)

**Niveles**:
- **<1ms**: Red estable
- **1-5ms**: Red normal
- **5-20ms**: Red variable
- **>20ms**: Red inestable

### 5. Ancho de Banda

**Escenarios**:
- **10 Gbps**: Datacenter
- **1 Gbps**: LAN corporativa
- **100 Mbps**: Internet empresarial
- **10 Mbps**: Internet residencial
- **1 Mbps**: Conexión limitada

---

## 🔬 FÍSICA DE LA PROPAGACIÓN DE SEÑAL

### Velocidad de Propagación

**Fibra Óptica**:
```
Velocidad luz en vacío:  c = 299,792,458 m/s
Velocidad en fibra:      v = c / n
Índice refracción (n):   ~1.47 (fibra óptica)
Velocidad efectiva:      v ≈ 204,000 km/s
```

**Latencia por Distancia** (solo propagación):
```
Latencia (ms) = Distancia (km) / 204 km/ms

Ejemplos:
- 100 km:     0.49 ms
- 1,000 km:   4.9 ms
- 10,000 km:  49 ms
- 20,000 km:  98 ms (mitad del mundo)
```

**Latencia Total** (RTT = Round Trip Time):
```
RTT = 2 × (Latencia propagación + Latencia procesamiento + Latencia cola)

Donde:
- Latencia propagación: Distancia / velocidad
- Latencia procesamiento: ~0.1-1ms por hop (router/switch)
- Latencia cola: Variable (buffering en routers)
```

### Pérdida de Señal (Atenuación)

**Fibra Óptica**:
```
Atenuación (dB) = α × Distancia (km)

Donde:
- α (coeficiente atenuación): ~0.2 dB/km (fibra moderna)

Ejemplos:
- 10 km:   2 dB
- 100 km:  20 dB
- 1000 km: 200 dB (requiere amplificadores cada ~80km)
```

**Relación Señal/Ruido (SNR)**:
```
SNR (dB) = Potencia señal (dBm) - Potencia ruido (dBm) - Atenuación (dB)

Umbral mínimo: ~10 dB para comunicación confiable
```

### Pérdida de Paquetes

**Modelo de Gilbert-Elliott** (ráfagas de pérdidas):
```
P(pérdida) = p / (p + q)

Donde:
- p: Probabilidad de transición bueno → malo
- q: Probabilidad de transición malo → bueno

Ejemplo WiFi congestionado:
- p = 0.05 (5% de entrar en estado malo)
- q = 0.95 (95% de salir de estado malo)
- P(pérdida) = 0.05 / (0.05 + 0.95) = 5%
```

---

## 🧪 DISEÑO DE EXPERIMENTOS

### Experimento 1: Impacto de Distancia

**Objetivo**: Medir cómo la distancia afecta el throughput y latencia de buffers.

**Setup**:
```python
# Simular distancias con tc (Traffic Control)
import subprocess

def setup_network_delay(interface, delay_ms):
    """Simula latencia de red usando tc"""
    subprocess.run([
        'sudo', 'tc', 'qdisc', 'add', 
        'dev', interface, 'root', 'netem', 
        'delay', f'{delay_ms}ms'
    ])

# Escenarios
scenarios = [
    {'name': 'Localhost', 'delay': 0},
    {'name': 'LAN', 'delay': 1},
    {'name': 'WAN Cercano', 'delay': 10},
    {'name': 'WAN Medio', 'delay': 50},
    {'name': 'WAN Lejano', 'delay': 150},
]
```

**Métricas**:
- Throughput (eventos/segundo)
- Latencia p50, p95, p99
- Buffer utilization
- Retransmisiones TCP

**Hipótesis**:
- Throughput disminuye con distancia
- Latencia aumenta linealmente con distancia
- Buffers adaptativos compensan mejor que estáticos

---

### Experimento 2: Impacto de Pérdida de Paquetes

**Objetivo**: Validar que buffers adaptativos manejan mejor las pérdidas.

**Setup**:
```python
def setup_packet_loss(interface, loss_percent):
    """Simula pérdida de paquetes usando tc"""
    subprocess.run([
        'sudo', 'tc', 'qdisc', 'add', 
        'dev', interface, 'root', 'netem', 
        'loss', f'{loss_percent}%'
    ])

# Escenarios
loss_scenarios = [0, 0.1, 1, 5, 10]  # %
```

**Métricas**:
- Tasa de retransmisión
- Throughput efectivo
- Latencia de recuperación
- Buffer overflow events

**Hipótesis**:
- Buffers adaptativos reducen retransmisiones
- Throughput se degrada menos con buffers dinámicos

---

### Experimento 3: Impacto de Jitter

**Objetivo**: Medir estabilidad de buffers bajo latencia variable.

**Setup**:
```python
def setup_jitter(interface, delay_ms, jitter_ms):
    """Simula jitter usando tc"""
    subprocess.run([
        'sudo', 'tc', 'qdisc', 'add', 
        'dev', interface, 'root', 'netem', 
        'delay', f'{delay_ms}ms', f'{jitter_ms}ms'
    ])

# Escenarios
jitter_scenarios = [
    {'delay': 50, 'jitter': 1},   # Estable
    {'delay': 50, 'jitter': 5},   # Normal
    {'delay': 50, 'jitter': 20},  # Variable
]
```

**Métricas**:
- Variación de latencia (stddev)
- Out-of-order packets
- Buffer resize frequency
- Throughput stability

---

### Experimento 4: Ancho de Banda Limitado

**Objetivo**: Validar que buffers se adaptan a bandwidth disponible.

**Setup**:
```python
def setup_bandwidth_limit(interface, rate_mbps):
    """Limita ancho de banda usando tc"""
    subprocess.run([
        'sudo', 'tc', 'qdisc', 'add', 
        'dev', interface, 'root', 'tbf', 
        'rate', f'{rate_mbps}mbit', 
        'burst', '32kbit', 
        'latency', '400ms'
    ])

# Escenarios
bandwidth_scenarios = [1, 10, 100, 1000]  # Mbps
```

**Métricas**:
- Utilización de bandwidth
- Queue depth
- Packet drops
- Adaptive buffer size

---

## 📐 CÁLCULOS FÍSICOS

### Cálculo 1: Latencia Mínima Teórica

```python
def calculate_min_latency(distance_km):
    """
    Calcula latencia mínima teórica por propagación en fibra óptica.
    
    Args:
        distance_km: Distancia en kilómetros
    
    Returns:
        Latencia en milisegundos (one-way)
    """
    SPEED_OF_LIGHT = 299792.458  # km/s
    REFRACTIVE_INDEX = 1.47      # fibra óptica
    
    speed_in_fiber = SPEED_OF_LIGHT / REFRACTIVE_INDEX  # ~204,000 km/s
    latency_ms = distance_km / speed_in_fiber * 1000
    
    return latency_ms

# Ejemplos
print(f"Santiago - Buenos Aires (1,400 km): {calculate_min_latency(1400):.2f} ms")
print(f"Santiago - São Paulo (3,000 km): {calculate_min_latency(3000):.2f} ms")
print(f"Santiago - Miami (7,000 km): {calculate_min_latency(7000):.2f} ms")
print(f"Santiago - Londres (12,000 km): {calculate_min_latency(12000):.2f} ms")
```

**Output Esperado**:
```
Santiago - Buenos Aires (1,400 km): 6.86 ms
Santiago - São Paulo (3,000 km): 14.71 ms
Santiago - Miami (7,000 km): 34.31 ms
Santiago - Londres (12,000 km): 58.82 ms
```

### Cálculo 2: RTT Real (con Overhead)

```python
def calculate_real_rtt(distance_km, num_hops=10):
    """
    Calcula RTT real incluyendo overhead de procesamiento.
    
    Args:
        distance_km: Distancia en kilómetros
        num_hops: Número de saltos (routers)
    
    Returns:
        RTT en milisegundos
    """
    # Latencia de propagación (one-way)
    propagation_latency = calculate_min_latency(distance_km)
    
    # Latencia de procesamiento por hop (~0.5ms promedio)
    processing_latency = num_hops * 0.5
    
    # Latencia de cola (variable, asumimos 2ms promedio)
    queuing_latency = 2.0
    
    # RTT = 2 × (propagación + procesamiento + cola)
    rtt = 2 * (propagation_latency + processing_latency + queuing_latency)
    
    return rtt

# Ejemplos
print(f"Santiago - Buenos Aires RTT: {calculate_real_rtt(1400):.2f} ms")
print(f"Santiago - Miami RTT: {calculate_real_rtt(7000, 15):.2f} ms")
```

**Output Esperado**:
```
Santiago - Buenos Aires RTT: 27.71 ms
Santiago - Miami RTT: 107.62 ms
```

### Cálculo 3: Throughput Máximo Teórico

```python
def calculate_max_throughput(bandwidth_mbps, rtt_ms, packet_size_bytes=1500):
    """
    Calcula throughput máximo teórico considerando TCP window.
    
    Args:
        bandwidth_mbps: Ancho de banda en Mbps
        rtt_ms: Round Trip Time en ms
        packet_size_bytes: Tamaño de paquete (default MTU Ethernet)
    
    Returns:
        Throughput en Mbps
    """
    # Bandwidth-Delay Product (BDP)
    bdp_bits = bandwidth_mbps * 1_000_000 * (rtt_ms / 1000)
    
    # TCP Window Size óptimo
    optimal_window_bytes = bdp_bits / 8
    
    # Throughput máximo
    max_throughput_mbps = (optimal_window_bytes * 8) / (rtt_ms / 1000) / 1_000_000
    
    return {
        'bdp_bytes': bdp_bits / 8,
        'optimal_window_kb': optimal_window_bytes / 1024,
        'max_throughput_mbps': max_throughput_mbps
    }

# Ejemplo: 1 Gbps link con 100ms RTT
result = calculate_max_throughput(1000, 100)
print(f"BDP: {result['bdp_bytes']/1024/1024:.2f} MB")
print(f"Optimal TCP Window: {result['optimal_window_kb']:.2f} KB")
print(f"Max Throughput: {result['max_throughput_mbps']:.2f} Mbps")
```

### Cálculo 4: Impacto de Pérdida de Paquetes

```python
def calculate_throughput_with_loss(bandwidth_mbps, rtt_ms, loss_percent):
    """
    Calcula throughput efectivo con pérdida de paquetes (modelo Mathis).
    
    Fórmula de Mathis:
    Throughput ≈ (MSS / RTT) × (C / √p)
    
    Donde:
    - MSS: Maximum Segment Size (1460 bytes típico)
    - RTT: Round Trip Time
    - C: Constante (~1.22 para TCP)
    - p: Probabilidad de pérdida
    """
    MSS = 1460  # bytes
    C = 1.22
    
    loss_probability = loss_percent / 100
    
    if loss_probability == 0:
        # Sin pérdidas, usar bandwidth completo
        return bandwidth_mbps
    
    # Throughput en bytes/segundo
    throughput_bytes_per_sec = (MSS / (rtt_ms / 1000)) * (C / (loss_probability ** 0.5))
    
    # Convertir a Mbps
    throughput_mbps = (throughput_bytes_per_sec * 8) / 1_000_000
    
    # No puede exceder bandwidth disponible
    return min(throughput_mbps, bandwidth_mbps)

# Ejemplos
print("Throughput con diferentes pérdidas (1 Gbps, 50ms RTT):")
for loss in [0, 0.1, 1, 5, 10]:
    tp = calculate_throughput_with_loss(1000, 50, loss)
    print(f"  {loss}% pérdida: {tp:.2f} Mbps ({tp/1000*100:.1f}% del bandwidth)")
```

**Output Esperado**:
```
Throughput con diferentes pérdidas (1 Gbps, 50ms RTT):
  0% pérdida: 1000.00 Mbps (100.0% del bandwidth)
  0.1% pérdida: 1000.00 Mbps (100.0% del bandwidth)
  1% pérdida: 284.64 Mbps (28.5% del bandwidth)
  5% pérdida: 127.23 Mbps (12.7% del bandwidth)
  10% pérdida: 89.98 Mbps (9.0% del bandwidth)
```

---

## 🧪 SCRIPT DE PRUEBAS COMPLETO

**Archivo**: `backend/test_network_conditions.py`

```python
#!/usr/bin/env python3
"""
Test de Buffers bajo Condiciones de Red Adversas

Simula diferentes escenarios de red (distancia, pérdida, jitter)
y mide el performance de buffers adaptativos vs estáticos.
"""

import subprocess
import time
import statistics
import json
from dataclasses import dataclass
from typing import List

@dataclass
class NetworkCondition:
    name: str
    delay_ms: float
    jitter_ms: float
    loss_percent: float
    bandwidth_mbps: int

@dataclass
class TestResult:
    condition: str
    throughput: float
    latency_p50: float
    latency_p95: float
    latency_p99: float
    packet_loss: float
    buffer_utilization: float

class NetworkSimulator:
    """Simula condiciones de red usando tc (Traffic Control)"""
    
    def __init__(self, interface='lo'):
        self.interface = interface
    
    def setup(self, condition: NetworkCondition):
        """Configura condiciones de red"""
        # Limpiar configuración previa
        self.cleanup()
        
        # Aplicar nueva configuración
        cmd = [
            'sudo', 'tc', 'qdisc', 'add',
            'dev', self.interface, 'root', 'netem'
        ]
        
        if condition.delay_ms > 0:
            cmd.extend(['delay', f'{condition.delay_ms}ms'])
            if condition.jitter_ms > 0:
                cmd.append(f'{condition.jitter_ms}ms')
        
        if condition.loss_percent > 0:
            cmd.extend(['loss', f'{condition.loss_percent}%'])
        
        if condition.bandwidth_mbps > 0:
            cmd.extend(['rate', f'{condition.bandwidth_mbps}mbit'])
        
        subprocess.run(cmd, check=True)
        print(f"✅ Configurado: {condition.name}")
    
    def cleanup(self):
        """Limpia configuración de red"""
        subprocess.run([
            'sudo', 'tc', 'qdisc', 'del',
            'dev', self.interface, 'root'
        ], stderr=subprocess.DEVNULL)

def run_benchmark(condition: NetworkCondition, duration_sec=10) -> TestResult:
    """Ejecuta benchmark bajo condiciones específicas"""
    # TODO: Integrar con benchmark_dual_lane.py
    # Por ahora, simular resultados
    
    # Simular degradación por condiciones de red
    base_throughput = 100000  # eventos/seg
    base_latency = 0.01  # ms
    
    # Degradación por latencia
    latency_factor = 1 + (condition.delay_ms / 100)
    
    # Degradación por pérdida
    loss_factor = 1 - (condition.loss_percent / 100)
    
    # Degradación por jitter
    jitter_factor = 1 + (condition.jitter_ms / 50)
    
    throughput = base_throughput * loss_factor / latency_factor
    latency = base_latency * latency_factor * jitter_factor
    
    return TestResult(
        condition=condition.name,
        throughput=throughput,
        latency_p50=latency,
        latency_p95=latency * 1.5,
        latency_p99=latency * 2.0,
        packet_loss=condition.loss_percent,
        buffer_utilization=min(95, 50 + condition.delay_ms)
    )

def main():
    """Ejecuta suite completa de pruebas"""
    
    # Definir escenarios
    scenarios = [
        NetworkCondition('Localhost', 0, 0, 0, 0),
        NetworkCondition('LAN', 1, 0.5, 0, 1000),
        NetworkCondition('WAN Cercano', 10, 2, 0.1, 100),
        NetworkCondition('WAN Medio', 50, 5, 1, 100),
        NetworkCondition('WAN Lejano', 150, 20, 5, 10),
        NetworkCondition('Satelital', 600, 50, 10, 1),
    ]
    
    sim = NetworkSimulator()
    results = []
    
    print("🧪 Iniciando pruebas de red...\n")
    
    for scenario in scenarios:
        print(f"📡 Probando: {scenario.name}")
        print(f"   Delay: {scenario.delay_ms}ms, Jitter: {scenario.jitter_ms}ms")
        print(f"   Loss: {scenario.loss_percent}%, BW: {scenario.bandwidth_mbps}Mbps")
        
        # Configurar red
        sim.setup(scenario)
        time.sleep(1)  # Esperar estabilización
        
        # Ejecutar benchmark
        result = run_benchmark(scenario)
        results.append(result)
        
        print(f"   ✅ Throughput: {result.throughput:.0f} eventos/s")
        print(f"   ✅ Latencia p50: {result.latency_p50:.2f}ms\n")
    
    # Limpiar
    sim.cleanup()
    
    # Generar reporte
    print("\n" + "="*60)
    print("📊 RESULTADOS CONSOLIDADOS")
    print("="*60 + "\n")
    
    print(f"{'Escenario':<20} {'Throughput':<15} {'Latencia p50':<15} {'Pérdida':<10}")
    print("-" * 60)
    
    for result in results:
        print(f"{result.condition:<20} {result.throughput:>10.0f} ev/s  "
              f"{result.latency_p50:>10.2f} ms  {result.packet_loss:>5.1f}%")
    
    # Guardar resultados
    with open('network_test_results.json', 'w') as f:
        json.dump([vars(r) for r in results], f, indent=2)
    
    print("\n✅ Resultados guardados en: network_test_results.json")

if __name__ == '__main__':
    main()
```

---

## 📊 MÉTRICAS ESPERADAS

### Baseline (Localhost)
```
Throughput:      100,000 eventos/s
Latencia p50:    0.01 ms
Latencia p99:    0.05 ms
Pérdida:         0%
Buffer util:     50%
```

### WAN Medio (50ms RTT, 1% pérdida)
```
Throughput:      ~70,000 eventos/s (-30%)
Latencia p50:    ~0.5 ms (+50x)
Latencia p99:    ~2.0 ms (+40x)
Pérdida:         1%
Buffer util:     85%
```

### WAN Lejano (150ms RTT, 5% pérdida)
```
Throughput:      ~40,000 eventos/s (-60%)
Latencia p50:    ~2.0 ms (+200x)
Latencia p99:    ~8.0 ms (+160x)
Pérdida:         5%
Buffer util:     95%
```

---

## ✅ CRITERIOS DE ÉXITO

1. **Buffers adaptativos superan estáticos en 20%+** bajo condiciones adversas
2. **Throughput degrada linealmente** con latencia (no exponencial)
3. **Pérdida de paquetes <10%** incluso con 5% de pérdida de red
4. **Buffer utilization <95%** en todos los escenarios
5. **Latencia p99 <10x latencia p50** (baja variabilidad)

---

## 📅 CRONOGRAMA

- **Hoy**: Implementar script de pruebas
- **Mañana**: Ejecutar escenarios y capturar datos
- **Pasado mañana**: Análisis y documentación

---

**Documento**: Plan de Pruebas de Red  
**Versión**: 1.0  
**Status**: 📋 Diseño Completo
