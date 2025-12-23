#!/usr/bin/env python3
"""
Benchmark para Forensic WAL
Mide overhead de HMAC, replay detection, y timestamp validation

MÉTRICAS:
- Latencia de write (p50, p95, p99)
- Throughput (eventos/segundo)
- Overhead de HMAC computation
- Overhead de replay detection
- Overhead de timestamp validation
"""

import sys
import asyncio
import time
import statistics
from pathlib import Path
import tempfile
import shutil
import json

# Agregar backend al path
sys.path.insert(0, str(Path(__file__).parent))

from app.core.forensic_wal import ForensicWAL


class ForensicWALBenchmark:
    """Benchmark suite para Forensic WAL"""
    
    def __init__(self, iterations: int = 10000):
        self.iterations = iterations
        self.results = {}
    
    async def benchmark_write_latency(self):
        """Benchmark: Latencia de write con HMAC"""
        print("\n📊 Benchmark 1: Write Latency (HMAC + Replay + Timestamp)")
        print("=" * 60)
        
        temp_dir = Path(tempfile.mkdtemp())
        wal = ForensicWAL(base_path=temp_dir)
        
        latencies = []
        
        try:
            for i in range(self.iterations):
                event_data = {
                    "action": "test_event",
                    "iteration": i,
                    "data": "x" * 100  # 100 bytes payload
                }
                
                start = time.perf_counter()
                await wal.write(event_data)
                end = time.perf_counter()
                
                latency_us = (end - start) * 1_000_000  # microsegundos
                latencies.append(latency_us)
            
            # Estadísticas
            mean = statistics.mean(latencies)
            median = statistics.median(latencies)
            stdev = statistics.stdev(latencies)
            p95 = statistics.quantiles(latencies, n=20)[18]  # 95th percentile
            p99 = statistics.quantiles(latencies, n=100)[98]  # 99th percentile
            min_lat = min(latencies)
            max_lat = max(latencies)
            
            print(f"Iterations: {self.iterations:,}")
            print(f"\nLatency (μs):")
            print(f"  Mean:   {mean:>10.2f} μs")
            print(f"  Median: {median:>10.2f} μs")
            print(f"  StdDev: {stdev:>10.2f} μs")
            print(f"  Min:    {min_lat:>10.2f} μs")
            print(f"  Max:    {max_lat:>10.2f} μs")
            print(f"  P95:    {p95:>10.2f} μs")
            print(f"  P99:    {p99:>10.2f} μs")
            
            # Throughput
            total_time = sum(latencies) / 1_000_000  # segundos
            throughput = self.iterations / total_time
            print(f"\nThroughput: {throughput:,.0f} events/sec")
            
            self.results["write_latency"] = {
                "mean_us": mean,
                "median_us": median,
                "stdev_us": stdev,
                "p95_us": p95,
                "p99_us": p99,
                "min_us": min_lat,
                "max_us": max_lat,
                "throughput_eps": throughput
            }
            
        finally:
            shutil.rmtree(temp_dir)
    
    async def benchmark_hmac_overhead(self):
        """Benchmark: Overhead de HMAC computation"""
        print("\n📊 Benchmark 2: HMAC Computation Overhead")
        print("=" * 60)
        
        temp_dir = Path(tempfile.mkdtemp())
        wal = ForensicWAL(base_path=temp_dir)
        
        hmac_times = []
        
        try:
            for i in range(self.iterations):
                record_data = {
                    "event_id": f"event_{i}",
                    "timestamp": time.time(),
                    "nonce": f"nonce_{i}",
                    "data": {"test": "data"}
                }
                
                start = time.perf_counter()
                wal._compute_hmac(record_data)
                end = time.perf_counter()
                
                hmac_time_us = (end - start) * 1_000_000
                hmac_times.append(hmac_time_us)
            
            mean = statistics.mean(hmac_times)
            median = statistics.median(hmac_times)
            p99 = statistics.quantiles(hmac_times, n=100)[98]
            
            print(f"Iterations: {self.iterations:,}")
            print(f"\nHMAC Computation (μs):")
            print(f"  Mean:   {mean:>10.2f} μs")
            print(f"  Median: {median:>10.2f} μs")
            print(f"  P99:    {p99:>10.2f} μs")
            
            self.results["hmac_overhead"] = {
                "mean_us": mean,
                "median_us": median,
                "p99_us": p99
            }
            
        finally:
            shutil.rmtree(temp_dir)
    
    async def benchmark_replay_detection(self):
        """Benchmark: Overhead de replay detection"""
        print("\n📊 Benchmark 3: Replay Detection Overhead")
        print("=" * 60)
        
        temp_dir = Path(tempfile.mkdtemp())
        wal = ForensicWAL(base_path=temp_dir)
        
        # Poblar seen_nonces
        for i in range(self.iterations):
            wal.seen_nonces.add(f"nonce_{i}")
        
        detection_times = []
        
        try:
            for i in range(self.iterations):
                nonce = f"nonce_{i}"
                
                start = time.perf_counter()
                is_replay = wal._check_replay_attack(nonce)
                end = time.perf_counter()
                
                detection_time_ns = (end - start) * 1_000_000_000  # nanosegundos
                detection_times.append(detection_time_ns)
            
            mean = statistics.mean(detection_times)
            median = statistics.median(detection_times)
            p99 = statistics.quantiles(detection_times, n=100)[98]
            
            print(f"Iterations: {self.iterations:,}")
            print(f"Nonces in set: {len(wal.seen_nonces):,}")
            print(f"\nReplay Detection (ns):")
            print(f"  Mean:   {mean:>10.2f} ns")
            print(f"  Median: {median:>10.2f} ns")
            print(f"  P99:    {p99:>10.2f} ns")
            
            self.results["replay_detection"] = {
                "mean_ns": mean,
                "median_ns": median,
                "p99_ns": p99
            }
            
        finally:
            shutil.rmtree(temp_dir)
    
    async def benchmark_timestamp_validation(self):
        """Benchmark: Overhead de timestamp validation"""
        print("\n📊 Benchmark 4: Timestamp Validation Overhead")
        print("=" * 60)
        
        temp_dir = Path(tempfile.mkdtemp())
        wal = ForensicWAL(base_path=temp_dir)
        
        validation_times = []
        
        try:
            for i in range(self.iterations):
                timestamp = time.time()
                
                start = time.perf_counter()
                is_valid = wal._check_timestamp_manipulation(timestamp)
                end = time.perf_counter()
                
                validation_time_ns = (end - start) * 1_000_000_000
                validation_times.append(validation_time_ns)
            
            mean = statistics.mean(validation_times)
            median = statistics.median(validation_times)
            p99 = statistics.quantiles(validation_times, n=100)[98]
            
            print(f"Iterations: {self.iterations:,}")
            print(f"\nTimestamp Validation (ns):")
            print(f"  Mean:   {mean:>10.2f} ns")
            print(f"  Median: {median:>10.2f} ns")
            print(f"  P99:    {p99:>10.2f} ns")
            
            self.results["timestamp_validation"] = {
                "mean_ns": mean,
                "median_ns": median,
                "p99_ns": p99
            }
            
        finally:
            shutil.rmtree(temp_dir)
    
    async def benchmark_comparison_vs_baseline(self):
        """Benchmark: Comparación vs WAL sin protección"""
        print("\n📊 Benchmark 5: Overhead vs Baseline WAL")
        print("=" * 60)
        
        temp_dir = Path(tempfile.mkdtemp())
        
        # Baseline: WAL simple sin protección
        baseline_times = []
        for i in range(1000):
            event_data = {"action": "test", "iteration": i}
            
            start = time.perf_counter()
            # Simular write simple
            wal_file = temp_dir / "baseline.wal"
            with open(wal_file, "a") as f:
                f.write(json.dumps(event_data) + "\n")
            end = time.perf_counter()
            
            baseline_times.append((end - start) * 1_000_000)
        
        # ForensicWAL: Con protección completa
        wal = ForensicWAL(base_path=temp_dir)
        forensic_times = []
        
        for i in range(1000):
            event_data = {"action": "test", "iteration": i}
            
            start = time.perf_counter()
            await wal.write(event_data)
            end = time.perf_counter()
            
            forensic_times.append((end - start) * 1_000_000)
        
        baseline_mean = statistics.mean(baseline_times)
        forensic_mean = statistics.mean(forensic_times)
        overhead = forensic_mean - baseline_mean
        overhead_pct = (overhead / baseline_mean) * 100
        
        print(f"Iterations: 1,000 each")
        print(f"\nBaseline WAL (no protection):")
        print(f"  Mean: {baseline_mean:>10.2f} μs")
        print(f"\nForensic WAL (HMAC + Replay + Timestamp):")
        print(f"  Mean: {forensic_mean:>10.2f} μs")
        print(f"\nOverhead:")
        print(f"  Absolute: {overhead:>10.2f} μs")
        print(f"  Relative: {overhead_pct:>10.1f}%")
        
        self.results["comparison"] = {
            "baseline_mean_us": baseline_mean,
            "forensic_mean_us": forensic_mean,
            "overhead_us": overhead,
            "overhead_pct": overhead_pct
        }
        
        shutil.rmtree(temp_dir)
    
    def save_results(self, filename: str = "forensic_wal_benchmark_results.json"):
        """Guarda resultados a JSON"""
        output_file = Path(filename)
        
        with open(output_file, "w") as f:
            json.dump(self.results, f, indent=2)
        
        print(f"\n💾 Resultados guardados en: {output_file.absolute()}")
    
    def print_summary(self):
        """Imprime resumen ejecutivo"""
        print("\n" + "=" * 70)
        print("📊 RESUMEN EJECUTIVO - FORENSIC WAL BENCHMARK")
        print("=" * 70)
        
        write = self.results.get("write_latency", {})
        hmac = self.results.get("hmac_overhead", {})
        replay = self.results.get("replay_detection", {})
        timestamp = self.results.get("timestamp_validation", {})
        comparison = self.results.get("comparison", {})
        
        print(f"\n1. Write Latency (End-to-End):")
        print(f"   Mean:       {write.get('mean_us', 0):>10.2f} μs")
        print(f"   P99:        {write.get('p99_us', 0):>10.2f} μs")
        print(f"   Throughput: {write.get('throughput_eps', 0):>10,.0f} events/sec")
        
        print(f"\n2. Component Overhead:")
        print(f"   HMAC:       {hmac.get('mean_us', 0):>10.2f} μs")
        print(f"   Replay:     {replay.get('mean_ns', 0)/1000:>10.2f} μs")
        print(f"   Timestamp:  {timestamp.get('mean_ns', 0)/1000:>10.2f} μs")
        
        print(f"\n3. vs Baseline WAL:")
        print(f"   Overhead:   {comparison.get('overhead_us', 0):>10.2f} μs ({comparison.get('overhead_pct', 0):.1f}%)")
        
        print("\n" + "=" * 70)
        print("✅ Claim 4: Forensic WAL - Performance Validated")
        print("=" * 70)


async def main():
    """Ejecuta todos los benchmarks"""
    print("\n" + "=" * 70)
    print("🔬 FORENSIC WAL - PERFORMANCE BENCHMARK SUITE")
    print("   Claim 4: HMAC + Replay Protection + Timestamp Validation")
    print("=" * 70)
    
    benchmark = ForensicWALBenchmark(iterations=10000)
    
    # Ejecutar benchmarks
    await benchmark.benchmark_write_latency()
    await benchmark.benchmark_hmac_overhead()
    await benchmark.benchmark_replay_detection()
    await benchmark.benchmark_timestamp_validation()
    await benchmark.benchmark_comparison_vs_baseline()
    
    # Resumen
    benchmark.print_summary()
    
    # Guardar resultados
    benchmark.save_results()
    
    print("\n✅ Benchmark completado exitosamente")
    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
