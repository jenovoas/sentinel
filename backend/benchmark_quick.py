"""
Benchmark Rápido - Buffers Estáticos vs Dinámicos
Versión simplificada para validación rápida (2-3 minutos)
"""

import asyncio
import time
import sys
from pathlib import Path
from statistics import mean, median

sys.path.insert(0, str(Path(__file__).parent))

from app.services.sentinel_fluido import SentinelFluido  # V1
from app.services.sentinel_fluido_v2 import SentinelFluidoV2  # V2


async def quick_benchmark():
    """Benchmark rápido con pocas muestras"""
    print("\n" + "="*60)
    print("🚀 BENCHMARK RÁPIDO - Buffers V1 vs V2")
    print("="*60)
    
    # Queries de prueba (una de cada tipo)
    queries = {
        "short": "Hola",
        "medium": "¿Cómo funciona Sentinel?",
        "long": "Explica en detalle la arquitectura completa de Sentinel"
    }
    
    results = {
        "v1": {},
        "v2": {}
    }
    
    # 1. BENCHMARK V1 (Buffers Estáticos)
    print("\n📊 V1: Buffers Estáticos")
    print("-" * 60)
    
    sentinel_v1 = SentinelFluido()
    
    for qtype, query in queries.items():
        ttfbs = []
        print(f"\n{qtype.upper()}:")
        
        for i in range(5):  # Solo 5 muestras por tipo
            _, ttfb = await sentinel_v1.responder_simple(f"user_{i}", query)
            ttfbs.append(ttfb)
            print(f"  [{i+1}/5] TTFB: {ttfb:.0f}ms")
        
        results["v1"][qtype] = {
            "mean": mean(ttfbs),
            "median": median(ttfbs),
            "min": min(ttfbs),
            "max": max(ttfbs)
        }
    
    await sentinel_v1.close()
    
    # 2. BENCHMARK V2 (Buffers Dinámicos)
    print("\n📊 V2: Buffers Dinámicos")
    print("-" * 60)
    
    sentinel_v2 = SentinelFluidoV2()
    
    for qtype, query in queries.items():
        ttfbs = []
        print(f"\n{qtype.upper()}:")
        
        for i in range(5):  # Solo 5 muestras por tipo
            _, ttfb = await sentinel_v2.responder_simple(f"user_{i}", query)
            ttfbs.append(ttfb)
            print(f"  [{i+1}/5] TTFB: {ttfb:.0f}ms")
        
        results["v2"][qtype] = {
            "mean": mean(ttfbs),
            "median": median(ttfbs),
            "min": min(ttfbs),
            "max": max(ttfbs)
        }
    
    await sentinel_v2.close()
    
    # 3. COMPARACIÓN
    print("\n" + "="*60)
    print("📊 RESULTADOS COMPARATIVOS")
    print("="*60)
    
    for qtype in ["short", "medium", "long"]:
        v1 = results["v1"][qtype]
        v2 = results["v2"][qtype]
        
        improvement = (v1["mean"] - v2["mean"]) / v1["mean"] * 100
        speedup = v1["mean"] / v2["mean"]
        
        print(f"\n{qtype.upper()}:")
        print(f"  V1 (Estático):  {v1['mean']:.0f}ms (min: {v1['min']:.0f}ms, max: {v1['max']:.0f}ms)")
        print(f"  V2 (Dinámico):  {v2['mean']:.0f}ms (min: {v2['min']:.0f}ms, max: {v2['max']:.0f}ms)")
        print(f"  Mejora: {improvement:+.1f}% ({speedup:.2f}x speedup)")
    
    # 4. GUARDAR RESULTADOS
    import json
    with open("benchmark_quick_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"\n💾 Resultados guardados: benchmark_quick_results.json")
    print("\n✅ Benchmark completado\n")
    
    return results


if __name__ == "__main__":
    try:
        asyncio.run(quick_benchmark())
    except KeyboardInterrupt:
        print("\n\n⚠️ Interrumpido por usuario")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
