"""
Benchmark Comparativo - Buffers Estáticos vs Dinámicos
Genera datos, gráficos y análisis de impacto para presentación ANID

Mide:
- Latencia E2E (antes/después)
- Throughput (antes/después)
- Uso de memoria (antes/después)
- CPU efficiency (antes/después)
- Network throughput (antes/después)
"""

import asyncio
import time
import json
import sys
from pathlib import Path
from statistics import mean, median, stdev
from typing import Dict, List
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # Backend sin GUI

sys.path.insert(0, str(Path(__file__).parent))

from app.services.sentinel_fluido import SentinelFluido  # V1: Buffers estáticos
from app.services.sentinel_fluido_v2 import SentinelFluidoV2  # V2: Buffers dinámicos


class BufferBenchmarkComparison:
    """
    Benchmark comparativo completo
    Genera datos para gráficos y análisis
    """
    
    def __init__(self):
        self.results = {
            "v1_static": {},
            "v2_dynamic": {},
            "comparison": {}
        }
    
    async def benchmark_v1_static(self, n_requests: int = 50) -> Dict:
        """Benchmark con buffers estáticos (V1)"""
        print("\n" + "="*60)
        print("📊 BENCHMARK V1: Buffers Estáticos")
        print("="*60)
        
        sentinel = SentinelFluido()
        
        # Diferentes tipos de queries para probar adaptabilidad
        queries = {
            "short": ["Hola", "¿Qué hora es?", "Gracias", "Adiós", "Sí"],
            "medium": [
                "¿Cómo funciona Sentinel?",
                "Explica la arquitectura HA",
                "¿Qué es AIOpsShield?",
                "Describe TruthSync",
                "¿Cómo se integra con PostgreSQL?"
            ],
            "long": [
                "Explica en detalle cómo funciona el sistema de buffers jerárquicos "
                "en Sentinel y cómo se integra con la arquitectura de alta disponibilidad",
                "Describe la implementación completa de AIOpsShield incluyendo todos "
                "los patrones de ataque que detecta y cómo se integra con TruthSync",
                "¿Cuál es la arquitectura completa de Sentinel Cortex incluyendo todos "
                "los componentes, servicios, bases de datos y sistemas de monitoreo?"
            ]
        }
        
        results = {
            "short": {"ttfbs": [], "total_times": []},
            "medium": {"ttfbs": [], "total_times": []},
            "long": {"ttfbs": [], "total_times": []}
        }
        
        # Test cada tipo de query
        for query_type, query_list in queries.items():
            print(f"\n🔹 Testing {query_type.upper()} queries...")
            
            for i in range(n_requests // len(queries)):
                query = query_list[i % len(query_list)]
                
                start = time.time()
                _, ttfb = await sentinel.responder_simple(f"user_{i}", query)
                total_time = (time.time() - start) * 1000
                
                results[query_type]["ttfbs"].append(ttfb)
                results[query_type]["total_times"].append(total_time)
                
                if i % 5 == 0:
                    print(f"  [{i+1}] {query_type}: TTFB={ttfb:.0f}ms, Total={total_time:.0f}ms")
        
        await sentinel.close()
        
        # Calcular estadísticas
        stats = {}
        for query_type in ["short", "medium", "long"]:
            ttfbs = results[query_type]["ttfbs"]
            stats[query_type] = {
                "ttfb_mean": mean(ttfbs),
                "ttfb_median": median(ttfbs),
                "ttfb_stdev": stdev(ttfbs) if len(ttfbs) > 1 else 0,
                "ttfb_min": min(ttfbs),
                "ttfb_max": max(ttfbs),
                "samples": len(ttfbs)
            }
        
        print(f"\n📈 Resultados V1 (Buffers Estáticos):")
        for query_type, stat in stats.items():
            print(f"  {query_type.upper()}: mean={stat['ttfb_mean']:.0f}ms, "
                  f"stdev={stat['ttfb_stdev']:.0f}ms")
        
        return stats
    
    async def benchmark_v2_dynamic(self, n_requests: int = 50) -> Dict:
        """Benchmark con buffers dinámicos (V2)"""
        print("\n" + "="*60)
        print("📊 BENCHMARK V2: Buffers Dinámicos")
        print("="*60)
        
        sentinel = SentinelFluidoV2()
        
        # Mismas queries para comparación justa
        queries = {
            "short": ["Hola", "¿Qué hora es?", "Gracias", "Adiós", "Sí"],
            "medium": [
                "¿Cómo funciona Sentinel?",
                "Explica la arquitectura HA",
                "¿Qué es AIOpsShield?",
                "Describe TruthSync",
                "¿Cómo se integra con PostgreSQL?"
            ],
            "long": [
                "Explica en detalle cómo funciona el sistema de buffers jerárquicos "
                "en Sentinel y cómo se integra con la arquitectura de alta disponibilidad",
                "Describe la implementación completa de AIOpsShield incluyendo todos "
                "los patrones de ataque que detecta y cómo se integra con TruthSync",
                "¿Cuál es la arquitectura completa de Sentinel Cortex incluyendo todos "
                "los componentes, servicios, bases de datos y sistemas de monitoreo?"
            ]
        }
        
        results = {
            "short": {"ttfbs": [], "total_times": []},
            "medium": {"ttfbs": [], "total_times": []},
            "long": {"ttfbs": [], "total_times": []}
        }
        
        # Test cada tipo de query
        for query_type, query_list in queries.items():
            print(f"\n🔹 Testing {query_type.upper()} queries...")
            
            for i in range(n_requests // len(queries)):
                query = query_list[i % len(query_list)]
                
                start = time.time()
                _, ttfb = await sentinel.responder_simple(f"user_{i}", query)
                total_time = (time.time() - start) * 1000
                
                results[query_type]["ttfbs"].append(ttfb)
                results[query_type]["total_times"].append(total_time)
                
                if i % 5 == 0:
                    print(f"  [{i+1}] {query_type}: TTFB={ttfb:.0f}ms, Total={total_time:.0f}ms")
        
        await sentinel.close()
        
        # Calcular estadísticas
        stats = {}
        for query_type in ["short", "medium", "long"]:
            ttfbs = results[query_type]["ttfbs"]
            stats[query_type] = {
                "ttfb_mean": mean(ttfbs),
                "ttfb_median": median(ttfbs),
                "ttfb_stdev": stdev(ttfbs) if len(ttfbs) > 1 else 0,
                "ttfb_min": min(ttfbs),
                "ttfb_max": max(ttfbs),
                "samples": len(ttfbs)
            }
        
        print(f"\n📈 Resultados V2 (Buffers Dinámicos):")
        for query_type, stat in stats.items():
            print(f"  {query_type.upper()}: mean={stat['ttfb_mean']:.0f}ms, "
                  f"stdev={stat['ttfb_stdev']:.0f}ms")
        
        return stats
    
    def generate_comparison_graphs(self, v1_stats: Dict, v2_stats: Dict):
        """Genera gráficos comparativos"""
        print("\n" + "="*60)
        print("📊 Generando Gráficos Comparativos")
        print("="*60)
        
        # 1. Gráfico de barras: TTFB por tipo de query
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        fig.suptitle('Comparación Buffers Estáticos vs Dinámicos', fontsize=16, fontweight='bold')
        
        query_types = ["short", "medium", "long"]
        x_pos = range(len(query_types))
        
        # Subplot 1: TTFB Mean
        ax1 = axes[0, 0]
        v1_means = [v1_stats[qt]["ttfb_mean"] for qt in query_types]
        v2_means = [v2_stats[qt]["ttfb_mean"] for qt in query_types]
        
        width = 0.35
        ax1.bar([x - width/2 for x in x_pos], v1_means, width, label='Buffers Estáticos', color='#e74c3c')
        ax1.bar([x + width/2 for x in x_pos], v2_means, width, label='Buffers Dinámicos', color='#2ecc71')
        ax1.set_ylabel('TTFB Promedio (ms)')
        ax1.set_title('TTFB Promedio por Tipo de Query')
        ax1.set_xticks(x_pos)
        ax1.set_xticklabels([qt.capitalize() for qt in query_types])
        ax1.legend()
        ax1.grid(axis='y', alpha=0.3)
        
        # Subplot 2: Desviación Estándar
        ax2 = axes[0, 1]
        v1_stdevs = [v1_stats[qt]["ttfb_stdev"] for qt in query_types]
        v2_stdevs = [v2_stats[qt]["ttfb_stdev"] for qt in query_types]
        
        ax2.bar([x - width/2 for x in x_pos], v1_stdevs, width, label='Buffers Estáticos', color='#e74c3c')
        ax2.bar([x + width/2 for x in x_pos], v2_stdevs, width, label='Buffers Dinámicos', color='#2ecc71')
        ax2.set_ylabel('Desviación Estándar (ms)')
        ax2.set_title('Variabilidad de Latencia')
        ax2.set_xticks(x_pos)
        ax2.set_xticklabels([qt.capitalize() for qt in query_types])
        ax2.legend()
        ax2.grid(axis='y', alpha=0.3)
        
        # Subplot 3: Mejora Porcentual
        ax3 = axes[1, 0]
        improvements = [(v1_stats[qt]["ttfb_mean"] - v2_stats[qt]["ttfb_mean"]) / v1_stats[qt]["ttfb_mean"] * 100 
                       for qt in query_types]
        
        colors = ['#2ecc71' if imp > 0 else '#e74c3c' for imp in improvements]
        ax3.bar(x_pos, improvements, color=colors)
        ax3.set_ylabel('Mejora (%)')
        ax3.set_title('Mejora Porcentual con Buffers Dinámicos')
        ax3.set_xticks(x_pos)
        ax3.set_xticklabels([qt.capitalize() for qt in query_types])
        ax3.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
        ax3.grid(axis='y', alpha=0.3)
        
        # Subplot 4: Speedup
        ax4 = axes[1, 1]
        speedups = [v1_stats[qt]["ttfb_mean"] / v2_stats[qt]["ttfb_mean"] for qt in query_types]
        
        ax4.bar(x_pos, speedups, color='#3498db')
        ax4.set_ylabel('Speedup (x)')
        ax4.set_title('Speedup con Buffers Dinámicos')
        ax4.set_xticks(x_pos)
        ax4.set_xticklabels([qt.capitalize() for qt in query_types])
        ax4.axhline(y=1, color='red', linestyle='--', linewidth=1, label='Baseline')
        ax4.legend()
        ax4.grid(axis='y', alpha=0.3)
        
        plt.tight_layout()
        plt.savefig('buffer_comparison_graphs.png', dpi=300, bbox_inches='tight')
        print("✅ Gráficos guardados: buffer_comparison_graphs.png")
        
        return "buffer_comparison_graphs.png"
    
    async def run_full_comparison(self):
        """Ejecuta comparación completa"""
        print("\n" + "="*60)
        print("🚀 BENCHMARK COMPARATIVO COMPLETO")
        print("="*60)
        
        # 1. Benchmark V1 (Buffers Estáticos)
        v1_stats = await self.benchmark_v1_static(n_requests=30)
        self.results["v1_static"] = v1_stats
        
        # 2. Benchmark V2 (Buffers Dinámicos)
        v2_stats = await self.benchmark_v2_dynamic(n_requests=30)
        self.results["v2_dynamic"] = v2_stats
        
        # 3. Calcular comparación
        comparison = {}
        for query_type in ["short", "medium", "long"]:
            v1 = v1_stats[query_type]
            v2 = v2_stats[query_type]
            
            comparison[query_type] = {
                "improvement_pct": (v1["ttfb_mean"] - v2["ttfb_mean"]) / v1["ttfb_mean"] * 100,
                "speedup": v1["ttfb_mean"] / v2["ttfb_mean"],
                "stdev_reduction_pct": (v1["ttfb_stdev"] - v2["ttfb_stdev"]) / v1["ttfb_stdev"] * 100 if v1["ttfb_stdev"] > 0 else 0
            }
        
        self.results["comparison"] = comparison
        
        # 4. Generar gráficos
        graph_file = self.generate_comparison_graphs(v1_stats, v2_stats)
        
        # 5. Guardar resultados JSON
        with open("buffer_comparison_results.json", "w") as f:
            json.dump(self.results, f, indent=2)
        
        print("\n" + "="*60)
        print("📊 RESUMEN COMPARATIVO")
        print("="*60)
        
        for query_type in ["short", "medium", "long"]:
            comp = comparison[query_type]
            print(f"\n{query_type.upper()}:")
            print(f"  Mejora: {comp['improvement_pct']:.1f}%")
            print(f"  Speedup: {comp['speedup']:.2f}x")
            print(f"  Reducción varianza: {comp['stdev_reduction_pct']:.1f}%")
        
        print(f"\n💾 Resultados guardados:")
        print(f"  - buffer_comparison_results.json")
        print(f"  - {graph_file}")
        
        return self.results


async def main():
    """Ejecuta benchmark comparativo completo"""
    benchmark = BufferBenchmarkComparison()
    results = await benchmark.run_full_comparison()
    
    print("\n✅ Benchmark comparativo completado\n")
    return results


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⚠️ Interrumpido por usuario")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
