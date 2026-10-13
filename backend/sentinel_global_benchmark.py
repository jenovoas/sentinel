"""
Sentinel Global Benchmark - Validación Completa
Mide TODOS los componentes del stack para validar mejoras proyectadas

Objetivos:
- E2E Pipeline: <500ms p95 (vs 10,426ms baseline) → 20x speedup
- LLM TTFB: <300ms p95 (latencia humana) → 30x speedup
- Network: >10 Gbps (vs 6.8 Gbps) → 1.5x speedup
- PostgreSQL: >300 qps (vs 100 qps) → 3x speedup
- CPU: <10% idle (vs 15%) → 1.5x efficiency
"""

from quantum.yatra_core import S60, PI_S60 # YATRA AUTO-INJECT
import asyncio
import time
import sys
from pathlib import Path
from statistics import mean, median
from typing import Dict, List
import json

sys.path.insert(0, str(Path(__file__).parent))

from app.services.sentinel_fluido import SentinelFluido


class SentinelGlobalBenchmark:
    """
    Benchmark completo de Sentinel Global
    Valida mejoras en TODOS los componentes
    """
    
    def __init__(self):
        self.results = {}
        self.baseline = {
            "e2e_ms": 10426,
            "llm_ttfb_ms": 10400,
            "network_gbps": 6.8,
            "postgresql_qps": 100,
            "cpu_idle_pct": 15,
            "downtime_min_month": 120  # 2 horas
        }
    
    async def benchmark_e2e_pipeline(self, n_requests: int = 10) -> Dict:
        """
        Benchmark E2E completo (request → response)
        
        Objetivo: <500ms p95 (vs 10,426ms baseline)
        """
        print("\n" + "="*60)
        print("📊 BENCHMARK 1: E2E Pipeline")
        print("="*60)
        
        sentinel = SentinelFluido()
        latencies = []
        
        mensajes = [
            "Hola, ¿cómo estás?",
            "Explica Sentinel",
            "¿Qué es AIOpsShield?",
            "Describe la arquitectura",
            "¿Cómo funciona TruthSync?",
        ] * 2  # 10 mensajes
        
        for i in range(n_requests):
            msg = mensajes[i % len(mensajes)]
            print(f"[{i+1}/{n_requests}] ", end='', flush=True)
            
            start = time.time()
            
            # Simula pipeline completo
            _, ttfb = await sentinel.responder_simple(f"user_{i}", msg)
            
            latency = (time.time() - start) * 1000
            latencies.append(latency)
            print(f"E2E: {latency:.0f}ms")
        
        await sentinel.close()
        
        # Estadísticas
        p50 = median(latencies)
        p95 = sorted(latencies)[int(len(latencies) * 0.95)] if len(latencies) > 20 else max(latencies)
        p99 = sorted(latencies)[int(len(latencies) * 0.99)] if len(latencies) > 100 else max(latencies)
        
        speedup = self.baseline["e2e_ms"] / p50
        meets_target = p95 < 500
        
        print(f"\n📈 Resultados E2E:")
        print(f"   p50: {p50:.0f}ms (objetivo: <300ms)")
        print(f"   p95: {p95:.0f}ms (objetivo: <500ms)")
        print(f"   p99: {p99:.0f}ms (objetivo: <1000ms)")
        print(f"   Speedup: {speedup:.1f}x (objetivo: >20x)")
        print(f"   Estado: {'✅ CUMPLE' if meets_target else '❌ NO CUMPLE'}")
        
        return {
            "p50_ms": p50,
            "p95_ms": p95,
            "p99_ms": p99,
            "speedup": speedup,
            "meets_target": meets_target,
            "target_p95_ms": 500
        }
    
    async def benchmark_llm_ttfb(self, n_requests: int = 20) -> Dict:
        """
        Benchmark LLM TTFB (Time To First Byte)
        
        Objetivo: <300ms p95 (latencia humana)
        """
        print("\n" + "="*60)
        print("📊 BENCHMARK 2: LLM TTFB (Latencia Humana)")
        print("="*60)
        
        sentinel = SentinelFluido()
        ttfbs = []
        
        for i in range(n_requests):
            print(f"[{i+1}/{n_requests}] ", end='', flush=True)
            
            _, ttfb = await sentinel.responder_simple(f"user_{i}", "Test rápido")
            ttfbs.append(ttfb)
            print(f"TTFB: {ttfb:.0f}ms")
        
        await sentinel.close()
        
        # Estadísticas
        p50 = median(ttfbs)
        p95 = sorted(ttfbs)[int(len(ttfbs) * 0.95)]
        
        speedup = self.baseline["llm_ttfb_ms"] / p50
        meets_target = p95 < 300
        
        print(f"\n📈 Resultados LLM TTFB:")
        print(f"   p50: {p50:.0f}ms (objetivo: <200ms)")
        print(f"   p95: {p95:.0f}ms (objetivo: <300ms)")
        print(f"   Speedup: {speedup:.1f}x (objetivo: >30x)")
        print(f"   Estado: {'✅ CUMPLE' if meets_target else '❌ NO CUMPLE'}")
        
        return {
            "p50_ms": p50,
            "p95_ms": p95,
            "speedup": speedup,
            "meets_target": meets_target,
            "target_p95_ms": 300
        }
    
    async def benchmark_network_throughput(self) -> Dict:
        """
        Benchmark Red Interna (requiere iperf3)
        
        Objetivo: >10 Gbps (vs 6.8 Gbps baseline)
        """
        print("\n" + "="*60)
        print("📊 BENCHMARK 3: Network Throughput")
        print("="*60)
        
        try:
            import subprocess
            
            # Verificar si iperf3 está disponible
            result = subprocess.run(
                ["which", "iperf3"],
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                print("⚠️ iperf3 no instalado, saltando benchmark de red")
                return {
                    "throughput_gbps": 0,
                    "speedup": 0,
                    "meets_target": False,
                    "skipped": True
                }
            
            # Ejecutar iperf3 (requiere servidor corriendo)
            print("   Ejecutando iperf3 (10 segundos)...")
            result = subprocess.run(
                ["iperf3", "-c", "localhost", "-t", "10", "-J"],
                capture_output=True,
                text=True,
                timeout=15
            )
            
            data = json.loads(result.stdout)
            throughput_bps = data["end"]["sum_received"]["bits_per_second"]
            throughput_gbps = throughput_bps / 1e9
            
            speedup = throughput_gbps / self.baseline["network_gbps"]
            meets_target = throughput_gbps > 10
            
            print(f"\n📈 Resultados Network:")
            print(f"   Throughput: {throughput_gbps:.2f} Gbps (objetivo: >10 Gbps)")
            print(f"   Speedup: {speedup:.2f}x (objetivo: >1.5x)")
            print(f"   Estado: {'✅ CUMPLE' if meets_target else '❌ NO CUMPLE'}")
            
            return {
                "throughput_gbps": throughput_gbps,
                "speedup": speedup,
                "meets_target": meets_target,
                "target_gbps": 10
            }
            
        except Exception as e:
            print(f"⚠️ Error en benchmark de red: {e}")
            return {
                "throughput_gbps": 0,
                "speedup": 0,
                "meets_target": False,
                "error": str(e)
            }
    
    async def benchmark_postgresql_qps(self) -> Dict:
        """
        Benchmark PostgreSQL QPS (requiere pgbench)
        
        Objetivo: >300 qps (vs 100 qps baseline)
        """
        print("\n" + "="*60)
        print("📊 BENCHMARK 4: PostgreSQL QPS")
        print("="*60)
        
        try:
            import subprocess
            
            # Verificar si pgbench está disponible
            result = subprocess.run(
                ["which", "pgbench"],
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                print("⚠️ pgbench no instalado, saltando benchmark de PostgreSQL")
                return {
                    "qps": 0,
                    "speedup": 0,
                    "meets_target": False,
                    "skipped": True
                }
            
            # Ejecutar pgbench
            print("   Ejecutando pgbench (30 segundos)...")
            result = subprocess.run(
                [
                    "pgbench",
                    "-h", "localhost",
                    "-U", "sentinel",
                    "-d", "sentinel_db",
                    "-T", "30",
                    "-c", "10",
                    "-j", "4",
                ],
                capture_output=True,
                text=True,
                timeout=40
            )
            
            # Parsear output
            qps = 0
            for line in result.stdout.split("\n"):
                if "tps" in line:
                    qps = float(line.split("=")[1].split()[0])
                    break
            
            speedup = qps / self.baseline["postgresql_qps"]
            meets_target = qps > 300
            
            print(f"\n📈 Resultados PostgreSQL:")
            print(f"   QPS: {qps:.0f} (objetivo: >300)")
            print(f"   Speedup: {speedup:.2f}x (objetivo: >3x)")
            print(f"   Estado: {'✅ CUMPLE' if meets_target else '❌ NO CUMPLE'}")
            
            return {
                "qps": qps,
                "speedup": speedup,
                "meets_target": meets_target,
                "target_qps": 300
            }
            
        except Exception as e:
            print(f"⚠️ Error en benchmark de PostgreSQL: {e}")
            return {
                "qps": 0,
                "speedup": 0,
                "meets_target": False,
                "error": str(e)
            }
    
    async def benchmark_cpu_efficiency(self) -> Dict:
        """
        Benchmark CPU Efficiency
        
        Objetivo: <10% idle (vs 15% baseline)
        """
        print("\n" + "="*60)
        print("📊 BENCHMARK 5: CPU Efficiency")
        print("="*60)
        
        try:
            import psutil
            
            print("   Midiendo CPU (10 segundos)...")
            cpu_samples = []
            for i in range(10):
                cpu = psutil.cpu_percent(interval=1)
                cpu_samples.append(cpu)
                print(f"   [{i+1}/10] CPU: {cpu:.1f}%")
            
            cpu_avg = mean(cpu_samples)
            efficiency = self.baseline["cpu_idle_pct"] / cpu_avg
            meets_target = cpu_avg < 10
            
            print(f"\n📈 Resultados CPU:")
            print(f"   CPU idle: {cpu_avg:.1f}% (objetivo: <10%)")
            print(f"   Efficiency: {efficiency:.2f}x (objetivo: >1.5x)")
            print(f"   Estado: {'✅ CUMPLE' if meets_target else '❌ NO CUMPLE'}")
            
            return {
                "cpu_idle_pct": cpu_avg,
                "efficiency": efficiency,
                "meets_target": meets_target,
                "target_cpu_pct": 10
            }
            
        except Exception as e:
            print(f"⚠️ Error en benchmark de CPU: {e}")
            return {
                "cpu_idle_pct": 0,
                "efficiency": 0,
                "meets_target": False,
                "error": str(e)
            }
    
    async def run_all_benchmarks(self):
        """
        Ejecuta TODOS los benchmarks
        """
        print("\n" + "="*60)
        print("🚀 SENTINEL GLOBAL - Benchmark Completo")
        print("="*60)
        print("\nBaseline:")
        print(f"   E2E: {self.baseline['e2e_ms']}ms")
        print(f"   LLM TTFB: {self.baseline['llm_ttfb_ms']}ms")
        print(f"   Network: {self.baseline['network_gbps']} Gbps")
        print(f"   PostgreSQL: {self.baseline['postgresql_qps']} qps")
        print(f"   CPU: {self.baseline['cpu_idle_pct']}%")
        
        results = {}
        
        # 1. E2E Pipeline (CRÍTICO)
        results["e2e"] = await self.benchmark_e2e_pipeline()
        
        # 2. LLM TTFB (CRÍTICO)
        results["llm"] = await self.benchmark_llm_ttfb()
        
        # 3. Network Throughput (OPCIONAL)
        results["network"] = await self.benchmark_network_throughput()
        
        # 4. PostgreSQL QPS (OPCIONAL)
        results["postgresql"] = await self.benchmark_postgresql_qps()
        
        # 5. CPU Efficiency
        results["cpu"] = await self.benchmark_cpu_efficiency()
        
        # Resumen Final
        print("\n" + "="*60)
        print("📊 RESUMEN FINAL - SENTINEL GLOBAL")
        print("="*60)
        
        # Contar cuántos cumplen
        total = len(results)
        passed = sum(1 for r in results.values() if r.get("meets_target", False))
        
        print(f"\n✅ Benchmarks cumplidos: {passed}/{total}")
        
        for name, result in results.items():
            if result.get("skipped"):
                print(f"   ⏭️  {name.upper()}: SALTADO")
            elif result.get("meets_target"):
                print(f"   ✅ {name.upper()}: CUMPLE")
            else:
                print(f"   ❌ {name.upper()}: NO CUMPLE")
        
        # Speedup total (E2E es el más importante)
        if results["e2e"]["meets_target"]:
            print(f"\n🎯 SPEEDUP TOTAL E2E: {results['e2e']['speedup']:.1f}x")
            print(f"   (Objetivo: >20x)")
        
        # Exportar JSON
        with open("sentinel_global_benchmark_results.json", "w") as f:
            json.dump({
                "baseline": self.baseline,
                "results": results,
                "summary": {
                    "total_benchmarks": total,
                    "passed": passed,
                    "pass_rate": passed / total * 100
                }
            }, f, indent=2)
        
        print(f"\n💾 Resultados guardados en: sentinel_global_benchmark_results.json")
        
        return results


async def main():
    """Ejecuta benchmark completo"""
    benchmark = SentinelGlobalBenchmark()
    results = await benchmark.run_all_benchmarks()
    
    print("\n✅ Benchmark completo\n")
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
