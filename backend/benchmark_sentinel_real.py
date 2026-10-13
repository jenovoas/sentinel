"""
Benchmark Real de Sentinel Optimizado
Ejecuta pruebas reales y genera métricas para patente

Hardware: GTX 1050 (3GB VRAM)
Target: TTFB <200ms, token-rate <250ms

Uso:
    python benchmark_sentinel_real.py
"""

from quantum.yatra_core import S60, PI_S60 # YATRA AUTO-INJECT
import asyncio
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.sentinel_optimized import SentinelOptimized


async def test_single_request():
    """Prueba simple de una request"""
    print("🧪 Test 1: Single Request")
    print("=" * 60)
    
    sentinel = SentinelOptimized()
    
    mensaje = "Explica cómo funciona Sentinel Cortex y sus componentes principales"
    
    print(f"Mensaje: {mensaje}\n")
    print("Respuesta:")
    print("-" * 60)
    
    async for chunk, metrics in sentinel.generate_optimized("test_user", mensaje):
        print(chunk, end='', flush=True)
    
    print("\n" + "=" * 60)
    print("\n📊 Métricas:")
    metrics = sentinel.get_patent_metrics()
    for key, value in metrics.items():
        print(f"  {key}: {value}")
    
    await sentinel.close()
    print("\n✅ Test completado\n")


async def benchmark_multiple_requests(n: int = 10):
    """Benchmark con múltiples requests"""
    print(f"🚀 Benchmark: {n} Requests")
    print("=" * 60)
    
    sentinel = SentinelOptimized()
    
    test_messages = [
        "¿Qué es TruthSync?",
        "Explica AIOpsShield",
        "¿Cómo funciona la sanitización?",
        "Describe la arquitectura de Sentinel",
        "¿Qué es AIOpsDoom?",
        "Explica los buffers jerárquicos",
        "¿Cómo se integra con PostgreSQL?",
        "Describe el stack de observabilidad",
        "¿Qué ventajas tiene sobre la competencia?",
        "Explica el sistema de verificación de verdad",
    ]
    
    for i in range(n):
        msg = test_messages[i % len(test_messages)]
        print(f"\n[{i+1}/{n}] {msg}")
        print("-" * 40)
        
        async for chunk, _ in sentinel.generate_optimized(f"user_{i}", msg):
            # Solo mostrar primeros 100 chars
            if len(chunk) < 100:
                print(chunk, end='', flush=True)
        
        print("...")
    
    print("\n" + "=" * 60)
    print("\n📊 MÉTRICAS FINALES (PARA PATENTE):")
    print("=" * 60)
    
    metrics = sentinel.get_patent_metrics()
    
    # Formato bonito
    print(f"\n🎯 TARGETS:")
    print(f"  TTFB target: {metrics['target_ttfb_ms']}ms")
    print(f"  Token-rate target: {metrics['target_token_rate_ms']}ms")
    
    print(f"\n📈 RESULTADOS:")
    print(f"  Total requests: {metrics['total_requests']}")
    print(f"  TTFB p95: {metrics['ttfb_p95_ms']:.0f}ms {'✅' if metrics['meets_ttfb_target'] else '❌'}")
    print(f"  TTFB mean: {metrics['ttfb_mean_ms']:.0f}ms")
    print(f"  Token-rate mean: {metrics['token_rate_mean_ms']:.0f}ms {'✅' if metrics['meets_token_rate_target'] else '❌'}")
    print(f"  Human-like: {metrics['human_like_percentage']:.1f}% {'✅' if metrics['meets_human_standard'] else '❌'}")
    
    print(f"\n{'✅ CUMPLE ESTÁNDARES HUMANOS' if metrics['meets_human_standard'] else '⚠️ NO CUMPLE ESTÁNDARES'}")
    
    # Exportar CSV
    sentinel.export_metrics_csv("sentinel_benchmark_results.csv")
    print(f"\n💾 Métricas exportadas a: sentinel_benchmark_results.csv")
    
    await sentinel.close()
    print("\n✅ Benchmark completado\n")


async def benchmark_stress_test(duration_seconds: int = 60):
    """Stress test durante N segundos"""
    print(f"⚡ Stress Test: {duration_seconds} segundos")
    print("=" * 60)
    
    sentinel = SentinelOptimized()
    
    start_time = asyncio.get_event_loop().time()
    request_count = 0
    
    test_msg = "Test de stress para medir latencia bajo carga"
    
    while (asyncio.get_event_loop().time() - start_time) < duration_seconds:
        async for chunk, _ in sentinel.generate_optimized(f"stress_user_{request_count}", test_msg):
            pass  # Solo recolectar métricas
        
        request_count += 1
        print(f"\rRequests: {request_count}", end='', flush=True)
    
    print(f"\n\n📊 STRESS TEST RESULTS:")
    print("=" * 60)
    
    metrics = sentinel.get_patent_metrics()
    
    print(f"  Duration: {duration_seconds}s")
    print(f"  Total requests: {request_count}")
    print(f"  Requests/sec: {request_count / duration_seconds:.2f}")
    print(f"  TTFB p95: {metrics['ttfb_p95_ms']:.0f}ms")
    print(f"  Degradation: {'✅ Minimal' if metrics['meets_ttfb_target'] else '⚠️ Significant'}")
    
    await sentinel.close()
    print("\n✅ Stress test completado\n")


async def main():
    """Menu principal"""
    print("\n" + "=" * 60)
    print("🛡️  SENTINEL OPTIMIZED - BENCHMARK REAL")
    print("=" * 60)
    print("\nOpciones:")
    print("  1. Test simple (1 request)")
    print("  2. Benchmark (10 requests)")
    print("  3. Benchmark extendido (50 requests)")
    print("  4. Stress test (60 segundos)")
    print("  5. Ejecutar todos")
    print()
    
    choice = input("Selecciona opción (1-5): ").strip()
    
    if choice == "1":
        await test_single_request()
    elif choice == "2":
        await benchmark_multiple_requests(10)
    elif choice == "3":
        await benchmark_multiple_requests(50)
    elif choice == "4":
        await benchmark_stress_test(60)
    elif choice == "5":
        print("\n🚀 Ejecutando todos los tests...\n")
        await test_single_request()
        await benchmark_multiple_requests(10)
        await benchmark_stress_test(30)
    else:
        print("❌ Opción inválida")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⚠️ Benchmark interrumpido por usuario")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
