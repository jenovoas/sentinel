#!/usr/bin/env python3
"""
Visualización de Levitación: Reactive vs Predictive

Genera gráficas que muestran la diferencia crítica entre sistemas reactivos
y predictivos, demostrando el efecto de "levitación" del tráfico.
"""

import json
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from datetime import datetime
import numpy as np


def load_benchmark_data(filepath='/tmp/levitation_benchmark_data.json'):
    """Carga datos del benchmark"""
    with open(filepath, 'r') as f:
        return json.load(f)


def normalize_timestamps(timestamps):
    """Normaliza timestamps para que empiecen en 0"""
    if not timestamps:
        return []
    start = timestamps[0]
    return [t - start for t in timestamps]


def plot_levitation(data, output_file='docs/levitation_proof.png'):
    """
    Genera la visualización completa de levitación.
    
    Muestra:
    1. Throughput vs tiempo (con área de tráfico)
    2. Buffer size (reactive vs predictive)
    3. Packet drops (barras rojas vs verdes)
    4. Latencia
    """
    
    # Preparar datos
    reactive = data['reactive']
    predictive = data['predictive']
    
    reactive_time = normalize_timestamps(reactive['timestamps'])
    predictive_time = normalize_timestamps(predictive['timestamps'])
    
    # Crear figura con 4 subplots
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle('Sentinel AI-Driven Burst Prediction vs. Reactive Baseline', 
                 fontsize=16, fontweight='bold')
    
    # ========== SUBPLOT 1: Throughput + Buffer Size ==========
    ax1_twin = ax1.twinx()
    
    # Área de tráfico (gris)
    ax1.fill_between(reactive_time, reactive['throughputs'], 
                     alpha=0.3, color='gray', label='Traffic Load')
    
    # Buffer sizes
    ax1_twin.plot(reactive_time, reactive['buffer_sizes'], 
                 'r-', linewidth=2, label='Reactive Buffer', marker='o', markersize=3)
    ax1_twin.plot(predictive_time, predictive['buffer_sizes'], 
                 'g-', linewidth=2, label='Predictive Buffer', marker='s', markersize=3)
    
    ax1.set_xlabel('Time (seconds)', fontsize=12)
    ax1.set_ylabel('Throughput (Mbps)', fontsize=12, color='gray')
    ax1_twin.set_ylabel('Buffer Size (MB)', fontsize=12)
    ax1.set_title('El Momento Crítico: Buffer Pre-expansion', fontsize=14, fontweight='bold')
    ax1.grid(True, alpha=0.3)
    ax1.tick_params(axis='y', labelcolor='gray')
    
    # Leyenda combinada
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax1_twin.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left')
    
    # Marcar el "momento crítico" (cuando predictive expande)
    if len(predictive['buffer_sizes']) > 0:
        # Encontrar cuando el buffer predictivo salta
        for i in range(1, len(predictive['buffer_sizes'])):
            if predictive['buffer_sizes'][i] > predictive['buffer_sizes'][i-1] * 1.5:
                critical_time = predictive_time[i]
                ax1.axvline(x=critical_time, color='gold', linestyle='--', linewidth=2, alpha=0.7)
                ax1.text(critical_time, max(reactive['throughputs']) * 0.9, 
                        '⚡ Prediction\nActivated', 
                        fontsize=10, fontweight='bold', color='gold',
                        ha='center', bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
                break
    
    # ========== SUBPLOT 2: Packet Drops (Barras) ==========
    # Acumular drops por intervalos de tiempo
    def accumulate_drops(timestamps, drops, interval=2):
        """Acumula drops en intervalos de tiempo"""
        if not timestamps:
            return [], []
        
        time_norm = normalize_timestamps(timestamps)
        max_time = max(time_norm)
        bins = np.arange(0, max_time + interval, interval)
        accumulated = []
        
        for i in range(len(bins) - 1):
            total = sum(d for t, d in zip(time_norm, drops) if bins[i] <= t < bins[i+1])
            accumulated.append(total)
        
        return bins[:-1], accumulated
    
    reactive_bins, reactive_drops_acc = accumulate_drops(reactive['timestamps'], reactive['packet_drops'])
    predictive_bins, predictive_drops_acc = accumulate_drops(predictive['timestamps'], predictive['packet_drops'])
    
    width = 0.8
    ax2.bar(reactive_bins, reactive_drops_acc, width=width, color='red', alpha=0.7, label='Reactive Drops')
    ax2.bar(predictive_bins, predictive_drops_acc, width=width, color='green', alpha=0.7, label='Predictive Drops')
    
    ax2.set_xlabel('Time (seconds)', fontsize=12)
    ax2.set_ylabel('Packet Drops (per 2s interval)', fontsize=12)
    ax2.set_title('Packet Drops: Reactive vs Predictive', fontsize=14, fontweight='bold')
    ax2.legend()
    ax2.grid(True, alpha=0.3, axis='y')
    
    # Anotar totales
    ax2.text(0.95, 0.95, f'Total Reactive Drops: {reactive["total_drops"]:,}\nTotal Predictive Drops: {predictive["total_drops"]:,}',
             transform=ax2.transAxes, fontsize=11, verticalalignment='top', horizontalalignment='right',
             bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
    
    # ========== SUBPLOT 3: Latency Comparison ==========
    ax3.plot(reactive_time, reactive['latencies'], 
            'r-', linewidth=2, label='Reactive Latency', alpha=0.7)
    ax3.plot(predictive_time, predictive['latencies'], 
            'g-', linewidth=2, label='Predictive Latency', alpha=0.7)
    
    ax3.set_xlabel('Time (seconds)', fontsize=12)
    ax3.set_ylabel('Latency P95 (ms)', fontsize=12)
    ax3.set_title('Latency Impact', fontsize=14, fontweight='bold')
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    
    # ========== SUBPLOT 4: Buffer Utilization ==========
    # Calcular utilización (throughput / buffer capacity)
    reactive_util = [t / (b * 100) * 100 for t, b in zip(reactive['throughputs'], reactive['buffer_sizes'])]
    predictive_util = [t / (b * 100) * 100 for t, b in zip(predictive['throughputs'], predictive['buffer_sizes'])]
    
    ax4.plot(reactive_time, reactive_util, 
            'r-', linewidth=2, label='Reactive Utilization', alpha=0.7)
    ax4.plot(predictive_time, predictive_util, 
            'g-', linewidth=2, label='Predictive Utilization', alpha=0.7)
    
    # Línea de saturación (100%)
    ax4.axhline(y=100, color='black', linestyle='--', linewidth=1, alpha=0.5, label='Saturation (100%)')
    
    ax4.set_xlabel('Time (seconds)', fontsize=12)
    ax4.set_ylabel('Buffer Utilization (%)', fontsize=12)
    ax4.set_title('Buffer Utilization: Staying Below Saturation', fontsize=14, fontweight='bold')
    ax4.legend()
    ax4.grid(True, alpha=0.3)
    ax4.set_ylim(0, max(max(reactive_util + predictive_util), 120))
    
    # Área de peligro (>100%)
    ax4.fill_between(reactive_time, 100, 150, alpha=0.2, color='red', label='Danger Zone')
    
    plt.tight_layout()
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"\n📊 Visualización guardada en: {output_file}")
    
    return fig


def main():
    """Genera visualización desde datos del benchmark"""
    
    print("\n" + "="*70)
    print("GENERANDO VISUALIZACIÓN DE LEVITACIÓN")
    print("="*70)
    
    try:
        data = load_benchmark_data()
        fig = plot_levitation(data)
        
        print("\n✅ Visualización generada exitosamente!")
        print("\nQué buscar en la gráfica:")
        print("  1. SUBPLOT 1 (arriba izq): La línea verde (Predictive) salta ANTES")
        print("     de que llegue el pico gris (tráfico)")
        print("  2. SUBPLOT 2 (arriba der): Barras rojas (Reactive drops) vs")
        print("     barras verdes (Predictive = ZERO)")
        print("  3. SUBPLOT 4 (abajo der): Predictive se mantiene bajo 100%,")
        print("     Reactive entra en zona roja")
        print("\n" + "="*70)
        
    except FileNotFoundError:
        print("\n❌ Error: No se encontraron datos del benchmark.")
        print("   Ejecuta primero: python tests/benchmark_levitation.py")
    except Exception as e:
        print(f"\n❌ Error: {e}")


if __name__ == "__main__":
    main()
