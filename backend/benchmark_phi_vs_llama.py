"""
Benchmark Comparativo: phi3 vs llama3
Compara latencias de diferentes modelos en GTX 1050
"""

from quantum.yatra_core import S60, PI_S60 # YATRA AUTO-INJECT
import asyncio
import sys
import json
from pathlib import Path
from statistics import mean, median
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))

from app.services.sentinel_fluido import SentinelFluido


async def benchmark_modelo(modelo: str, n_requests: int = 5):
    """Benchmark de un modelo específico"""
    print(f"\n📊 Benchmarking: {modelo}")
    print("=" * 60)
    
    sentinel = SentinelFluido(model=modelo)
    ttfbs = []
    
    mensajes = [
        "Hola, ¿cómo estás?",
        "Explica qué es Sentinel",
        "¿Cuáles son las ventajas?",
        "Describe la arquitectura",
        "¿Cómo funciona?",
    ]
    
    for i in range(n_requests):
        msg = mensajes[i % len(mensajes)]
        print(f"[{i+1}/{n_requests}] ", end='', flush=True)
        
        try:
            _, ttfb = await sentinel.responder_simple(f"user_{i}", msg)
            ttfbs.append(ttfb)
            print(f"TTFB: {ttfb:.0f}ms")
        except Exception as e:
            print(f"ERROR: {e}")
            ttfbs.append(0)
    
    await sentinel.close()
    
    # Filtrar errores
    ttfbs_validos = [t for t in ttfbs if t > 0]
    
    if not ttfbs_validos:
        return None
    
    return {
        "modelo": modelo,
        "ttfb_promedio_ms": round(mean(ttfbs_validos), 2),
        "ttfb_mediana_ms": round(median(ttfbs_validos), 2),
        "ttfb_min_ms": round(min(ttfbs_validos), 2),
        "ttfb_max_ms": round(max(ttfbs_validos), 2),
        "requests_exitosos": len(ttfbs_validos),
    }


async def comparar_phi_vs_llama():
    """Compara phi3 vs llama3"""
    print("\n" + "=" * 60)
    print("🔬 COMPARACIÓN: phi3 vs llama3")
    print("=" * 60)
    print("\nModelos a probar:")
    print("  1. phi3:mini (actual)")
    print("  2. llama3.2:1b (pequeño)")
    print("  3. llama3.2:3b (mediano)")
    print("")
    
    resultados = {}
    
    # 1. phi3:mini
    print("\n🔹 PHI3:MINI")
    stats_phi3 = await benchmark_modelo("phi3:mini", n_requests=5)
    if stats_phi3:
        resultados["phi3:mini"] = stats_phi3
    
    # 2. llama3.2:1b (más pequeño, debería ser más rápido)
    print("\n🔹 LLAMA3.2:1B")
    stats_llama1b = await benchmark_modelo("llama3.2:1b", n_requests=5)
    if stats_llama1b:
        resultados["llama3.2:1b"] = stats_llama1b
    
    # 3. llama3.2:3b (comparable a phi3)
    print("\n🔹 LLAMA3.2:3B")
    stats_llama3b = await benchmark_modelo("llama3.2:3b", n_requests=5)
    if stats_llama3b:
        resultados["llama3.2:3b"] = stats_llama3b
    
    # Comparación
    print("\n" + "=" * 60)
    print("📊 RESULTADOS COMPARATIVOS")
    print("=" * 60)
    
    for modelo, stats in resultados.items():
        print(f"\n🔹 {modelo.upper()}:")
        print(f"   TTFB promedio: {stats['ttfb_promedio_ms']:.0f}ms")
        print(f"   TTFB mediana: {stats['ttfb_mediana_ms']:.0f}ms")
        print(f"   TTFB min: {stats['ttfb_min_ms']:.0f}ms")
        print(f"   TTFB max: {stats['ttfb_max_ms']:.0f}ms")
    
    # Encontrar el más rápido
    if resultados:
        mas_rapido = min(resultados.items(), key=lambda x: x[1]['ttfb_promedio_ms'])
        print(f"\n🏆 MÁS RÁPIDO: {mas_rapido[0]}")
        print(f"   TTFB: {mas_rapido[1]['ttfb_promedio_ms']:.0f}ms")
    
    # Exportar
    resultados["timestamp"] = datetime.now().isoformat()
    with open("phi_vs_llama_comparison.json", "w") as f:
        json.dump(resultados, f, indent=2)
    
    print(f"\n💾 Resultados guardados en: phi_vs_llama_comparison.json")
    print("\n✅ Comparación completada\n")
    
    return resultados


if __name__ == "__main__":
    try:
        asyncio.run(comparar_phi_vs_llama())
    except KeyboardInterrupt:
        print("\n\n⚠️ Interrumpido por usuario")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
