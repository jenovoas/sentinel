"""
Benchmark Comparativo - Ollama Antes/Después Optimización
Documenta latencias para validar mejoras
"""

import asyncio
import sys
import json
from pathlib import Path
from statistics import mean, median

sys.path.insert(0, str(Path(__file__).parent))

from app.services.sentinel_fluido import SentinelFluido


async def benchmark_completo(modelo: str, n_requests: int = 10):
    """
    Benchmark completo con estadísticas
    
    Args:
        modelo: Nombre del modelo Ollama
        n_requests: Número de requests para promediar
    
    Returns:
        Dict con estadísticas
    """
    print(f"\n📊 Benchmarking: {modelo}")
    print("=" * 60)
    
    sentinel = SentinelFluido(model=modelo)
    ttfbs = []
    
    mensajes_test = [
        "Hola, ¿cómo estás?",
        "Explica qué es Sentinel",
        "¿Cuáles son las ventajas de la optimización?",
        "Describe la arquitectura",
        "¿Cómo funciona el buffer jerárquico?",
    ] * 2  # 10 mensajes
    
    for i in range(n_requests):
        msg = mensajes_test[i % len(mensajes_test)]
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
        return {"error": "No se obtuvieron métricas válidas"}
    
    stats = {
        "modelo": modelo,
        "requests": n_requests,
        "ttfb_promedio_ms": round(mean(ttfbs_validos), 2),
        "ttfb_mediana_ms": round(median(ttfbs_validos), 2),
        "ttfb_min_ms": round(min(ttfbs_validos), 2),
        "ttfb_max_ms": round(max(ttfbs_validos), 2),
        "requests_exitosos": len(ttfbs_validos),
        "requests_fallidos": n_requests - len(ttfbs_validos)
    }
    
    return stats


async def comparar_modelos():
    """Compara modelo actual vs optimizado"""
    print("\n" + "=" * 60)
    print("🔬 COMPARACIÓN OLLAMA - ANTES/DESPUÉS OPTIMIZACIÓN")
    print("=" * 60)
    
    resultados = {}
    
    # 1. Modelo actual (baseline)
    print("\n📌 BASELINE: phi3:mini (modelo actual)")
    stats_baseline = await benchmark_completo("phi3:mini", n_requests=5)
    resultados["baseline"] = stats_baseline
    
    # 2. Modelo optimizado (si está disponible)
    print("\n⚡ OPTIMIZADO: phi3:mini-q4_K_M")
    print("   (Ejecutar 'ollama pull phi3:mini-q4_K_M' si no está)")
    
    try:
        stats_optimizado = await benchmark_completo("phi3:mini-q4_K_M", n_requests=5)
        resultados["optimizado"] = stats_optimizado
    except Exception as e:
        print(f"   ⚠️ Modelo no disponible: {e}")
        stats_optimizado = None
        resultados["optimizado"] = {"error": "Modelo no disponible"}
    
    # 3. Comparación
    print("\n" + "=" * 60)
    print("📊 RESULTADOS COMPARATIVOS")
    print("=" * 60)
    
    if "error" not in stats_baseline:
        print(f"\n🔹 BASELINE (phi3:mini):")
        print(f"   TTFB promedio: {stats_baseline['ttfb_promedio_ms']:.0f}ms")
        print(f"   TTFB mediana: {stats_baseline['ttfb_mediana_ms']:.0f}ms")
        print(f"   TTFB min: {stats_baseline['ttfb_min_ms']:.0f}ms")
        print(f"   TTFB max: {stats_baseline['ttfb_max_ms']:.0f}ms")
    
    if stats_optimizado and "error" not in stats_optimizado:
        print(f"\n⚡ OPTIMIZADO (phi3:mini-q4_K_M):")
        print(f"   TTFB promedio: {stats_optimizado['ttfb_promedio_ms']:.0f}ms")
        print(f"   TTFB mediana: {stats_optimizado['ttfb_mediana_ms']:.0f}ms")
        print(f"   TTFB min: {stats_optimizado['ttfb_min_ms']:.0f}ms")
        print(f"   TTFB max: {stats_optimizado['ttfb_max_ms']:.0f}ms")
        
        # Calcular mejora
        mejora = (
            (stats_baseline['ttfb_promedio_ms'] - stats_optimizado['ttfb_promedio_ms']) 
            / stats_baseline['ttfb_promedio_ms'] 
            * 100
        )
        
        print(f"\n🎯 MEJORA:")
        print(f"   {mejora:.1f}% más rápido")
        print(f"   {stats_baseline['ttfb_promedio_ms'] - stats_optimizado['ttfb_promedio_ms']:.0f}ms reducción")
    
    # 4. Exportar JSON
    with open("ollama_benchmark_comparison.json", "w") as f:
        json.dump(resultados, f, indent=2)
    
    print(f"\n💾 Resultados guardados en: ollama_benchmark_comparison.json")
    print("\n✅ Comparación completada\n")
    
    return resultados


if __name__ == "__main__":
    try:
        asyncio.run(comparar_modelos())
    except KeyboardInterrupt:
        print("\n\n⚠️ Interrumpido por usuario")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
